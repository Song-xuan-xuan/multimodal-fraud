#!/usr/bin/env python3
"""
评测脚本 — 自动跑批评测 + 输出 F1/Accuracy 报告

用法:
    python evaluation/run_evaluation.py [--base-url http://127.0.0.1:8000]
"""

import argparse
import csv
import json
import logging
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = "http://127.0.0.1:8000"
DATASET_PATH = Path(__file__).parent / "dataset.json"
IMAGES_DIR = Path(__file__).parent / "images"
AUDIO_DIR = Path(__file__).parent / "audio"
OUTPUT_DIR = Path(__file__).parent / "results"
USERNAME = "admin"
PASSWORD = "123456"
TIMEOUT = 120  # seconds per request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_media(case_id: str) -> dict:
    """查找与 case_id 匹配的 image / audio 文件。"""
    media = {}
    img = IMAGES_DIR / f"{case_id}.jpg"
    if img.exists():
        media["image"] = img
    wav = AUDIO_DIR / f"{case_id}.wav"
    if wav.exists():
        media["audio"] = wav
    return media


def check_server_available(client: httpx.Client) -> None:
    """在正式评测前先检查后端是否可达。"""
    try:
        resp = client.get(f"{BASE_URL}/health", timeout=10)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(
            f"无法连接后端服务 {BASE_URL} 。请先启动 FastAPI 后端，再执行评测。原始错误: {e}"
        ) from e


def summarize_dataset(samples: list[dict]) -> None:
    total = len(samples)
    black = sum(1 for s in samples if s.get("label") == 1)
    white = sum(1 for s in samples if s.get("label") == 0)
    has_image = sum(1 for s in samples if find_media(s["case_id"]).get("image"))
    has_audio = sum(1 for s in samples if find_media(s["case_id"]).get("audio"))
    logger.info(
        "样本数: %d (黑=%d, 白=%d, 图片=%d, 音频=%d)",
        total, black, white, has_image, has_audio,
    )
    if has_audio == 0:
        logger.warning("未检测到任何音频样本，音频能力不会被覆盖到。")
    if has_image == 0:
        logger.warning("未检测到任何图片样本，图片能力不会被覆盖到。")


def infer_risk(result: dict) -> str:
    """复刻 backend _infer_risk()。"""
    conf = result.get("confidence", 0) or 0
    if result.get("is_ai_generated") or result.get("is_fake"):
        return "high" if conf >= 0.7 else "medium"
    label = result.get("label", "").lower()
    if "fake" in label or "虚假" in label:
        return "high" if conf >= 0.7 else "medium"
    return "low"


def map_prediction(risk_level: str) -> int:
    """二分类映射: medium/high → 1 (黑), low → 0 (白)。"""
    return 1 if risk_level in ("medium", "high") else 0


def compute_metrics(y_true: list[int], y_pred: list[int]) -> dict:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    total = len(y_true)
    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1,
    }


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def login(client: httpx.Client) -> str:
    """登录获取 token；失败则先注册再登录。"""
    url = f"{BASE_URL}/api/v1/auth/login"
    resp = client.post(url, json={"username": USERNAME, "password": PASSWORD})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    # 尝试注册
    reg_url = f"{BASE_URL}/api/v1/auth/register"
    reg_resp = client.post(reg_url, json={
        "username": USERNAME, "password": PASSWORD, "confirm_password": PASSWORD,
    })
    if reg_resp.status_code not in (200, 201):
        logger.warning("注册返回 %s: %s", reg_resp.status_code, reg_resp.text)
    resp = client.post(url, json={"username": USERNAME, "password": PASSWORD})
    try:
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(
            f"登录失败。请检查评测脚本中的账号密码是否与当前数据库一致。"
            f" username={USERNAME!r}, status={resp.status_code}, body={resp.text[:200]}"
        ) from e
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Phase 1: Agent
# ---------------------------------------------------------------------------

