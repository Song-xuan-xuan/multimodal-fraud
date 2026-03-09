from pydantic import BaseModel, Field
from typing import Any, List

class DetectTextRequest(BaseModel):
    text: str = Field(..., min_length=1)

class DetectUrlRequest(BaseModel):
    url: str = Field(..., min_length=1)

class DetectAITextResponse(BaseModel):
    is_ai_generated: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    probability: float = Field(default=0.0, ge=0.0, le=1.0)
    label: str = ""
    overall_label: str = ""
    summary: str = ""
    conclusion: str = ""
    details: dict[str, Any] = Field(default_factory=dict)

class DetectAIImageResponse(BaseModel):
    is_ai_generated: bool = False
    confidence: float = 0.0
    probability: float = 0.0
    label: str = ""
    summary: str = ""
    conclusion: str = ""
    details: dict[str, Any] = Field(default_factory=dict)

class DetectAIAudioResponse(BaseModel):
    is_ai_generated: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    probability: float = Field(default=0.0, ge=0.0, le=1.0)
    label: str = ""
    overall_label: str = ""
    summary: str = ""
    conclusion: str = ""
    transcript: str = ""
    details: dict[str, Any] = Field(default_factory=dict)

class DetectMultimodalResponse(BaseModel):
    is_fake: bool = False
    confidence: float = 0.0
    text_analysis: dict = Field(default_factory=dict)
    image_analysis: dict = Field(default_factory=dict)

class DetectNewsResponse(BaseModel):
    label: str = "未知"
    confidence: float = 0.0
    credibility_score: float = 0.0
    dimensions: dict = Field(default_factory=dict)
    summary: str = ""
    conclusion: str = ""

class DetectAggregateRequest(BaseModel):
    title: str = ""
    content: str = ""
    url: str = ""

class DetectAggregateResponse(BaseModel):
    news_detection: DetectNewsResponse = Field(default_factory=DetectNewsResponse)
    ai_text_detection: DetectAITextResponse = Field(default_factory=DetectAITextResponse)
    overall_credibility: float = 0.0
    overall_label: str = "未知"

class DetectUrlResponse(BaseModel):
    title: str = ""
    content: str = ""
    url: str = ""
    title_txt_match: bool = True
    title_txt_similarity: float = 0.0
    text_pic_similarity: float = 0.0
    consistency_result: str = "未知"
    details: dict = Field(default_factory=dict)

class DetectFileResponse(BaseModel):
    title: str = ""
    content: str = ""
    title_txt_match: bool = True
    title_txt_similarity: float = 0.0
    consistency_result: str = "未知"
    details: dict = Field(default_factory=dict)

class DetectSegmentRequest(BaseModel):
    title: str = ""
    content: str = Field(..., min_length=1)
    segment_size: int = Field(default=500, ge=200, le=1000)

class SegmentResult(BaseModel):
    segment_id: int = 0
    text: str = ""
    label: str = "未知"
    real_probability: float = 0.0
    fake_probability: float = 0.0

class DetectSegmentResponse(BaseModel):
    credibility_score: float = 0.0
    credibility_level: str = "未知"
    segment_count: int = 0
    conclusion: str = ""
    segments: List[SegmentResult] = Field(default_factory=list)
    feature_tags: dict = Field(default_factory=dict)
