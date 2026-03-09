from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.base import get_db
from app.schemas.feedback import (
    FeedbackListResponse,
    FeedbackReviewRequest,
    FeedbackReviewResponse,
    FeedbackSubmitRequest,
    FeedbackSubmitResponse,
    NewsFeedbackStatsResponse,
    VoteSubmitRequest,
)
from app.services.feedback_service import (
    get_news_feedback_stats,
    list_my_feedback,
    review_feedback,
    serialize_feedback_item,
    submit_feedback,
    submit_vote,
)

router = APIRouter()


@router.post("/submit-vote", response_model=FeedbackSubmitResponse)
async def submit_vote_api(
    req: VoteSubmitRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item, changed = await submit_vote(db, req.news_id, user.username, req.vote)
    return FeedbackSubmitResponse(
        message="投票提交成功" if not changed else "投票已更新",
        item=serialize_feedback_item(item),
        idempotent=not changed,
    )


@router.post("/submit-feedback", response_model=FeedbackSubmitResponse)
async def submit_feedback_api(
    req: FeedbackSubmitRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item, changed = await submit_feedback(db, req.news_id, user.username, req.feedback)
    return FeedbackSubmitResponse(
        message="反馈提交成功" if not changed else "反馈已更新",
        item=serialize_feedback_item(item),
        idempotent=not changed,
    )


@router.post("/{submission_id}/review", response_model=FeedbackReviewResponse)
async def review_feedback_api(
    submission_id: int,
    req: FeedbackReviewRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await review_feedback(
        db,
        submission_id=submission_id,
        target_status=req.status,
        reviewer_username=user.username,
        reason=req.reason,
    )
    return FeedbackReviewResponse(message="审核成功", item=serialize_feedback_item(item))


@router.get("/my", response_model=FeedbackListResponse)
async def list_my_feedback_api(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    news_id: str | None = Query(default=None),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await list_my_feedback(
        db,
        user.username,
        page=page,
        page_size=page_size,
        feedback_type=type,
        status=status,
        news_id=news_id,
    )
    return FeedbackListResponse(**result)


@router.get("/stats/{news_id}", response_model=NewsFeedbackStatsResponse)
async def get_feedback_stats_api(
    news_id: str,
    db: AsyncSession = Depends(get_db),
):
    stats = await get_news_feedback_stats(db, news_id)
    return NewsFeedbackStatsResponse(**stats)
