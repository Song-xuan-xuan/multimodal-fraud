import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.db.base import get_db
from app.schemas.chat import (
    ChatCreate,
    ChatListItem,
    ChatListResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatRenameRequest,
    ChatResponse,
    ChatSendResponse,
    ChatShareRequest,
    ChatShareResponse,
    SharedChatResponse,
)
from app.services.chat_service import (
    build_chat_message_payload,
    build_chat_message_payload_from_dict,
    create_new_chat,
    get_chat_detail,
    get_user_chats,
    remove_chat,
    rename_chat,
    send_message,
)

router = APIRouter()


@router.get("/", response_model=ChatListResponse)
async def list_chats(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chats = await get_user_chats(db, user.id)
    return ChatListResponse(items=[ChatListItem(**c) for c in chats], total=len(chats))


@router.post("/", response_model=ChatResponse)
async def create_chat(req: ChatCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chat = await create_new_chat(db, user.id, req.title)
    return ChatResponse(
        id=chat.id, title=chat.title,
        created_at=str(chat.created_at) if chat.created_at else "",
        updated_at=str(chat.updated_at) if chat.updated_at else "",
    )


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat_api(chat_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        chat, messages = await get_chat_detail(db, chat_id, user.id)
        return ChatResponse(
            id=chat.id, title=chat.title,
            created_at=str(chat.created_at) if chat.created_at else "",
            updated_at=str(chat.updated_at) if chat.updated_at else "",
            is_shared=chat.is_shared,
            messages=[ChatMessageResponse(**build_chat_message_payload(m)) for m in messages],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{chat_id}/messages", response_model=ChatSendResponse)
async def send_message_api(
    chat_id: str, req: ChatMessageCreate,
    user=Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    try:
        user_msg, assistant_msg = await send_message(db, chat_id, user.id, req.content)
        return ChatSendResponse(
            user_message=ChatMessageResponse(**build_chat_message_payload(user_msg)),
            assistant_message=ChatMessageResponse(**build_chat_message_payload(assistant_msg)),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{chat_id}")
async def delete_chat_api(chat_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        await remove_chat(db, chat_id, user.id)
        return {"message": "对话已删除"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{chat_id}", response_model=ChatResponse)
async def rename_chat_api(
    chat_id: str,
    req: ChatRenameRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        chat = await rename_chat(db, chat_id, user.id, req.title)
        return ChatResponse(
            id=chat.id,
            title=chat.title,
            created_at=str(chat.created_at) if chat.created_at else "",
            updated_at=str(chat.updated_at) if chat.updated_at else "",
            is_shared=chat.is_shared,
        )
    except ValueError as e:
        detail = str(e)
        raise HTTPException(status_code=400 if detail == "对话标题不能为空" else 404, detail=detail)


# --- Chat sharing endpoints ---

def _get_shared_dir() -> Path:
    settings = get_settings()
    shared_dir = settings.storage_path / "shared_chats"
    shared_dir.mkdir(parents=True, exist_ok=True)
    return shared_dir


@router.post("/share", response_model=ChatShareResponse)
async def share_chat(
    req: ChatShareRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        chat, messages = await get_chat_detail(db, req.chat_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    share_id = uuid4().hex[:8]
    msg_list = [
        build_chat_message_payload(m)
        for m in messages
    ]

    if req.message_index is not None and 0 <= req.message_index < len(msg_list):
        msg_list = msg_list[: req.message_index + 1]

    shared_data = {
        "title": chat.title,
        "shared_by": user.username,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "messages": msg_list,
        "is_readonly": req.is_readonly,
        "original_chat_id": req.chat_id,
    }

    shared_path = _get_shared_dir() / f"{share_id}.json"
    shared_path.write_text(json.dumps(shared_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return ChatShareResponse(share_id=share_id, share_url=f"/shared/{share_id}")


@router.get("/shared/{share_id}", response_model=SharedChatResponse)
async def get_shared_chat(share_id: str):
    if "/" in share_id or "\\" in share_id:
        raise HTTPException(status_code=400, detail="Invalid share ID")

    shared_path = _get_shared_dir() / f"{share_id}.json"
    if not shared_path.exists():
        raise HTTPException(status_code=404, detail="Shared chat not found")

    data = json.loads(shared_path.read_text(encoding="utf-8"))
    return SharedChatResponse(
        title=data.get("title", ""),
        shared_by=data.get("shared_by", ""),
        created_at=data.get("created_at", ""),
        messages=[ChatMessageResponse(**build_chat_message_payload_from_dict(m)) for m in data.get("messages", [])],
        is_readonly=data.get("is_readonly", True),
    )


@router.post("/shared/{share_id}/reply")
async def reply_shared_chat(
    share_id: str,
    req: ChatMessageCreate,
    user=Depends(get_current_user),
):
    if "/" in share_id or "\\" in share_id:
        raise HTTPException(status_code=400, detail="Invalid share ID")

    shared_path = _get_shared_dir() / f"{share_id}.json"
    if not shared_path.exists():
        raise HTTPException(status_code=404, detail="Shared chat not found")

    data = json.loads(shared_path.read_text(encoding="utf-8"))
    if data.get("is_readonly", True):
        raise HTTPException(status_code=403, detail="This shared chat is read-only")

    new_msg = {
        "id": len(data.get("messages", [])) + 1,
        "role": "user",
        "content": req.content,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    data.setdefault("messages", []).append(new_msg)
    shared_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"message": "Reply added", "reply": new_msg}
