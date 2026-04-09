"""Guardian email notification service backed by Resend."""

import logging
from typing import Iterable

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

RESEND_EMAIL_API_URL = "https://api.resend.com/emails"


def mask_email_address(email: str) -> str:
    normalized = (email or "").strip()
    if "@" not in normalized:
        return ""

    local_part, domain = normalized.split("@", 1)
    if len(local_part) <= 2:
        masked_local = (local_part[:1] or "*") + "***"
    else:
        masked_local = local_part[:2] + "***"
    return f"{masked_local}@{domain}"


def build_guardian_alert_text(
    *,
    guardian_name: str,
    username: str,
    fraud_types: Iterable[str],
    summary: str,
    recommended_actions: Iterable[str],
) -> str:
    fraud_summary = "、".join([item for item in fraud_types if item]) or "可疑诈骗风险"
    actions = [item for item in recommended_actions if item]
    salutation = f"{guardian_name}：" if guardian_name else "监护人："
    action_lines = "\n".join(f"{index + 1}. {item}" for index, item in enumerate(actions[:5]))
    if not action_lines:
        action_lines = "1. 立即电话联系当事人\n2. 暂停一切转账、验证码提供和屏幕共享操作"

    return (
        f"{salutation}\n\n"
        f"系统检测到用户 {username} 当前遭遇高风险诈骗场景，疑似涉及：{fraud_summary}。\n\n"
        f"风险摘要：{summary}\n\n"
        "建议你立刻执行以下动作：\n"
        f"{action_lines}\n\n"
        "请优先通过电话直接联系当事人，确认其是否正在转账、提供验证码或共享屏幕。"
    )


def _build_skip_result(message: str) -> dict:
    return {
        "attempted": False,
        "sent": False,
        "status": "skipped",
        "message": message,
        "recipient_masked": "",
    }


async def send_guardian_alert_email(
    *,
    guardian_name: str,
    guardian_email: str,
    username: str,
    fraud_types: Iterable[str],
    summary: str,
    recommended_actions: Iterable[str],
) -> dict:
    settings = get_settings()
    api_key = (settings.RESEND_API_KEY or "").strip()
    from_email = (settings.RESEND_FROM_EMAIL or "").strip()
    from_name = (settings.RESEND_FROM_NAME or "反诈智能助手").strip() or "反诈智能助手"
    recipient = (guardian_email or "").strip()

    if not api_key or not from_email:
        return _build_skip_result("未配置 Resend 邮件服务，已跳过监护人提醒。")
    if not recipient:
        return _build_skip_result("未配置监护人邮箱，已跳过监护人提醒。")

    payload = {
        "from": f"{from_name} <{from_email}>",
        "to": [recipient],
        "subject": "【高风险预警】请立即联系被监护人",
        "text": build_guardian_alert_text(
            guardian_name=guardian_name,
            username=username,
            fraud_types=fraud_types,
            summary=summary,
            recommended_actions=recommended_actions,
        ),
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(RESEND_EMAIL_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info("Guardian alert email sent for %s, resend_id=%s", username, data.get("id", ""))
            return {
                "attempted": True,
                "sent": True,
                "status": "sent",
                "message": "监护人提醒邮件已发送。",
                "recipient_masked": mask_email_address(recipient),
            }
    except Exception as exc:
        logger.error("Guardian alert email failed for %s: %s", username, exc)
        return {
            "attempted": True,
            "sent": False,
            "status": "failed",
            "message": f"监护人提醒邮件发送失败: {exc}",
            "recipient_masked": mask_email_address(recipient),
        }
