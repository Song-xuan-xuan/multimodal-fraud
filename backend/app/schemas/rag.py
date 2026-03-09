from pydantic import BaseModel, Field
from typing import List, Optional

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    session_id: str | None = None

class SourceNode(BaseModel):
    text: str = ""
    score: float = 0.0
    metadata: dict = Field(default_factory=dict)

class AskResponse(BaseModel):
    answer: str
    sources: List[SourceNode] = Field(default_factory=list)
    session_id: str = ""
