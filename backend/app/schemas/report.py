from pydantic import BaseModel, Field


class ReportSubmitRequest(BaseModel):
    type: str = Field(..., min_length=1)
    url: str = ""
    description: str = Field(..., min_length=1)


class ReportSubmitResponse(BaseModel):
    report_id: str
    message: str


class ReportItem(BaseModel):
    id: int
    report_id: str
    type: str
    url: str = ""
    description: str
    reported_by: str = ""
    status: str
    review_reason: str = ""
    reviewed_by: str = ""
    reviewed_at: str = ""
    created_at: str


class ReportReviewRequest(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    reason: str | None = Field(default=None, max_length=1000)


class ReportReviewResponse(BaseModel):
    message: str
    item: ReportItem


class ReportListResponse(BaseModel):
    items: list[ReportItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class ReportExportResponse(BaseModel):
    news_id: str
    title: str = ""
    label: str = ""
    location: str = ""
    platform: str = ""
    publish_time: str = ""
    summary: str = ""
    conclusion: str = ""
    evidence_count: int = 0
    evidences: list[dict] = Field(default_factory=list)
