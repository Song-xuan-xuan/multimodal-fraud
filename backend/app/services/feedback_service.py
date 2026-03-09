from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.feedback import Feedback
from app.db.models.news import NewsArticle

PENDING_STATUS = "pending"
APPROVED_STATUS = "approved"
REJECTED_STATUS = "rejected"
ALLOWED_REVIEW_TARGETS = {APPROVED_STATUS, REJECTED_STATUS}

TYPE_VOTE = "vote"
TYPE_FEEDBACK = "feedback"


def serialize_feedback_item(item: Feedback) -> dict:
    return {
        "id": item.id,
        "news_id": item.news_id,
        "type": item.feedback_type,
        "content": item.content,
        "submitted_by": item.submitted_by,
        "submitted_at": item.submitted_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
        "status": item.status,
        "reason": item.reason or "",
        "reviewed_by": item.reviewed_by or "",
        "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else "",
    }


async def _ensure_news_exists(db: AsyncSession, news_id: str) -> None:
    result = await db.execute(select(NewsArticle.news_id).where(NewsArticle.news_id == news_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail=f"新闻 {news_id} 不存在")


async def _upsert_feedback(
    db: AsyncSession,
    *,
    news_id: str,
    username: str,
    feedback_type: str,
    content: str,
) -> tuple[Feedback, bool]:
    await _ensure_news_exists(db, news_id)

    existing_query = select(Feedback).where(
        Feedback.news_id == news_id,
        Feedback.submitted_by == username,
        Feedback.feedback_type == feedback_type,
    )
    existing_result = await db.execute(existing_query)
    item = existing_result.scalar_one_or_none()

    cleaned_content = content.strip()
    now = datetime.now(timezone.utc)

    if item:
        changed = item.content != cleaned_content
        item.content = cleaned_content
        item.updated_at = now
        item.status = PENDING_STATUS
        item.reason = None
        item.reviewed_by = None
        item.reviewed_at = None
        await db.flush()
        return item, changed

    item = Feedback(
        news_id=news_id,
        submitted_by=username,
        feedback_type=feedback_type,
        content=cleaned_content,
        submitted_at=now,
        updated_at=now,
        status=PENDING_STATUS,
    )
    db.add(item)
    await db.flush()
    return item, False


async def submit_vote(db: AsyncSession, news_id: str, username: str, vote: str) -> tuple[Feedback, bool]:
    return await _upsert_feedback(
        db,
        news_id=news_id,
        username=username,
        feedback_type=TYPE_VOTE,
        content=vote,
    )


async def submit_feedback(db: AsyncSession, news_id: str, username: str, feedback: str) -> tuple[Feedback, bool]:
    return await _upsert_feedback(
        db,
        news_id=news_id,
        username=username,
        feedback_type=TYPE_FEEDBACK,
        content=feedback,
    )


async def review_feedback(
    db: AsyncSession,
    submission_id: int,
    target_status: str,
    reviewer_username: str,
    reason: str | None,
) -> Feedback:
    if target_status not in ALLOWED_REVIEW_TARGETS:
        raise HTTPException(status_code=400, detail="非法审核状态，仅支持 approved/rejected")

    result = await db.execute(select(Feedback).where(Feedback.id == submission_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="提交不存在")

    if item.status != PENDING_STATUS:
        raise HTTPException(
            status_code=409,
            detail=f"当前状态为 {item.status}，仅 pending 状态可审核",
        )

    item.status = target_status
    item.reason = reason.strip() if reason and reason.strip() else None
    item.reviewed_by = reviewer_username
    item.reviewed_at = datetime.now(timezone.utc)
    item.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return item


async def list_my_feedback(
    db: AsyncSession,
    username: str,
    *,
    page: int,
    page_size: int,
    feedback_type: str | None,
    status: str | None,
    news_id: str | None,
) -> dict:
    base_query = select(Feedback).where(Feedback.submitted_by == username)

    if feedback_type:
        base_query = base_query.where(Feedback.feedback_type == feedback_type)
    if status:
        base_query = base_query.where(Feedback.status == status)
    if news_id:
        base_query = base_query.where(Feedback.news_id == news_id)

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    effective_page = min(page, total_pages) if total_pages > 0 else 1

    offset = (effective_page - 1) * page_size
    result = await db.execute(base_query.order_by(desc(Feedback.updated_at)).offset(offset).limit(page_size))
    items = result.scalars().all()

    return {
        "items": [serialize_feedback_item(item) for item in items],
        "total": total,
        "page": effective_page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


async def get_news_feedback_stats(db: AsyncSession, news_id: str) -> dict:
    await _ensure_news_exists(db, news_id)

    stats_query = select(
        func.count(Feedback.id).label("total"),
        func.sum(case((Feedback.feedback_type == TYPE_VOTE, 1), else_=0)).label("vote_total"),
        func.sum(
            case(
                ((Feedback.feedback_type == TYPE_VOTE) & (Feedback.content == "agree"), 1),
                else_=0,
            )
        ).label("vote_agree"),
        func.sum(
            case(
                ((Feedback.feedback_type == TYPE_VOTE) & (Feedback.content == "disagree"), 1),
                else_=0,
            )
        ).label("vote_disagree"),
        func.sum(case((Feedback.feedback_type == TYPE_FEEDBACK, 1), else_=0)).label("feedback_total"),
        func.sum(case((Feedback.status == PENDING_STATUS, 1), else_=0)).label("pending"),
        func.sum(case((Feedback.status == APPROVED_STATUS, 1), else_=0)).label("approved"),
        func.sum(case((Feedback.status == REJECTED_STATUS, 1), else_=0)).label("rejected"),
    ).where(Feedback.news_id == news_id)

    row = (await db.execute(stats_query)).one()
    return {
        "news_id": news_id,
        "total": int(row.total or 0),
        "vote_total": int(row.vote_total or 0),
        "vote_agree": int(row.vote_agree or 0),
        "vote_disagree": int(row.vote_disagree or 0),
        "feedback_total": int(row.feedback_total or 0),
        "pending": int(row.pending or 0),
        "approved": int(row.approved or 0),
        "rejected": int(row.rejected or 0),
    }
