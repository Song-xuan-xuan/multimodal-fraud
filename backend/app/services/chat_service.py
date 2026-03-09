"""Chat service with LLM integration for AI assistant replies."""

import logging
from typing import List

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.repositories.chat_repo import (
    create_chat as repo_create_chat,
    list_chats as repo_list_chats,
    get_chat,
    get_messages,
    add_message,
    delete_chat as repo_delete_chat,
)

logger = logging.getLogger(__name__)

# System prompt for the AI assistant
SYSTEM_PROMPT = (
    "你是一个专业的多模态反诈智能助手。你可以帮助用户：\n"
    "1. 分析聊天记录、截图和可疑内容中的诈骗风险\n"
    "2. 解释常见诈骗剧本、高风险话术与诱导特征\n"
    "3. 提供风险核验、处置建议与自我保护方案\n"
    "4. 回答与反诈知识、风险识别和求助路径相关的问题\n"
    "请用中文回答，回答要简洁、准确、有帮助，并优先提醒用户避免转账、泄露验证码或共享屏幕。"
)


async def _call_llm(messages: List[dict]) -> str:
    """Call OpenAI-compatible API to generate a reply.

    Args:
        messages: List of {"role": ..., "content": ...} message dicts.

    Returns:
        The assistant's reply text.
    """
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        return "反诈助手回复功能未配置 API 密钥，请在 .env 中设置 OPENAI_API_KEY。"

    api_url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"

    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": messages,
        "temperature": settings.OPENAI_TEMPERATURE,
        "max_tokens": 1024,
    }
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(api_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except httpx.TimeoutException:
        logger.error("LLM API timeout")
        return "AI回复超时，请稍后再试。"
    except Exception as e:
        logger.error("LLM API error: %s", e)
        return f"AI回复出错: {e}"


async def create_new_chat(db: AsyncSession, user_id: int, title: str = "新对话"):
    return await repo_create_chat(db, user_id, title)


async def get_user_chats(db: AsyncSession, user_id: int):
    chats = await repo_list_chats(db, user_id)
    result = []
    for chat in chats:
        messages = await get_messages(db, chat.id)
        result.append({
            "id": chat.id,
            "title": chat.title,
            "created_at": str(chat.created_at) if chat.created_at else "",
            "updated_at": str(chat.updated_at) if chat.updated_at else "",
            "message_count": len(messages),
        })
    return result


async def get_chat_detail(db: AsyncSession, chat_id: str, user_id: int):
    chat = await get_chat(db, chat_id)
    if not chat or chat.user_id != user_id:
        raise ValueError("对话不存在或无权访问")
    messages = await get_messages(db, chat_id)
    return chat, messages


async def send_message(db: AsyncSession, chat_id: str, user_id: int, content: str):
    """Send a user message and get an AI reply."""
    chat = await get_chat(db, chat_id)
    if not chat or chat.user_id != user_id:
        raise ValueError("对话不存在或无权访问")

    # Save user message
    user_msg = await add_message(db, chat_id, "user", content)

    # Build conversation history for LLM
    history = await get_messages(db, chat_id)
    llm_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        llm_messages.append({"role": msg.role, "content": msg.content})

    # Generate AI reply
    reply_text = await _call_llm(llm_messages)
    assistant_msg = await add_message(db, chat_id, "assistant", reply_text)

    return user_msg, assistant_msg


async def remove_chat(db: AsyncSession, chat_id: str, user_id: int):
    chat = await get_chat(db, chat_id)
    if not chat or chat.user_id != user_id:
        raise ValueError("对话不存在或无权访问")
    await repo_delete_chat(db, chat_id)
