from pydantic import BaseModel, Field
from typing import List, Optional

from app.schemas.rag import SourceNode

class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1)

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: str
    sources: List[SourceNode] = Field(default_factory=list)
    retrieval_mode: Optional[str] = None

class ChatCreate(BaseModel):
    title: str = Field(default="新对话")


class ChatRenameRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)


class ChatResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    is_shared: bool = False
    messages: List[ChatMessageResponse] = Field(default_factory=list)


class ChatSendResponse(BaseModel):
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse

class ChatListItem(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0

class ChatListResponse(BaseModel):
    items: List[ChatListItem]
    total: int


class ChatShareRequest(BaseModel):
    chat_id: str
    message_index: Optional[int] = None
    is_readonly: bool = True


class ChatShareResponse(BaseModel):
    share_id: str
    share_url: str


class SharedChatResponse(BaseModel):
    title: str
    shared_by: str = ""
    created_at: str
    messages: List[ChatMessageResponse] = Field(default_factory=list)
    is_readonly: bool = True
