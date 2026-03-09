from typing import Literal

from pydantic import BaseModel, Field


EvidenceStatus = Literal["pending", "approved", "rejected"]
ReviewableEvidenceStatus = Literal["approved", "rejected"]


class EvidenceItem(BaseModel):
    id: int
    news_id: str
    content: str
    source: str = ""
    submitted_by: str = ""
    submitted_at: str
    status: EvidenceStatus = "pending"
    reason: str = ""
    reviewed_by: str = ""
    reviewed_at: str = ""


class EvidenceReviewRequest(BaseModel):
    status: ReviewableEvidenceStatus
    reason: str | None = Field(default=None, max_length=1000)


class EvidenceReviewResponse(BaseModel):
    message: str
    item: EvidenceItem


class EvidenceSubmissionListResponse(BaseModel):
    items: list[EvidenceItem] = Field(default_factory=list)
    total: int = 0


class MyEvidenceStatsResponse(BaseModel):
    total: int = 0
    pending: int = 0
    approved: int = 0
    rejected: int = 0
