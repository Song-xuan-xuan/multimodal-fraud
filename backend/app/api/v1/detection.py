import logging

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.detection import (
    DetectTextRequest, DetectAITextResponse, DetectAIImageResponse, DetectAIAudioResponse,
    DetectMultimodalResponse, DetectNewsResponse,
    DetectAggregateRequest, DetectAggregateResponse,
    DetectUrlRequest, DetectUrlResponse, DetectFileResponse,
    DetectSegmentRequest, DetectSegmentResponse,
)
from app.services.detection_service import (
    detect_ai_text, detect_ai_image, detect_audio_risk, detect_multimodal,
    detect_fake_news, detect_aggregate,
    detect_by_url, detect_by_file, detect_segments,
)
from app.core.deps import get_current_user
from app.db.base import get_db
from app.services.profile_service import record_detection

logger = logging.getLogger(__name__)
router = APIRouter()


def _infer_risk(result: dict) -> str | None:
    """Infer risk level from detection result."""
    conf = result.get("confidence", 0)
    if result.get("is_ai_generated") or result.get("is_fake"):
        return "high" if conf >= 0.7 else "medium"
    label = result.get("label", "").lower()
    if "fake" in label or "虚假" in label:
        return "high" if conf >= 0.7 else "medium"
    return "low"


@router.post('/ai-text', response_model=DetectAITextResponse)
async def detect_ai_text_api(
    req: DetectTextRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await detect_ai_text(req.text)
    await record_detection(db, user.id, "ai-text", _infer_risk(result))
    return DetectAITextResponse(**result)


@router.post('/ai-image', response_model=DetectAIImageResponse)
async def detect_ai_image_api(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    contents = await file.read()
    result = await detect_ai_image(contents, file.filename or '')
    await record_detection(db, user.id, "ai-image", _infer_risk(result))
    return DetectAIImageResponse(**result)


@router.post('/audio-risk', response_model=DetectAIAudioResponse)
async def detect_audio_risk_api(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info('[audio-risk] 收到请求: filename=%s, content_type=%s', file.filename, file.content_type)
    try:
        contents = await file.read()
    except Exception as e:
        logger.exception('[audio-risk] 文件读取失败')
        return DetectAIAudioResponse(
            summary='文件读取失败', conclusion=str(e),
            details={'error': str(e), 'input_modality': 'audio'},
        )
    try:
        result = await detect_audio_risk(contents, file.filename or '', file.content_type)
    except Exception as e:
        logger.exception('[audio-risk] detect_audio_risk 异常')
        return DetectAIAudioResponse(
            summary='语音分析异常', conclusion=str(e),
            details={'error': str(e), 'input_modality': 'audio'},
        )
    try:
        resp = DetectAIAudioResponse(**result)
        await record_detection(db, user.id, "audio-risk", _infer_risk(result))
        return resp
    except Exception as e:
        logger.exception('[audio-risk] 响应序列化失败, result=%s', result)
        return DetectAIAudioResponse(
            summary='响应构造失败', conclusion=str(e),
            details={'error': str(e), 'raw_keys': list(result.keys())},
        )


@router.post('/multimodal', response_model=DetectMultimodalResponse)
async def detect_multimodal_api(
    text: str = Form(''),
    file: UploadFile | None = File(None),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    image_bytes = await file.read() if file else None
    result = await detect_multimodal(text, image_bytes)
    await record_detection(db, user.id, "multimodal", _infer_risk(result))
    return DetectMultimodalResponse(**result)


@router.post('/news', response_model=DetectNewsResponse)
async def detect_news_api(
    req: DetectAggregateRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await detect_fake_news(req.title, req.content)
    await record_detection(db, user.id, "news", _infer_risk(result))
    return DetectNewsResponse(**result)


@router.post('/aggregate', response_model=DetectAggregateResponse)
async def detect_aggregate_api(
    req: DetectAggregateRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await detect_aggregate(req.title, req.content, req.url)
    await record_detection(db, user.id, "aggregate", _infer_risk(result))
    return DetectAggregateResponse(**result)


@router.post('/url', response_model=DetectUrlResponse)
async def detect_url_api(
    req: DetectUrlRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await detect_by_url(req.url)
    if 'error' in result:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=result['error'])
    await record_detection(db, user.id, "url", _infer_risk(result))
    return DetectUrlResponse(**result)


@router.post('/file', response_model=DetectFileResponse)
async def detect_file_api(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    contents = await file.read()
    result = await detect_by_file(contents, file.filename or 'upload.txt')
    if 'error' in result:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=result['error'])
    await record_detection(db, user.id, "file", _infer_risk(result))
    return DetectFileResponse(**result)


@router.post('/segments', response_model=DetectSegmentResponse)
async def detect_segments_api(
    req: DetectSegmentRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await detect_segments(req.title, req.content, req.segment_size)
    await record_detection(db, user.id, "segments", _infer_risk(result))
    return DetectSegmentResponse(**result)


@router.post('/audio-risk-debug')
async def audio_risk_debug(file: UploadFile = File(...), user=Depends(get_current_user)):
    """诊断端点：不调用智谱 API，仅测试文件上传 + 响应链路。"""
    try:
        contents = await file.read()
    except Exception as e:
        return {'step': 'file_read', 'error': str(e)}

    info = {
        'step': 'all_ok',
        'filename': file.filename,
        'content_type': file.content_type,
        'size_bytes': len(contents),
        'first_4_bytes': contents[:4].hex() if contents else '',
    }

    try:
        import httpx  # noqa: F401
        info['httpx_available'] = True
    except ImportError as e:
        info['httpx_available'] = False
        info['httpx_error'] = str(e)

    try:
        from app.core.config import get_settings
        s = get_settings()
        info['zhipu_api_key_set'] = bool(s.ZHIPU_AUDIO_API_KEY)
        info['zhipu_base_url'] = s.ZHIPU_AUDIO_BASE_URL
        info['zhipu_model'] = s.ZHIPU_AUDIO_MODEL
    except Exception as e:
        info['config_error'] = str(e)

    return info
