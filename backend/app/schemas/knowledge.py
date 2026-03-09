from typing import Literal

from pydantic import BaseModel, Field

KnowledgeType = Literal["case", "law", "guideline", "notice"]


class KnowledgeItemCreate(BaseModel):
    item_id: str = Field(..., min_length=1, max_length=255)
    item_type: KnowledgeType = "case"
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    conclusion: str = ""
    fraud_type: str = ""
    risk_level: str = ""
    source: str = ""
    tags: list[str] = Field(default_factory=list)
    target_groups: list[str] = Field(default_factory=list)
    signals: list[str] = Field(default_factory=list)
    advice: list[str] = Field(default_factory=list)


class KnowledgeItemReviewRequest(BaseModel):
    status: Literal["approved", "rejected"]
    reason: str | None = Field(default=None, max_length=1000)


class KnowledgeItemResponse(BaseModel):
    id: int
    item_id: str
    item_type: str
    title: str
    content: str
    conclusion: str = ""
    fraud_type: str = ""
    risk_level: str = ""
    source: str = ""
    tags: list[str] = Field(default_factory=list)
    target_groups: list[str] = Field(default_factory=list)
    signals: list[str] = Field(default_factory=list)
    advice: list[str] = Field(default_factory=list)
    status: str = "pending"
    submitted_by: str = ""
    reviewed_by: str = ""
    reviewed_reason: str = ""
    created_at: str = ""
    updated_at: str = ""


class KnowledgeItemListResponse(BaseModel):
    items: list[KnowledgeItemResponse] = Field(default_factory=list)
    total: int = 0


class KnowledgeRebuildResponse(BaseModel):
    message: str
    item_count: int = 0
    storage_path: str = ""
    status: str = "ready"
