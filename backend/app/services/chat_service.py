"""Chat service with LLM integration for AI assistant replies."""

import asyncio
import json
import logging
from typing import Any, List

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
    rename_chat as repo_rename_chat,
)
from app.services.rag_service import retrieve_relevant_sources

logger = logging.getLogger(__name__)

RECENT_HISTORY_LIMIT = 8
RECENT_USER_QUERY_LIMIT = 3
HISTORY_CHAR_BUDGET = 2400
MESSAGE_CHAR_LIMIT = 600
RAG_QUERY_CHAR_LIMIT = 900
RAG_SOURCE_LIMIT = 3
RAG_SOURCE_TEXT_LIMIT = 320
RAG_SOURCES_MARKER = "\n\n[[RAG_SOURCES_JSON]]"

# System prompt for the AI assistant
SYSTEM_PROMPT = (
    "你是一个专业的多模态反诈智能助手。你可以帮助用户：\n"
    "1. 分析聊天记录、截图和可疑内容中的诈骗风险\n"
    "2. 解释常见诈骗剧本、高风险话术与诱导特征\n"
    "3. 提供风险核验、处置建议与自我保护方案\n"
    "4. 回答与反诈知识、风险识别和求助路径相关的问题\n"
    "请用中文回答，回答要简洁、准确、有帮助，并优先提醒用户避免转账、泄露验证码或共享屏幕。"
)


def _normalize_sources(sources: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for source in sources or []:
        if not isinstance(source, dict):
            continue
        normalized.append({
            "text": str(source.get("text", "") or ""),
            "score": float(source.get("score", 0.0) or 0.0),
            "metadata": source.get("metadata") or {},
        })
    return normalized


def encode_assistant_content(
    content: str,
    sources: list[dict[str, Any]] | None = None,
    retrieval_mode: str | None = None,
) -> str:
    normalized_sources = _normalize_sources(sources)
    cleaned_content = (content or "").strip()
    normalized_mode = str(retrieval_mode or "").strip()
    if not normalized_sources and not normalized_mode:
        return cleaned_content

    payload: dict[str, Any] = {}
    if normalized_sources:
        payload["sources"] = normalized_sources
    if normalized_mode:
        payload["retrieval_mode"] = normalized_mode
    payload = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return f"{cleaned_content}{RAG_SOURCES_MARKER}{payload}"


def decode_assistant_content(content: str) -> tuple[str, list[dict[str, Any]], str]:
    raw_content = str(content or "")
    marker_index = raw_content.rfind(RAG_SOURCES_MARKER)
    if marker_index < 0:
        return raw_content, [], "llm_only"

    payload = raw_content[marker_index + len(RAG_SOURCES_MARKER):].strip()
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return raw_content, [], "llm_only"

    sources = _normalize_sources(data.get("sources"))
    retrieval_mode = str(data.get("retrieval_mode") or "").strip()
    if not retrieval_mode:
        retrieval_mode = "knowledge_enhanced" if sources else "llm_only"

    return raw_content[:marker_index].rstrip(), sources, retrieval_mode


def build_chat_message_payload(message: Any) -> dict[str, Any]:
    content, sources, retrieval_mode = decode_assistant_content(getattr(message, "content", None))
    created_at = getattr(message, "created_at", "")
    role = getattr(message, "role", "assistant")
    return {
        "id": getattr(message, "id", 0),
        "role": role,
        "content": content,
        "created_at": str(created_at) if created_at else "",
        "sources": sources,
        "retrieval_mode": retrieval_mode if role == "assistant" else None,
    }


def build_chat_message_payload_from_dict(message: dict[str, Any]) -> dict[str, Any]:
    content, sources, retrieval_mode = decode_assistant_content(message.get("content", ""))
    role = message.get("role", "assistant")
    return {
        "id": message.get("id", 0),
        "role": role,
        "content": content,
        "created_at": str(message.get("created_at", "") or ""),
        "sources": _normalize_sources(message.get("sources")) or sources,
        "retrieval_mode": message.get("retrieval_mode") or (retrieval_mode if role == "assistant" else None),
    }


def _clip_text(value: str, limit: int) -> str:
    normalized = " ".join(str(value or "").split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(limit - 1, 0)].rstrip() + "…"


def _build_recent_history(history: list[dict[str, str]]) -> list[dict[str, str]]:
    trimmed_history = history[-RECENT_HISTORY_LIMIT:]
    budget = HISTORY_CHAR_BUDGET
    result: list[dict[str, str]] = []
    for message in reversed(trimmed_history):
        role = str(message.get("role", "") or "")
        content = _clip_text(str(message.get("content", "") or ""), MESSAGE_CHAR_LIMIT)
        if not content:
            continue
        remaining_budget = budget - len(content)
        if remaining_budget < 0 and result:
            break
        if remaining_budget < 0:
            content = _clip_text(content, budget)
        result.append({"role": role, "content": content})
        budget -= len(content)
        if budget <= 0:
            break

    return list(reversed(result))


def _build_rag_query(history: list[dict[str, str]]) -> str:
    recent_user_messages = [
        _clip_text(str(message.get("content", "") or "").strip(), MESSAGE_CHAR_LIMIT)
        for message in history
        if message.get("role") == "user" and str(message.get("content", "") or "").strip()
    ]
    query = "\n".join(recent_user_messages[-RECENT_USER_QUERY_LIMIT:])
    return _clip_text(query, RAG_QUERY_CHAR_LIMIT)


async def _retrieve_chat_sources(
    current_content: str,
    recent_history: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], str]:
    retrieval_errors: list[Exception] = []
    candidate_queries: list[str] = []

    primary_query = _clip_text(current_content, RAG_QUERY_CHAR_LIMIT)
    if primary_query:
        candidate_queries.append(primary_query)

    fallback_query = _build_rag_query(recent_history)
    if fallback_query and fallback_query != primary_query:
        candidate_queries.append(fallback_query)

    for query in candidate_queries:
        try:
            sources = await asyncio.to_thread(retrieve_relevant_sources, query)
            if sources:
                return sources, "knowledge_enhanced"
        except Exception as exc:
            retrieval_errors.append(exc)
            logger.warning("RAG retrieval failed for query %r: %s", query, exc)

    if retrieval_errors:
        return [], "retrieval_failed"
    return [], "retrieval_empty"


