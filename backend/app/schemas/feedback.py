from typing import Literal

from pydantic import BaseModel, Field


FeedbackType = Literal["vote", "feedback"]
VoteOption = Literal["agree", "disagree"]
FeedbackStatus = Literal["pending", "approved", "rejected"]
ReviewableFeedbackStatus = Literal["approved", "rejected"]


class VoteSubmitRequest(BaseModel):
    news_id: str = Field(..., min_length=1, max_length=255)
    vote: VoteOption


class FeedbackSubmitRequest(BaseModel):
    news_id: str = Field(..., min_length=1, max_length=255)
    feedback: str = Field(..., min_length=1, max_length=5000)


class FeedbackItem(BaseModel):
    id: int
    news_id: str
    type: FeedbackType
    content: str
    submitted_by: str
    submitted_at: str
    updated_at: str
    status: FeedbackStatus = "pending"
    reason: str = ""
    reviewed_by: str = ""
    reviewed_at: str = ""


class FeedbackSubmitResponse(BaseModel):
    message: str
    item: FeedbackItem
    idempotent: bool


class FeedbackReviewRequest(BaseModel):
    status: ReviewableFeedbackStatus
    reason: str | None = Field(default=None, max_length=1000)


class FeedbackReviewResponse(BaseModel):
    message: str
    item: FeedbackItem


class FeedbackListResponse(BaseModel):
    items: list[FeedbackItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class NewsFeedbackStatsResponse(BaseModel):
    news_id: str
    total: int = 0
    vote_total: int = 0
    vote_agree: int = 0
    vote_disagree: int = 0
    feedback_total: int = 0
    pending: int = 0
    approved: int = 0
    rejected: int = 0
