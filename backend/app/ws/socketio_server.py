# Integration: In main.py, add:
#   from app.ws.socketio_server import socket_app
#   app.mount("/ws", socket_app)

import logging
from urllib.parse import parse_qs

import socketio

logger = logging.getLogger(__name__)

EVENT_CONTRACT_VERSION = "v1"
EVENT_ALERT_CREATED = "alert_created"
EVENT_REVIEW_UPDATED = "review_updated"

# 创建 ASGI 兼容的 Socket.IO 服务器
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
)

# 创建 ASGI 应用（用于挂载到 FastAPI）
socket_app = socketio.ASGIApp(sio)


async def _emit_to_user(username: str, event_name: str, payload: dict) -> None:
    room = f"user:{username}"
    await sio.emit(event_name, payload, room=room)


async def push_alert_created_event(payload: dict) -> None:
    """推送警报创建事件（契约版本 v1）。"""
    await _emit_to_user(payload["recipient_username"], EVENT_ALERT_CREATED, payload)


async def push_review_updated_event(payload: dict) -> None:
    """推送审核更新事件（契约版本 v1）。"""
    await _emit_to_user(payload["recipient_username"], EVENT_REVIEW_UPDATED, payload)


@sio.event
async def connect(sid, environ):
    query = parse_qs(environ.get("QUERY_STRING", ""))
    username = (query.get("username") or [""])[0].strip()
    if username:
        room = f"user:{username}"
        await sio.enter_room(sid, room)
        logger.info("Client connected: %s joined %s", sid, room)
    else:
        logger.info("Client connected: %s", sid)


@sio.event
async def disconnect(sid):
    logger.info("Client disconnected: %s", sid)


@sio.on("new_message")
async def handle_new_message(sid, data):
    """处理论坛新消息，广播给所有客户端"""
    logger.info("New message from %s", sid)
    await sio.emit("new_message", data)
