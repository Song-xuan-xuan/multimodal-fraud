from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.base import get_db
from app.schemas.alert import (
    AlertCreateRequest,
    AlertCreateResponse,
    AlertListResponse,
    AlertReviewRequest,
    AlertReviewResponse,
)
from app.services.alert_service import create_alert, list_my_alerts, review_alert, serialize_alert_item
from app.ws.socketio_server import push_alert_created_event, push_review_updated_event

router = APIRouter()


@router.post("", response_model=AlertCreateResponse)
async def create_alert_api(
    req: AlertCreateRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recipient_username = req.recipient_username.strip() if req.recipient_username else user.username
    item, event = await create_alert(
        db,
        alert_type=req.alert_type,
        title=req.title,
        message=req.message,
        recipient_username=recipient_username,
        created_by=user.username,
        metadata=req.metadata,
    )
    await push_alert_created_event(event)
    return AlertCreateResponse(message="警报创建成功", item=serialize_alert_item(item), event=event)


@router.post("/{alert_id}/review", response_model=AlertReviewResponse)
async def review_alert_api(
    alert_id: str,
    req: AlertReviewRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item, event = await review_alert(
        db,
        alert_id=alert_id,
        target_status=req.status,
        reviewer_username=user.username,
        feedback=req.feedback,
    )
    await push_review_updated_event(event)
    return AlertReviewResponse(message="警报审核成功", item=serialize_alert_item(item), event=event)


@router.get("/my", response_model=AlertListResponse)
async def list_my_alerts_api(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    status: str | None = Query(default=None),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await list_my_alerts(
        db,
        user.username,
        page=page,
        page_size=page_size,
        status=status,
    )
    return AlertListResponse(**result)