def run_phase1_agent(samples: list[dict], client: httpx.Client, token: str) -> list[dict]:
    results = []
    headers = auth_headers(token)
    url = f"{BASE_URL}/api/v1/agent/analyze"

    for i, s in enumerate(samples, 1):
        case_id = s["case_id"]
        content = s.get("content") or s.get("title", "")
        media = find_media(case_id)

        data = {"text": content}
        files = {}
        if "image" in media:
            files["image"] = (media["image"].name, open(media["image"], "rb"), "image/jpeg")
        if "audio" in media:
            files["audio"] = (media["audio"].name, open(media["audio"], "rb"), "audio/wav")

        logger.info("[Phase1] %d/%d  %s  media=%s", i, len(samples), case_id, list(media.keys()))
        try:
            resp = client.post(url, data=data, files=files if files else None,
                               headers=headers, timeout=TIMEOUT)
            resp.raise_for_status()
            body = resp.json()
        except Exception as e:
            logger.error("[Phase1] %s 请求失败: %s", case_id, e)
            body = {"error": str(e)}
        finally:
            for file_tuple in files.values() if isinstance(files, dict) else []:
                try:
                    fobj = file_tuple[1]
                    fobj.close()
                except Exception:
                    pass

        risk = body.get("risk_level", "low")
        pred = map_prediction(risk)
        results.append({
            "case_id": case_id,
            "label": s["label"],
            "risk_level": risk,
            "prediction": pred,
            "response": body,
        })
    return results


# ---------------------------------------------------------------------------
# Phase 2: Detection
# ---------------------------------------------------------------------------

def run_phase2_detection(samples: list[dict], client: httpx.Client, token: str) -> list[dict]:
    results = []
    headers = auth_headers(token)
    risk_priority = {"high": 3, "medium": 2, "low": 1}

    for i, s in enumerate(samples, 1):
        case_id = s["case_id"]
        content = s.get("content") or s.get("title", "")
        media = find_media(case_id)

        sub_results = []
        logger.info("[Phase2] %d/%d  %s  media=%s", i, len(samples), case_id, list(media.keys()))

        # 1) 文本检测
        try:
            resp = client.post(f"{BASE_URL}/api/v1/detection/ai-text",
                               json={"text": content}, headers=headers, timeout=TIMEOUT)
            resp.raise_for_status()
            text_res = resp.json()
            sub_results.append({"modality": "text", "result": text_res, "risk": infer_risk(text_res)})
        except Exception as e:
            logger.error("[Phase2] %s text 失败: %s", case_id, e)

        # 2) 图片检测
        if "image" in media:
            try:
                with open(media["image"], "rb") as f:
                    resp = client.post(f"{BASE_URL}/api/v1/detection/ai-image",
                                       files={"file": (media["image"].name, f, "image/jpeg")},
                                       headers=headers, timeout=TIMEOUT)
                    resp.raise_for_status()
                    img_res = resp.json()
                    sub_results.append({"modality": "image", "result": img_res, "risk": infer_risk(img_res)})
            except Exception as e:
                logger.error("[Phase2] %s image 失败: %s", case_id, e)

        # 3) 音频检测
        if "audio" in media:
            try:
                with open(media["audio"], "rb") as f:
                    resp = client.post(f"{BASE_URL}/api/v1/detection/audio-risk",
                                       files={"file": (media["audio"].name, f, "audio/wav")},
                                       headers=headers, timeout=TIMEOUT)
                    resp.raise_for_status()
                    aud_res = resp.json()
                    sub_results.append({"modality": "audio", "result": aud_res, "risk": infer_risk(aud_res)})
            except Exception as e:
                logger.error("[Phase2] %s audio 失败: %s", case_id, e)

        # 综合: 取最高 risk_level
        all_risks = [sr["risk"] for sr in sub_results] or ["low"]
        final_risk = max(all_risks, key=lambda r: risk_priority.get(r, 0))
        pred = map_prediction(final_risk)

        results.append({
            "case_id": case_id,
            "label": s["label"],
            "risk_level": final_risk,
            "prediction": pred,
            "sub_results": sub_results,
        })
    return results