def _format_rag_context(sources: list[dict[str, Any]]) -> str:
    context_blocks: list[str] = []
    for index, source in enumerate(_normalize_sources(sources)[:RAG_SOURCE_LIMIT], start=1):
        metadata = source.get("metadata") or {}
        title = metadata.get("title") or metadata.get("item_id") or f"资料{index}"
        item_type = metadata.get("item_type") or "资料"
        fraud_type = metadata.get("fraud_type") or "未标注"
        origin = metadata.get("source") or "未提供来源"
        text = _clip_text(str(source.get("text", "") or "").strip(), RAG_SOURCE_TEXT_LIMIT)
        context_blocks.append(
            "\n".join([
                f"资料{index}: {title}",
                f"类型: {item_type}",
                f"诈骗类型: {fraud_type}",
                f"来源: {origin}",
                f"内容: {text}",
            ])
        )
    return "\n\n".join(context_blocks)


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
    decoded_history = []
    for msg in history:
        decoded_content, _, _ = decode_assistant_content(msg.content)
        decoded_history.append({"role": msg.role, "content": decoded_content})

    recent_history = _build_recent_history(decoded_history)
    rag_sources: list[dict[str, Any]] = []
    retrieval_mode = "llm_only"
    if content.strip():
        rag_sources, retrieval_mode = await _retrieve_chat_sources(content, recent_history)
        if retrieval_mode == "retrieval_failed":
            logger.warning("RAG retrieval failed, falling back to pure LLM reply")

    llm_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if rag_sources:
        llm_messages.append({
            "role": "system",
            "content": (
                "以下是知识库中检索到的相关诈骗事件、案例与资料。"
                "回答时请优先结合这些资料，并在资料不足时明确说明：\n\n"
                f"{_format_rag_context(rag_sources)}"
            ),
        })
    llm_messages.extend(recent_history)

    # Generate AI reply
    reply_text = await _call_llm(llm_messages)
    assistant_msg = await add_message(
        db,
        chat_id,
        "assistant",
        encode_assistant_content(reply_text, rag_sources, retrieval_mode),
    )

    return user_msg, assistant_msg


async def remove_chat(db: AsyncSession, chat_id: str, user_id: int):
    chat = await get_chat(db, chat_id)
    if not chat or chat.user_id != user_id:
        raise ValueError("对话不存在或无权访问")
    await repo_delete_chat(db, chat_id)


async def rename_chat(db: AsyncSession, chat_id: str, user_id: int, title: str):
    chat = await get_chat(db, chat_id)
    if not chat or chat.user_id != user_id:
        raise ValueError("对话不存在或无权访问")

    normalized_title = " ".join(str(title or "").split()).strip()
    if not normalized_title:
        raise ValueError("对话标题不能为空")

    renamed_chat = await repo_rename_chat(db, chat_id, normalized_title)
    if not renamed_chat:
        raise ValueError("对话不存在或无权访问")
    return renamed_chat
