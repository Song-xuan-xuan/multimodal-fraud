import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.alert import Alert
from app.schemas.alert import AlertEventPayload

PENDING_STATUS = "pending"
APPROVED_STATUS = "approved"
REJECTED_STATUS = "rejected"
ALLOWED_REVIEW_TARGETS = {APPROVED_STATUS, REJECTED_STATUS}


def serialize_alert_item(item: Alert) -> dict:
    return {
        "alert_id": item.alert_id,
        "alert_type": item.alert_type,
        "title": item.title,
        "message": item.message,
        "recipient_username": item.recipient_username,
        "created_by": item.created_by,
        "metadata": json.loads(item.metadata_json or "{}"),
        "status": item.status,
        "review_feedback": item.review_feedback or "",
        "reviewed_by": item.reviewed_by or "",
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else "",
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }


def _build_event_payload(*, event: str, item: Alert, triggered_by: str) -> dict:
    payload = AlertEventPayload(
        event=event,
        occurred_at=datetime.now(timezone.utc).isoformat(),
        recipient_username=item.recipient_username,
        triggered_by=triggered_by,
        alert=serialize_alert_item(item),
    )
    return payload.model_dump()


async def create_alert(
    db: AsyncSession,
    *,
    alert_type: str,
    title: str,
    message: str,
    recipient_username: str,
    created_by: str,
    metadata: dict,
) -> tuple[Alert, dict]:
    now = datetime.now(timezone.utc)
    item = Alert(
        alert_id=f"alt_{uuid4().hex[:12]}",
        alert_type=alert_type.strip(),
        title=title.strip(),
        message=message.strip(),
        recipient_username=recipient_username.strip(),
        created_by=created_by.strip(),
        metadata_json=json.dumps(metadata or {}, ensure_ascii=False),
        status=PENDING_STATUS,
        created_at=now,
        updated_at=now,
    )
    db.add(item)
    await db.flush()
    return item, _build_event_payload(event="alert_created", item=item, triggered_by=created_by)


async def review_alert(
    db: AsyncSession,
    *,
    alert_id: str,
    target_status: str,
    reviewer_username: str,
    feedback: str | None,
) -> tuple[Alert, dict]:
    if target_status not in ALLOWED_REVIEW_TARGETS:
        raise HTTPException(status_code=400, detail="非法审核状态，仅支持 approved/rejected")

    result = await db.execute(select(Alert).where(Alert.alert_id == alert_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="警报不存在")

    if item.status != PENDING_STATUS:
        raise HTTPException(
            status_code=409,
            detail=f"当前状态为 {item.status}，仅 pending 状态可审核",
        )

    now = datetime.now(timezone.utc)
    item.status = target_status
    item.review_feedback = feedback.strip() if feedback and feedback.strip() else None
    item.reviewed_by = reviewer_username
    item.reviewed_at = now
    item.updated_at = now
    await db.flush()

    return item, _build_event_payload(event="review_updated", item=item, triggered_by=reviewer_username)


async def list_my_alerts(
    db: AsyncSession,
    username: str,
    *,
    page: int,
    page_size: int,
    status: str | None,
) -> dict:
    base_query = select(Alert).where(Alert.recipient_username == username)
    if status:
        base_query = base_query.where(Alert.status == status)

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    effective_page = min(page, total_pages) if total_pages > 0 else 1

    offset = (effective_page - 1) * page_size
    result = await db.execute(base_query.order_by(desc(Alert.updated_at)).offset(offset).limit(page_size))
    items = result.scalars().all()

    return {
        "items": [serialize_alert_item(item) for item in items],
        "total": total,
        "page": effective_page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
