import base64
import json
import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def analyze_image_fraud_risk(image_bytes: bytes, filename: str = '') -> dict[str, Any]:
    settings = get_settings()

    api_key = settings.VISION_API_KEY or settings.OPENAI_API_KEY
    base_url = settings.VISION_BASE_URL or settings.OPENAI_BASE_URL
    model = settings.VISION_MODEL or settings.OPENAI_MODEL
    temperature = settings.VISION_TEMPERATURE

    if not api_key or not base_url or not model:
        raise RuntimeError('未配置视觉分析 API')

    mime = 'image/png'
    lower = filename.lower()
    if lower.endswith('.jpg') or lower.endswith('.jpeg'):
        mime = 'image/jpeg'
    elif lower.endswith('.webp'):
        mime = 'image/webp'

    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    data_url = f'data:{mime};base64,{image_b64}'

    system_prompt = (
        '你是反诈视觉分析助手。请判断图片是否涉及诈骗场景，识别截图中的关键文字，'
        '输出风险等级、风险分数、诈骗类型、OCR文本、命中信号、摘要和结论。'
        '必须只返回 JSON，不要输出其他说明。'
    )
    user_prompt = (
        '请分析这张图片是否是诈骗相关截图，如转账、收款、贷款、客服退款、解冻、保证金、验证码、'
        '共享屏幕诱导等场景。返回 JSON，字段包括：risk_level, risk_score, scene_type, '
        'fraud_types, ocr_text, matched_signals, summary, conclusion。'
    )

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': user_prompt},
                    {'type': 'image_url', 'image_url': {'url': data_url}},
                ],
            },
        ],
        'temperature': temperature,
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    url = f"{base_url.rstrip('/')}/chat/completions"

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        body = response.json()

    content = body['choices'][0]['message']['content']
    if not isinstance(content, str):
        raise RuntimeError('视觉模型未返回文本结果')

    content = content.strip()
    if content.startswith('```'):
        content = content.strip('`')
        if content.startswith('json'):
            content = content[4:].strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        logger.error('视觉模型返回非 JSON: %s', content[:500])
        raise RuntimeError('视觉模型未返回合法 JSON') from exc

    return {
        'risk_level': parsed.get('risk_level', 'low'),
        'risk_score': float(parsed.get('risk_score', 0.0) or 0.0),
        'scene_type': parsed.get('scene_type', ''),
        'fraud_types': parsed.get('fraud_types', []) or [],
        'ocr_text': parsed.get('ocr_text', '') or '',
        'matched_signals': parsed.get('matched_signals', []) or [],
        'summary': parsed.get('summary', '') or '',
        'conclusion': parsed.get('conclusion', '') or '',
        'label': parsed.get('scene_type', '') or parsed.get('risk_level', ''),
    }
