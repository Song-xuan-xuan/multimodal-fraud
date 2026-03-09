import uuid
from datetime import datetime, timezone
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.chat import Chat, ChatMessage

async def create_chat(db: AsyncSession, user_id: int, title: str = "新对话") -> Chat:
    chat = Chat(id=str(uuid.uuid4()), user_id=user_id, title=title)
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat

async def list_chats(db: AsyncSession, user_id: int) -> list:
    result = await db.execute(
        select(Chat).where(Chat.user_id == user_id).order_by(Chat.updated_at.desc())
    )
    return list(result.scalars().all())

async def get_chat(db: AsyncSession, chat_id: str) -> Chat | None:
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    return result.scalar_one_or_none()

async def get_messages(db: AsyncSession, chat_id: str) -> list:
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.chat_id == chat_id).order_by(ChatMessage.created_at)
    )
    return list(result.scalars().all())

async def add_message(db: AsyncSession, chat_id: str, role: str, content: str) -> ChatMessage:
    msg = ChatMessage(chat_id=chat_id, role=role, content=content)
    db.add(msg)
    # Update chat's updated_at
    chat_result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = chat_result.scalar_one_or_none()
    if chat:
        chat.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(msg)
    return msg

async def delete_chat(db: AsyncSession, chat_id: str):
    await db.execute(delete(ChatMessage).where(ChatMessage.chat_id == chat_id))
    await db.execute(delete(Chat).where(Chat.id == chat_id))
    await db.commit()
