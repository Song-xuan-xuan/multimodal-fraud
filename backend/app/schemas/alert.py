from typing import Any, Literal

from pydantic import BaseModel, Field


EventContractVersion = Literal["v1"]
AlertStatus = Literal["pending", "approved", "rejected"]
ReviewTargetStatus = Literal["approved", "rejected"]


class AlertCreateRequest(BaseModel):
    alert_type: str = Field(default="feedback_review", min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=5000)
    recipient_username: str | None = Field(default=None, min_length=1, max_length=255)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AlertReviewRequest(BaseModel):
    status: ReviewTargetStatus
    feedback: str | None = Field(default=None, max_length=1000)


class AlertItem(BaseModel):
    alert_id: str
    alert_type: str
    title: str
    message: str
    recipient_username: str
    created_by: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: AlertStatus
    review_feedback: str = ""
    reviewed_by: str = ""
    reviewed_at: str = ""
    created_at: str
    updated_at: str


class AlertEventPayload(BaseModel):
    event: Literal["alert_created", "review_updated"]
    contract_version: EventContractVersion = "v1"
    occurred_at: str
    recipient_username: str
    triggered_by: str
    alert: AlertItem


class AlertCreateResponse(BaseModel):
    message: str
    item: AlertItem
    event: AlertEventPayload


class AlertReviewResponse(BaseModel):
    message: str
    item: AlertItem
    event: AlertEventPayload


class AlertListResponse(BaseModel):
    items: list[AlertItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
