from pydantic import BaseModel, Field


class EvidenceResponse(BaseModel):
    id: int
    news_id: str
    content: str
    source: str = ""
    submitted_by: str = ""
    submitted_at: str
    status: str = "pending"


class SubmitEvidenceRequest(BaseModel):
    news_id: str
    content: str = Field(..., min_length=1)
    source: str | None = None


class LeaderboardItem(BaseModel):
    username: str
    contributions: int


class LeaderboardResponse(BaseModel):
    items: list[LeaderboardItem] = Field(default_factory=list)


class ForumPostResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: str


class CreateForumPostRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class ForumPostListResponse(BaseModel):
    items: list[ForumPostResponse] = Field(default_factory=list)
    total: int = 0
