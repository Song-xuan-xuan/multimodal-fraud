"""Detection service - bridges FastAPI endpoints to model layer.

All model calls are wrapped in asyncio.to_thread() since the underlying
PyTorch inference is synchronous / CPU-bound.
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path

logger = logging.getLogger(__name__)

# Ensure the repository root is importable so `model` can be resolved.
_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def _coerce_probability(value: object, default: float = 0.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = default
    return max(0.0, min(1.0, numeric))



def _coerce_bool(value: object, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no", ""}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default



def _normalize_ai_text_result(result: Mapping[str, object] | None) -> dict:
    """Normalize AI text detection output for current frontend and legacy clients."""
    payload = dict(result) if isinstance(result, Mapping) else {}
    raw_details = payload.get("details")
    details = dict(raw_details) if isinstance(raw_details, Mapping) else {}

    confidence = _coerce_probability(payload.get("confidence"), 0.0)
    model_probability = _coerce_probability(payload.get("probability"), confidence)
    heuristics = _estimate_fraud_signal_probability(str(payload.get("text") or ""))
    merged_probability = max(model_probability, heuristics["risk_probability"])

    is_ai_generated = _coerce_bool(payload.get("is_ai_generated"), merged_probability > 0.45)
    confidence = merged_probability if confidence in {0.0, 1.0} else max(confidence, merged_probability)
    ai_probability = round(merged_probability, 4)
    human_probability = round(1.0 - merged_probability, 4)

    label = "高风险话术" if is_ai_generated else "低风险文本"
    summary = f"高风险表达概率 {ai_probability * 100:.1f}%，低风险表达概率 {human_probability * 100:.1f}%。"
    conclusion = (
        "文本中存在较强风险话术特征，建议结合上下文、身份声明和资金要求进一步核验。"
        if is_ai_generated
        else "文本整体风险较低，但仍建议结合场景、对象身份和资金要求继续复核。"
    )

    return {
        "is_ai_generated": is_ai_generated,
        "confidence": confidence if "confidence" in payload else merged_probability,
        "probability": merged_probability,
        "label": label,
        "overall_label": label,
        "summary": summary,
        "conclusion": conclusion,
        "details": {
            **details,
            "ai_probability": ai_probability,
            "human_probability": human_probability,
            "model_probability": round(model_probability, 4),
            "rule_probability": round(heuristics["risk_probability"], 4),
            "risk_signal_hits": heuristics["matched_signals"],
            "protective_hits": heuristics["protective_signals"],
        },
    }


def _estimate_fraud_signal_probability(text: str) -> dict[str, object]:
    content = (text or "").strip()
    if not content:
        return {"risk_probability": 0.0, "matched_signals": [], "protective_signals": []}

    fraud_signals = [
        "转账", "汇款", "收款码", "扫码", "二维码", "验证码", "银行卡", "密码",
        "点击链接", "下载", "客服", "退款", "征信", "刷单", "投资", "充值",
        "任务", "担保", "保证金", "紧急", "截止", "限时", "立刻",
    ]
    protective_signals = ["核实", "确认", "回拨", "报警", "谨慎", "不要", "防范", "建议"]

    matched = [token for token in fraud_signals if token in content]
    protective = [token for token in protective_signals if token in content]

    score = 0.02
    if len(matched) >= 1:
        score += 0.18
    if len(matched) >= 3:
        score += 0.22
    if len(matched) >= 5:
        score += 0.2

    if any(token in content for token in ["转账", "汇款", "收款码", "扫码", "二维码"]):
        score += 0.16
    if any(token in content for token in ["验证码", "银行卡", "密码"]):
        score += 0.16
    if any(token in content for token in ["紧急", "截止", "限时", "立刻"]):
        score += 0.12

    score -= min(0.2, len(protective) * 0.05)
    score = max(0.0, min(0.95, score))
    return {"risk_probability": round(score, 4), "matched_signals": matched, "protective_signals": protective}


async def detect_ai_text(text: str) -> dict:
    """AI-generated text detection using Fast-DetectGPT."""
    logger.info("AI text detection requested, text_length=%d", len(text))
    try:
        from model.ai_text.service import detect
        result = await asyncio.to_thread(detect, text)
        payload = dict(result) if isinstance(result, Mapping) else {}
        payload["text"] = text
        return _normalize_ai_text_result(payload)
    except Exception as e:
        logger.error("AI text detection error: %s", e)
        return _normalize_ai_text_result({"is_ai_generated": False, "confidence": 0.0, "details": {"error": str(e)}})


async def detect_ai_image(image_bytes: bytes, filename: str) -> dict:
    """Screenshot risk analysis (fraud-oriented), with AIorNot fallback."""
    logger.info("AI image detection: %s", filename)

    # Primary path: fraud-scene visual analysis
    try:
        from app.services.vision_service import analyze_image_fraud_risk

        visual = await analyze_image_fraud_risk(image_bytes, filename)
        raw_score = visual.get("risk_score", 0.0)
        score = _coerce_probability(raw_score if isinstance(raw_score, (int, float)) and raw_score <= 1 else (float(raw_score) / 100.0 if raw_score else 0.0))
        risk_level = str(visual.get("risk_level") or "").lower()
        fraud_types = visual.get("fraud_types") or []
        matched_signals = visual.get("matched_signals") or []
        ocr_text = str(visual.get("ocr_text") or "")
        scene_type = str(visual.get("scene_type") or "")

        label = scene_type or ("高风险截图" if score >= 0.6 else ("中风险截图" if score >= 0.35 else "低风险截图"))
        is_risky = score >= 0.45
        summary = str(visual.get("summary") or f"截图风险概率 {score * 100:.1f}%，建议结合对话背景继续核验。")
        conclusion = str(visual.get("conclusion") or ("截图命中多个风险信号，建议先核验再操作。" if is_risky else "截图整体风险较低，但仍建议谨慎核验。"))

        return {
            "is_ai_generated": is_risky,
            "confidence": score,
            "probability": score,
            "label": label,
            "overall_label": label,
            "summary": summary,
            "conclusion": conclusion,
            "details": {
                "engine": "vision-fraud",
                "risk_level": risk_level,
                "fraud_types": fraud_types,
                "matched_signals": matched_signals,
                "ocr_text": ocr_text,
            },
        }
    except Exception as vision_exc:
        logger.warning("Visual fraud analysis unavailable, fallback to AIorNot: %s", vision_exc)

    # Fallback path: AI-generated image detection
    try:
        from model.ai_image.service import classify_image

        result = await asyncio.to_thread(classify_image, image_bytes)
        prob = _coerce_probability(result.get("confidence"), 0.0)
        is_ai = bool(result.get("is_ai_generated", False))
        label = str(result.get("label", "unknown"))
        summary = f"诈骗概率 {prob * 100:.1f}%"
        conclusion = "图片疑似 AI 合成，建议结合来源与上下文进一步核验。" if is_ai else "图片更接近真实拍摄，但不代表内容真实性，请继续核验。"
        return {
            "is_ai_generated": is_ai,
            "confidence": prob,
            "probability": prob,
            "label": label,
            "overall_label": label,
            "summary": summary,
            "conclusion": conclusion,
            "details": {"engine": "aiornot"},
        }
    except Exception as e:
        logger.error("AI image detection error: %s", e)
        return {
            "is_ai_generated": False,
            "confidence": 0.0,
            "probability": 0.0,
            "label": "error",
            "overall_label": "error",
            "summary": "截图分析失败，请稍后重试。",
            "conclusion": str(e),
            "details": {"error": str(e)},
        }


async def detect_multimodal(text: str, image_bytes: bytes | None = None) -> dict:
    """Multimodal deepfake detection.

    Currently combines AI text detection + AI image detection.
    HAMMER model integration is reserved for future work.
    """
    logger.info("Multimodal detection")
    text_analysis = {}
    image_analysis = {}

    if text:
        text_analysis = await detect_ai_text(text)
    if image_bytes:
        image_analysis = await detect_ai_image(image_bytes, "multimodal_input")

    # Simple fusion: if either detects AI content, flag as potentially fake
    text_ai = text_analysis.get("is_ai_generated", False)
    image_ai = image_analysis.get("is_ai_generated", False)
    text_conf = text_analysis.get("confidence", 0.0)
    image_conf = image_analysis.get("confidence", 0.0)

    is_fake = text_ai or image_ai
    confidence = max(text_conf, image_conf) if is_fake else min(text_conf, image_conf)

    return {
        "is_fake": is_fake,
        "confidence": confidence,
        "text_analysis": text_analysis,
        "image_analysis": image_analysis,
    }


async def detect_fake_news(title: str, content: str) -> dict:
    """Fake news detection using BERT classifier + feature analysis."""
    logger.info("Fake news detection: %s", title[:50] if title else "")
    try:
        from model.fake_news.service import detect
        result = await asyncio.to_thread(detect, title, content)
        return result
    except Exception as e:
        logger.error("Fake news detection error: %s", e)
        return {
            "label": "未知", "confidence": 0.0, "credibility_score": 0.0,
            "dimensions": {}, "summary": str(e), "conclusion": "检测失败",
        }


async def detect_aggregate(title: str, content: str, url: str = "") -> dict:
    """Aggregate detection: combines fake news + AI text detection."""
    news_result = await detect_fake_news(title, content)
    ai_text_result = await detect_ai_text(content)

    cred_score = news_result.get("credibility_score", 0)
    ai_conf = ai_text_result.get("confidence", 0)
    overall = (cred_score + (10.0 - ai_conf * 10)) / 2

    return {
        "news_detection": news_result,
        "ai_text_detection": ai_text_result,
        "overall_credibility": overall,
        "overall_label": news_result.get("label", "未知"),
    }


async def detect_by_url(url: str) -> dict:
    """Extract news content from URL and run consistency detection."""
    logger.info("URL detection: %s", url)
    try:
        def _extract_and_detect(url: str) -> dict:
            try:
                from newspaper import Article, ArticleException
            except ImportError:
                return {"error": "newspaper3k library not installed"}

            try:
                article = Article(url)
                article.download()
                article.parse()
                article.nlp()
            except Exception as e:
                return {"error": f"Failed to parse URL: {e}"}

            title = article.title or ""
            text = article.text or ""
            images = list(article.images) if article.images else []

            if not text.strip():
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(article.html or "", "html.parser")
                text = soup.get_text(separator="\n").strip()

            if not text.strip():
                return {"error": "Could not extract content from URL"}

            # Title-text consistency
            result: dict = {
                "title": title,
                "content": text[:500],
                "url": url,
            }

            if title and text:
                try:
                    from model.text_similarity.service import compute_similarity
                    sim = compute_similarity(title, text)
                    result["title_txt_similarity"] = sim
                    result["title_txt_match"] = sim >= 0.5
                    result["consistency_result"] = "match" if sim >= 0.5 else "mismatch"
                except Exception as e:
                    logger.warning("Similarity computation failed: %s", e)
                    result["title_txt_similarity"] = 0.0
                    result["title_txt_match"] = True
                    result["consistency_result"] = "unknown"

            result["details"] = {
                "authors": article.authors or [],
                "publish_date": str(article.publish_date) if article.publish_date else "",
                "summary": article.summary or "",
                "keywords": article.keywords or [],
                "image_count": len(images),
            }
            return result

        return await asyncio.to_thread(_extract_and_detect, url)
    except Exception as e:
        logger.error("URL detection error: %s", e)
        return {"error": str(e)}


async def detect_by_file(file_bytes: bytes, filename: str) -> dict:
    """Extract content from uploaded file and run consistency detection."""
    logger.info("File detection: %s", filename)
    try:
        def _extract_and_detect(data: bytes, fname: str) -> dict:
            suffix = Path(fname).suffix.lower()
            title = ""
            text = ""

            if suffix in (".txt", ".text"):
                content = data.decode("utf-8", errors="replace")
                lines = [l.strip() for l in content.split("\n") if l.strip()]
                title = lines[0] if lines else ""
                text = "\n".join(lines[1:]) if len(lines) > 1 else title

            elif suffix in (".json",):
                try:
                    obj = json.loads(data)
                    title = obj.get("title", "")
                    text = obj.get("content", "") or obj.get("text", "")
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON file"}

            elif suffix in (".doc", ".docx"):
                try:
                    import docx
                    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                        tmp.write(data)
                        tmp_path = tmp.name
                    doc = docx.Document(tmp_path)
                    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
                    title = paragraphs[0] if paragraphs else ""
                    text = "\n".join(paragraphs[1:]) if len(paragraphs) > 1 else title
                    os.unlink(tmp_path)
                except ImportError:
                    return {"error": "python-docx library not installed"}

            elif suffix in (".pdf",):
                try:
                    import PyPDF2
                    import io
                    reader = PyPDF2.PdfReader(io.BytesIO(data))
                    full_text = ""
                    for page in reader.pages:
                        full_text += page.extract_text() or ""
                    lines = [l.strip() for l in full_text.split("\n") if l.strip()]
                    title = lines[0] if lines else ""
                    text = "\n".join(lines[1:]) if len(lines) > 1 else title
                except ImportError:
                    return {"error": "PyPDF2 library not installed"}
            else:
                content = data.decode("utf-8", errors="replace")
                lines = [l.strip() for l in content.split("\n") if l.strip()]
                title = lines[0] if lines else ""
                text = "\n".join(lines[1:]) if len(lines) > 1 else title

            if not text.strip():
                return {"error": "Could not extract content from file"}

            result: dict = {
                "title": title,
                "content": text[:500],
            }

            if title and text:
                try:
                    from model.text_similarity.service import compute_similarity
                    sim = compute_similarity(title, text)
                    result["title_txt_similarity"] = sim
                    result["title_txt_match"] = sim >= 0.5
                    result["consistency_result"] = "match" if sim >= 0.5 else "mismatch"
                except Exception as e:
                    logger.warning("Similarity computation failed: %s", e)
                    result["title_txt_similarity"] = 0.0
                    result["title_txt_match"] = True
                    result["consistency_result"] = "unknown"

            result["details"] = {"filename": fname, "file_size": len(data)}
            return result

        return await asyncio.to_thread(_extract_and_detect, file_bytes, filename)
    except Exception as e:
        logger.error("File detection error: %s", e)
        return {"error": str(e)}


async def detect_segments(title: str, content: str, segment_size: int = 500) -> dict:
    """Segment-based fake news detection: split content into segments and detect each."""
    logger.info("Segment detection: title=%s, seg_size=%d", title[:30] if title else "", segment_size)

    # Split content into segments
    segments = []
    for i in range(0, len(content), segment_size):
        seg_text = content[i:i + segment_size]
        if seg_text.strip():
            segments.append(seg_text)

    if not segments:
        return {
            "credibility_score": 0.0,
            "credibility_level": "unknown",
            "segment_count": 0,
            "conclusion": "No content to analyze",
            "segments": [],
            "feature_tags": {},
        }

    segment_results = []
    total_score = 0.0

    for idx, seg_text in enumerate(segments):
        result = await detect_fake_news(title, seg_text)
        score = result.get("credibility_score", 5.0)
        total_score += score
        label = result.get("label", "unknown")
        real_prob = score / 10.0
        fake_prob = 1.0 - real_prob
        segment_results.append({
            "segment_id": idx,
            "text": seg_text[:200],
            "label": label,
            "real_probability": round(real_prob, 4),
            "fake_probability": round(fake_prob, 4),
        })

    avg_score = total_score / len(segments) if segments else 0.0
    if avg_score >= 7:
        level = "high"
        conclusion = "Content is largely credible"
    elif avg_score >= 4:
        level = "medium"
        conclusion = "Content credibility is uncertain"
    else:
        level = "low"
        conclusion = "Content is likely unreliable"

    return {
        "credibility_score": round(avg_score, 2),
        "credibility_level": level,
        "segment_count": len(segments),
        "conclusion": conclusion,
        "segments": segment_results,
        "feature_tags": {
            "title_present": bool(title),
            "total_length": len(content),
            "segment_size": segment_size,
        },
    }

def _convert_to_mono_wav(audio_bytes: bytes, filename: str) -> tuple[bytes, str]:
    """用 ffmpeg 将任意音频转为 16kHz 单声道 WAV，兼容智谱 ASR 要求。"""
    import subprocess

    suffix = Path(filename).suffix.lower() or '.wav'
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_in:
        tmp_in.write(audio_bytes)
        in_path = tmp_in.name

    out_path = in_path + '.mono.wav'
    try:
        cmd = [
            'ffmpeg', '-y', '-i', in_path,
            '-ac', '1',           # 单声道
            '-ar', '16000',       # 16kHz 采样率
            '-sample_fmt', 's16', # 16-bit
            '-f', 'wav', out_path,
        ]
        proc = subprocess.run(cmd, capture_output=True, timeout=30)
        if proc.returncode != 0:
            stderr = proc.stderr.decode('utf-8', errors='replace')[:500]
            logger.error('ffmpeg 转码失败: %s', stderr)
            raise RuntimeError(f'音频转码失败: {stderr}')
        mono_bytes = Path(out_path).read_bytes()
        logger.info('音频转码完成: %d bytes -> %d bytes (mono wav)', len(audio_bytes), len(mono_bytes))
        return mono_bytes, Path(filename).stem + '.wav'
    finally:
        for p in (in_path, out_path):
            try:
                os.unlink(p)
            except OSError:
                pass


async def _transcribe_audio_via_zhipu(audio_bytes: bytes, filename: str, content_type: str | None = None) -> str:
    import httpx
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.ZHIPU_AUDIO_API_KEY:
        raise RuntimeError('未配置语音转写 API 密钥')

    # 先转为单声道 WAV（智谱 ASR 要求单声道）
    try:
        audio_bytes, filename = await asyncio.to_thread(_convert_to_mono_wav, audio_bytes, filename)
        content_type = 'audio/wav'
    except Exception as e:
        logger.error('音频预处理失败: %s', e)
        raise RuntimeError(f'音频预处理失败: {e}') from e

    api_url = f"{settings.ZHIPU_AUDIO_BASE_URL.rstrip('/')}/audio/transcriptions"
    headers = {
        'Authorization': f'Bearer {settings.ZHIPU_AUDIO_API_KEY}',
    }

    files = {
        'file': (filename or 'audio.wav', audio_bytes, content_type),
    }
    data = {
        'model': settings.ZHIPU_AUDIO_MODEL,
    }

    logger.info(
        '智谱 ASR 请求: url=%s, model=%s, filename=%s, content_type=%s, size=%d bytes',
        api_url, settings.ZHIPU_AUDIO_MODEL, filename, content_type, len(audio_bytes),
    )

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=10.0)) as client:
            response = await client.post(api_url, headers=headers, data=data, files=files)
    except httpx.TimeoutException as exc:
        logger.error('智谱 ASR 请求超时: %s', exc)
        raise RuntimeError('语音转写请求超时，请稍后重试') from exc
    except httpx.RequestError as exc:
        logger.error('智谱 ASR 网络错误: %s', exc)
        raise RuntimeError(f'语音转写网络错误: {exc}') from exc

    logger.info('智谱 ASR 响应: status=%d, content_type=%s', response.status_code, response.headers.get('content-type', ''))

    if response.status_code != 200:
        logger.error('智谱 ASR 非 200 响应: status=%d, body=%s', response.status_code, response.text[:500])
        raise RuntimeError(f'语音转写服务返回错误 (HTTP {response.status_code}): {response.text[:200]}')

    # 解析 JSON 响应
    try:
        payload = response.json()
    except Exception:
        logger.error('智谱 ASR 响应非 JSON: %s', response.text[:500])
        raise RuntimeError('语音转写服务返回了非 JSON 格式的响应')

    logger.debug('智谱 ASR 响应体: %s', json.dumps(payload, ensure_ascii=False)[:500])

    # 检查 API 层面的错误
    if 'error' in payload:
        err_msg = payload['error'] if isinstance(payload['error'], str) else payload['error'].get('message', str(payload['error']))
        logger.error('智谱 ASR API 错误: %s', err_msg)
        raise RuntimeError(f'语音转写 API 错误: {err_msg}')

    transcript = payload.get('text') or payload.get('transcript') or ''
    if not transcript:
        logger.error('智谱 ASR 未返回文本, 完整响应: %s', json.dumps(payload, ensure_ascii=False)[:500])
        raise RuntimeError('语音转写接口未返回有效文本')
    return transcript


async def detect_audio_risk(audio_bytes: bytes, filename: str, content_type: str | None = None) -> dict:
    logger.info('Audio risk detection: %s', filename)
    try:
        transcript = await _transcribe_audio_via_zhipu(audio_bytes, filename, content_type)
        text_result = await detect_ai_text(transcript)
        result = dict(text_result)
        result['transcript'] = transcript
        result['summary'] = f"语音转写完成。{result.get('summary', '')}".strip()
        result['conclusion'] = result.get('conclusion') or '语音已转写并完成风险分析。'
        details = dict(result.get('details') or {})
        details['input_modality'] = 'audio'
        details['filename'] = filename
        result['details'] = details
        return result
    except Exception as e:
        logger.error('Audio risk detection error: %s', e)
        return {
            'is_ai_generated': False,
            'confidence': 0.0,
            'probability': 0.0,
            'label': '待复核',
            'overall_label': '待复核',
            'summary': '语音分析失败，请检查转写服务配置后重试。',
            'conclusion': str(e),
            'transcript': '',
            'details': {'error': str(e), 'input_modality': 'audio', 'filename': filename},
        }
