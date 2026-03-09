from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.evidence import Evidence

PENDING_STATUS = "pending"
APPROVED_STATUS = "approved"
REJECTED_STATUS = "rejected"
ALLOWED_REVIEW_TARGETS = {APPROVED_STATUS, REJECTED_STATUS}


def serialize_evidence_item(item: Evidence) -> dict:
    return {
        "id": item.id,
        "news_id": item.news_id,
        "content": item.content,
        "source": item.source or "",
        "submitted_by": item.submitted_by or "",
        "submitted_at": item.submitted_at.isoformat(),
        "status": item.status,
        "reason": item.reason or "",
        "reviewed_by": item.reviewed_by or "",
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else "",
    }


async def build_user_evidence_stats(db: AsyncSession, username: str) -> dict:
    stats_query = select(
        func.count(Evidence.id).label("total"),
        func.sum(case((Evidence.status == PENDING_STATUS, 1), else_=0)).label("pending"),
        func.sum(case((Evidence.status == APPROVED_STATUS, 1), else_=0)).label("approved"),
        func.sum(case((Evidence.status == REJECTED_STATUS, 1), else_=0)).label("rejected"),
    ).where(Evidence.submitted_by == username)

    stats_result = (await db.execute(stats_query)).one()
    return {
        "total": int(stats_result.total or 0),
        "pending": int(stats_result.pending or 0),
        "approved": int(stats_result.approved or 0),
        "rejected": int(stats_result.rejected or 0),
    }


async def review_evidence(
    db: AsyncSession,
    submission_id: int,
    target_status: str,
    reviewer_username: str,
    reason: str | None,
) -> Evidence:
    if target_status not in ALLOWED_REVIEW_TARGETS:
        raise HTTPException(status_code=400, detail="非法审核状态，仅支持 approved/rejected")

    result = await db.execute(select(Evidence).where(Evidence.id == submission_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="提交不存在")

    if evidence.status != PENDING_STATUS:
        raise HTTPException(
            status_code=409,
            detail=f"当前状态为 {evidence.status}，仅 pending 状态可审核",
        )

    evidence.status = target_status
    evidence.reason = reason.strip() if reason and reason.strip() else None
    evidence.reviewed_by = reviewer_username
    evidence.reviewed_at = datetime.now(timezone.utc)

    await db.flush()
    return evidence