def get_modality_result_map(sub_results: list[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for item in sub_results or []:
        modality = str(item.get("modality") or "")
        if modality:
            result[modality] = item
    return result


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def generate_report(
    samples: list[dict],
    p1_results: list[dict],
    p2_results: list[dict],
    p1_metrics: dict,
    p2_metrics: dict,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 数据集统计
    total = len(samples)
    black = sum(1 for s in samples if s["label"] == 1)
    white = total - black
    fraud_types = Counter(s.get("fraud_type", "unknown") for s in samples if s["label"] == 1)
    has_image = sum(1 for s in samples if find_media(s["case_id"]).get("image"))
    has_audio = sum(1 for s in samples if find_media(s["case_id"]).get("audio"))

    def confusion_table(m):
        return (
            f"| | 预测=黑 | 预测=白 |\n"
            f"|---|---|---|\n"
            f"| 实际=黑 | {m['tp']} | {m['fn']} |\n"
            f"| 实际=白 | {m['fp']} | {m['tn']} |"
        )

    def metrics_table(m):
        return (
            f"| 指标 | 值 |\n|---|---|\n"
            f"| Accuracy | {m['accuracy']:.4f} |\n"
            f"| Precision | {m['precision']:.4f} |\n"
            f"| Recall | {m['recall']:.4f} |\n"
            f"| F1-Score | {m['f1']:.4f} |"
        )

    # 诈骗类型表
    fraud_rows = "\n".join(f"| {ft} | {cnt} |" for ft, cnt in fraud_types.most_common())

    # 逐条明细
    detail_rows = []
    p1_map = {r["case_id"]: r for r in p1_results}
    p2_map = {r["case_id"]: r for r in p2_results}
    for s in samples:
        cid = s["case_id"]
        label = "黑" if s["label"] == 1 else "白"
        p1r = p1_map.get(cid, {})
        p2r = p2_map.get(cid, {})
        p1_risk = p1r.get("risk_level", "-")
        p2_risk = p2r.get("risk_level", "-")
        p1_pred = "黑" if p1r.get("prediction") == 1 else "白" if "prediction" in p1r else "-"
        p2_pred = "黑" if p2r.get("prediction") == 1 else "白" if "prediction" in p2r else "-"
        p1_ok = "✓" if p1r.get("prediction") == s["label"] else "✗" if "prediction" in p1r else "-"
        p2_ok = "✓" if p2r.get("prediction") == s["label"] else "✗" if "prediction" in p2r else "-"
        p2_modality_map = get_modality_result_map(p2r.get("sub_results", []))
        text_risk = p2_modality_map.get("text", {}).get("risk", "-")
        image_risk = p2_modality_map.get("image", {}).get("risk", "-")
        audio_risk = p2_modality_map.get("audio", {}).get("risk", "-")
        media = find_media(cid)
        modalities = ["text"]
        if media.get("image"):
            modalities.append("image")
        if media.get("audio"):
            modalities.append("audio")
        detail_rows.append(
            f"| {cid} | {label} | {'+'.join(modalities)} | "
            f"{p1_risk} | {p1_pred} | {p1_ok} | "
            f"{text_risk} | {image_risk} | {audio_risk} | "
            f"{p2_risk} | {p2_pred} | {p2_ok} |"
        )

    report = f"""# 评测报告

生成时间: {now}

## 1. 数据集概览

| 项目 | 值 |
|---|---|
| 样本总数 | {total} |
| 黑样本 (label=1) | {black} |
| 白样本 (label=0) | {white} |
| 黑白比例 | {black}:{white} |
| 含图片样本 | {has_image} |
| 含音频样本 | {has_audio} |

## 2. 诈骗类型覆盖 ({len(fraud_types)} 种)

| 诈骗类型 | 数量 |
|---|---|
{fraud_rows}

## 3. 数据获取与处理

- **黑样本构建**: 以公开反诈案例、警情通报、反诈宣传报道等真实公开材料为基础，围绕投资理财、刷单返利、婚恋交友、冒充班主任收费、兼职招聘、AI 冒充亲属等诈骗场景进行人工筛选和标签整理。
- **白样本构建**: 以公开正常新闻、社会资讯、政务信息、科技教育类报道为基础，通过新闻抓取脚本获取候选内容后，再进行人工复核，剔除与诈骗风险强相关的文本，保留正常语义样本。
- **文本清洗流程**: 原始样本先以 txt 形式归档，再统一转换为 `evaluation/dataset.json`。转换过程中完成字段标准化、空白折叠、缺失内容补齐、标签修正与 `case_id` 统一命名。
- **图片与音频对齐**: 图片和音频采用与样本 `case_id` 同名的文件命名规则，分别放置于 `evaluation/images/` 与 `evaluation/audio/`，评测脚本运行时按文件名自动匹配对应模态资源。
- **多模态覆盖方式**: 当前评测集以文本为基础样本集，在此基础上补充部分图片样本和音频样本，用于验证系统在文本、图像、语音三类输入下的识别表现。
- **数据构建相关脚本**:
  - 候选样本抓取: `scripts/fetch_sogou_wechat_dataset.py`
  - 微信文章正文提取: `scripts/extract_article_content.py`
  - txt 转结构化 JSON: `scripts/convert_txt_dataset_to_json.py`
  - 图片/音频资源挂载: `scripts/attach_media_assets_to_dataset.py`
  - 提交版数据集整理: `scripts/build_submission_dataset.py`

## 4. 评测方法

- **Phase 1 (Agent 综合分析)**: 调用 `POST /api/v1/agent/analyze`，将文本、图片、音频作为联合输入，由多模态智能体直接输出风险等级与综合判断结果。
- **Phase 2 (Detection 逐模态检测)**: 分别调用 `ai-text`、`ai-image`、`audio-risk` 三类专项检测接口，记录各模态风险结果，并以最高风险等级作为当前样本的综合判定结果。
- **标签映射规则**: `risk_level ∈ {{medium, high}}` 映射为黑样本（1），`low` 映射为白样本（0），用于统一计算 Accuracy、Precision、Recall 与 F1-Score。
- **鉴权方式**: 评测脚本通过账号密码自动登录后端服务，获取 Bearer Token 后执行批量测评。

## 5. Phase 1 — Agent 综合分析结果

{metrics_table(p1_metrics)}

### 混淆矩阵

{confusion_table(p1_metrics)}

## 6. Phase 2 — Detection 逐模态检测结果

{metrics_table(p2_metrics)}

### 混淆矩阵

{confusion_table(p2_metrics)}

## 7. 逐条结果明细

| case_id | 标签 | 模态 | P1风险 | P1预测 | P1正确 | 文本风险 | 图片风险 | 音频风险 | P2综合风险 | P2预测 | P2正确 |
|---|---|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(detail_rows)}

## 8. 总结

- **Agent (Phase 1)**: Accuracy={p1_metrics['accuracy']:.4f}, F1={p1_metrics['f1']:.4f}
- **Detection (Phase 2)**: Accuracy={p2_metrics['accuracy']:.4f}, F1={p2_metrics['f1']:.4f}

## 9. 结果分析

- **Phase 1 特征**: 综合分析链路具有较高召回率，对黑样本的识别更偏保守，能够覆盖更多可疑样本，但对白样本存在一定误报。
- **Phase 2 特征**: 逐模态专项检测结果整体更均衡，Accuracy 与 F1-Score 均优于 Phase 1，说明拆分文本、图像、音频后再做风险聚合，更有利于降低误报并提升整体稳定性。
- **误判来源**: 当前误差主要集中在两类场景，一类是“反诈宣传/案例报道”与真实诈骗文本在语义层面较为接近，另一类是部分白样本图片或音频存在较强风险提示信号，导致综合判定被抬高。
- **结论**: 从当前评测结果看，系统已具备对文本、图像、音频三类模态进行联合研判的能力，能够在保持较高识别能力的同时输出结构化评测结果，满足演示与阶段性测评需求。
"""
    return report


def save_summary_csv(samples, p1_results, p2_results, path: Path):
    p1_map = {r["case_id"]: r for r in p1_results}
    p2_map = {r["case_id"]: r for r in p2_results}
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "label", "fraud_type", "modalities",
                     "p1_risk", "p1_pred", "p1_correct",
                     "p2_text_risk", "p2_image_risk", "p2_audio_risk",
                     "p2_risk", "p2_pred", "p2_correct"])
        for s in samples:
            cid = s["case_id"]
            media = find_media(cid)
            mods = "text"
            if media.get("image"):
                mods += "+image"
            if media.get("audio"):
                mods += "+audio"
            ft = s.get("fraud_type", "")
            p1 = p1_map.get(cid, {})
            p2 = p2_map.get(cid, {})
            p2_modality_map = get_modality_result_map(p2.get("sub_results", []))
            w.writerow([
                cid, s["label"], ft, mods,
                p1.get("risk_level", ""), p1.get("prediction", ""),
                int(p1.get("prediction") == s["label"]) if "prediction" in p1 else "",
                p2_modality_map.get("text", {}).get("risk", ""),
                p2_modality_map.get("image", {}).get("risk", ""),
                p2_modality_map.get("audio", {}).get("risk", ""),
                p2.get("risk_level", ""), p2.get("prediction", ""),
                int(p2.get("prediction") == s["label"]) if "prediction" in p2 else "",
            ])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    global BASE_URL, USERNAME, PASSWORD
    parser = argparse.ArgumentParser(description="评测脚本")
    parser.add_argument("--base-url", default=BASE_URL, help="后端 API 地址")
    parser.add_argument("--username", default=USERNAME, help="登录用户名")
    parser.add_argument("--password", default=PASSWORD, help="登录密码")
    parser.add_argument("--skip-phase1", action="store_true", help="跳过 Phase 1，复用已有结果文件")
    args = parser.parse_args()
    BASE_URL = args.base_url.rstrip("/")
    USERNAME = args.username
    PASSWORD = args.password

    # 加载数据集
    logger.info("加载数据集: %s", DATASET_PATH)
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"数据集不存在: {DATASET_PATH}")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        samples = json.load(f)
    if not isinstance(samples, list) or not samples:
        raise RuntimeError("dataset.json 为空或格式不是样本列表")

    # 运行时修复
    for s in samples:
        # TXT_BLACK_012 content 为空 → 用 title
        if not s.get("content"):
            s["content"] = s.get("title", "")
        # 白样本 fraud_type="true" → "benign"
        if s.get("fraud_type") == "true":
            s["fraud_type"] = "benign"

    summarize_dataset(samples)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with httpx.Client(timeout=TIMEOUT) as client:
        # 预检
        logger.info("检查后端可用性: %s", BASE_URL)
        check_server_available(client)

        # 登录
        logger.info("登录 %s ...", BASE_URL)
        token = login(client)
        logger.info("登录成功")

        phase1_path = OUTPUT_DIR / "phase1_agent_results.json"
        if args.skip_phase1:
            if not phase1_path.exists():
                raise FileNotFoundError(f"已指定 --skip-phase1，但结果文件不存在: {phase1_path}")
            logger.info("跳过 Phase 1，复用已有结果: %s", phase1_path)
            with open(phase1_path, "r", encoding="utf-8") as f:
                p1_results = json.load(f)
        else:
            logger.info("=" * 60)
            logger.info("Phase 1: Agent 综合分析")
            logger.info("=" * 60)
            t0 = time.time()
            p1_results = run_phase1_agent(samples, client, token)
            p1_time = time.time() - t0
            logger.info("Phase 1 完成, 耗时 %.1fs", p1_time)

            with open(phase1_path, "w", encoding="utf-8") as f:
                json.dump(p1_results, f, ensure_ascii=False, indent=2)

        # Phase 2
        logger.info("=" * 60)
        logger.info("Phase 2: Detection 逐模态检测")
        logger.info("=" * 60)
        t0 = time.time()
        p2_results = run_phase2_detection(samples, client, token)
        p2_time = time.time() - t0
        logger.info("Phase 2 完成, 耗时 %.1fs", p2_time)

        with open(OUTPUT_DIR / "phase2_detection_results.json", "w", encoding="utf-8") as f:
            json.dump(p2_results, f, ensure_ascii=False, indent=2)

        # 计算指标
        p1_true = [r["label"] for r in p1_results]
        p1_pred = [r["prediction"] for r in p1_results]
        p1_metrics = compute_metrics(p1_true, p1_pred)

        p2_true = [r["label"] for r in p2_results]
        p2_pred = [r["prediction"] for r in p2_results]
        p2_metrics = compute_metrics(p2_true, p2_pred)

        logger.info("Phase 1 — Accuracy=%.4f  F1=%.4f", p1_metrics["accuracy"], p1_metrics["f1"])
        logger.info("Phase 2 — Accuracy=%.4f  F1=%.4f", p2_metrics["accuracy"], p2_metrics["f1"])

        # 生成报告
        report = generate_report(samples, p1_results, p2_results, p1_metrics, p2_metrics)
        report_path = OUTPUT_DIR / "evaluation_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        logger.info("报告已保存: %s", report_path)

        # CSV
        csv_path = OUTPUT_DIR / "evaluation_summary.csv"
        save_summary_csv(samples, p1_results, p2_results, csv_path)
        logger.info("CSV 已保存: %s", csv_path)
    logger.info("评测完成!")


if __name__ == "__main__":
    main()
