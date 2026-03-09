from pydantic import BaseModel, Field
from typing import List, Optional


class FactCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, description="需要核查的文本")
    use_advanced: bool = Field(default=False, description="是否使用高级核查")


class FactCheckSource(BaseModel):
    title: str = ""
    url: str = ""
    snippet: str = ""
    relevance: float = 0.0


class FactCheckResponse(BaseModel):
    query: str
    verdict: str = "待核查"
    confidence: float = 0.0
    explanation: str = ""
    sources: List[FactCheckSource] = Field(default_factory=list)
    evidence_unavailable: bool = False


class FactCheckHistoryItem(BaseModel):
    id: str
    query: str
    verdict: str
    confidence: float
    checked_at: str


class FactCheckHistoryResponse(BaseModel):
    items: List[FactCheckHistoryItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class FactCheckMultiSourceRequest(BaseModel):
    text: str = Field(..., min_length=1)
    sources: List[str] = Field(default_factory=list, description="Specific sources to check against")


class FactCheckEvidenceOnlyRequest(BaseModel):
    text: str = Field(..., min_length=1)


class FactCheckEvidenceResponse(BaseModel):
    query: str
    evidence: List[FactCheckSource] = Field(default_factory=list)
    total_sources: int = 0


class FactCheckSaveRequest(BaseModel):
    query: str
    verdict: str
    confidence: float = 0.0
    explanation: str = ""
    save_type: str = "all"
