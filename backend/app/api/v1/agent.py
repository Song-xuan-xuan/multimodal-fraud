from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.base import get_db
from app.schemas.agent import AgentAnalyzeResponse
from app.services.anti_fraud_agent_service import analyze_multimodal_input

router = APIRouter()


@router.post('/analyze', response_model=AgentAnalyzeResponse)
async def analyze_agent_input(
    text: str = Form(''),
    image: UploadFile | None = File(None),
    audio: UploadFile | None = File(None),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not text.strip() and image is None and audio is None:
        raise HTTPException(status_code=400, detail='至少提供一种输入模态')

    image_bytes = await image.read() if image else None
    audio_bytes = await audio.read() if audio else None

    result = await analyze_multimodal_input(
        db=db,
        user=user,
        text=text,
        image_bytes=image_bytes,
        image_filename=image.filename if image else '',
        audio_bytes=audio_bytes,
        audio_filename=audio.filename if audio else '',
    )
    return AgentAnalyzeResponse(**result)
