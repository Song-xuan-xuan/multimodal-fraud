from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator


class NewsListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)
    keyword: str | None = None
    province: str | None = None
    label: str | None = None


class CredibilityDimensionScores(BaseModel):
    source: float = 0.0
    content: float = 0.0
    logic: float = 0.0
    propagation: float = 0.0
    AI: float = 0.0
    content1: float = 0.0
    content2: float = 0.0

    @field_validator("source", "content", "logic", "propagation", "AI", "content1", "content2", mode="before")
    @classmethod
    def coerce_to_float(cls, v: object) -> float:
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return 0.0
            try:
                return float(v)
            except ValueError:
                return 0.0
        return 0.0


class CredibilityInfo(BaseModel):
    score: float = 0.0
    dimension_scores: CredibilityDimensionScores = Field(
        default_factory=CredibilityDimensionScores
    )
    verification_progress: int = Field(
        default=0,
        ge=0,
        le=100,
        description="核查进度百分比：0=未核查，1-99=核查中，100=核查完成",
    )
    verified: bool = False


class PropagationTrendPoint(BaseModel):
    timestamp: str = ""
    value: int = 0


class PropagationPlatformItem(BaseModel):
    platform: str = ""
    count: int = 0
    ratio: float = 0.0


class PropagationRegionItem(BaseModel):
    region: str = ""
    count: int = 0


class PropagationInfo(BaseModel):
    total_mentions: int = 0
    peak_timestamp: str = ""
    trend: List[PropagationTrendPoint] = Field(default_factory=list)
    platform_distribution: List[PropagationPlatformItem] = Field(default_factory=list)
    region_distribution: List[PropagationRegionItem] = Field(default_factory=list)


class RelatedNewsItem(BaseModel):
    news_id: str = ""
    title: str = ""
    similarity: float = 0.0
    platform: str = ""
    publish_time: str = ""
    url: str = ""


class RelationNode(BaseModel):
    node_id: str = ""
    name: str = ""
    category: str = ""
    value: float = 0.0


class RelationEdge(BaseModel):
    source: str = ""
    target: str = ""
    relation_type: str = ""
    weight: float = 0.0


class RelationsInfo(BaseModel):
    related_news: List[RelatedNewsItem] = Field(default_factory=list)
    nodes: List[RelationNode] = Field(default_factory=list)
    edges: List[RelationEdge] = Field(default_factory=list)


class NewsDetailUIFallbacks(BaseModel):
    summary: str = "暂无摘要"
    conclusion: str = "暂无结论"
    propagation_empty_reason: str = "暂无传播数据"
    relations_empty_reason: str = "暂无关联关系数据"


class NewsDetailResponse(BaseModel):
    news_id: str
    title: str = ""
    content: str = ""
    url: str = ""
    pic_url: str = ""
    label: str = "未知"
    platform: str = ""
    hashtag: str = ""
    summary: str = ""
    location: str = ""
    conclusion: str = ""
    publish_time: str = ""
    check_time: str = ""
    iscredit: bool = False
    credibility: CredibilityInfo = Field(default_factory=CredibilityInfo)
    propagation: PropagationInfo = Field(default_factory=PropagationInfo)
    relations: RelationsInfo = Field(default_factory=RelationsInfo)
    ui_fallbacks: NewsDetailUIFallbacks = Field(default_factory=NewsDetailUIFallbacks)
    propagation_data: Dict[str, Any] = Field(default_factory=dict)
    relations_data: Dict[str, Any] = Field(default_factory=dict)


class NewsResponse(BaseModel):
    news_id: str
    title: str = ""
    content: str = ""
    url: str = ""
    pic_url: str = ""
    label: str = "未知"
    platform: str = ""
    hashtag: str = ""
    summary: str = ""
    location: str = ""
    conclusion: str = ""
    publish_time: str = ""
    check_time: str = ""
    iscredit: bool = False
    credibility: CredibilityInfo = Field(default_factory=CredibilityInfo)
    propagation_data: Dict[str, Any] = Field(default_factory=dict)
    relations_data: Dict[str, Any] = Field(default_factory=dict)


class NewsListResponse(BaseModel):
    items: List[NewsResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class NewsSearchRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    platforms: List[str] = Field(default_factory=list)


class NewsAnalyzeRequest(BaseModel):
    url: str = ""
    title: str = ""
    content: str = ""


class NewsAnalyzeResponse(BaseModel):
    title: str = ""
    keywords: List[str] = Field(default_factory=list)
    sentiment: str = "neutral"
    sentiment_score: float = 0.0
    summary: str = ""
    related_count: int = 0
    impact_level: str = "low"
    details: Dict[str, Any] = Field(default_factory=dict)


class NewsTimelineRequest(BaseModel):
    news_id: str = ""
    title: str = ""
    content: str = ""


class TimelineEvent(BaseModel):
    timestamp: str = ""
    platform: str = ""
    description: str = ""
    shares: int = 0


class NewsTimelineResponse(BaseModel):
    news_id: str = ""
    title: str = ""
    timeline: List[TimelineEvent] = Field(default_factory=list)
    platform_similarity: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphResponse(BaseModel):
    seed_news_id: str = ""
    seed_title: str = ""
    nodes: List[RelationNode] = Field(default_factory=list)
    edges: List[RelationEdge] = Field(default_factory=list)
