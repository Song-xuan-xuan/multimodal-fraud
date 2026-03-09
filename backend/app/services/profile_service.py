"""Profile service — user profile CRUD and behavior stats."""
import json
import logging
from typing import Optional

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models.chat import Chat
from app.db.models.detection_history import DetectionHistory
from app.db.models.evidence import Evidence
from app.db.models.fact_check_history import FactCheckHistory
from app.db.models.report import Report
from app.db.models.user_profile import UserProfile
from app.schemas.profile import (
    BehaviorStats,
    ProfileData,
    RecentDetection,
    UserProfileUpdate,
)

logger = logging.getLogger(__name__)


async def get_or_create_profile(db: AsyncSession, user_id: int) -> UserProfile:
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        await db.flush()
    return profile


async def update_profile(
    db: AsyncSession, user_id: int, data: UserProfileUpdate
) -> UserProfile:
    profile = await get_or_create_profile(db, user_id)
    update_data = data.model_dump(exclude_none=True)
    if "concern_tags" in update_data:
        update_data["concern_tags"] = json.dumps(
            update_data["concern_tags"], ensure_ascii=False
        )
    for key, value in update_data.items():
        setattr(profile, key, value)
    await db.flush()
    return profile


def _profile_to_data(profile: UserProfile) -> ProfileData:
    tags: list[str] = []
    if profile.concern_tags:
        try:
            tags = json.loads(profile.concern_tags)
        except (json.JSONDecodeError, TypeError):
            tags = []
    return ProfileData(
        age_group=profile.age_group,
        gender=profile.gender,
        occupation=profile.occupation,
        region=profile.region,
        concern_tags=tags,
    )


async def get_behavior_stats(
    db: AsyncSession, username: str, user_id: int
) -> BehaviorStats:
    # detection count
    det_count = await db.scalar(
        select(func.count()).select_from(DetectionHistory).where(
            DetectionHistory.user_id == user_id
        )
    ) or 0

    # recent 5 detections
    recent_rows = (
        await db.execute(
            select(DetectionHistory)
            .where(DetectionHistory.user_id == user_id)
            .order_by(DetectionHistory.created_at.desc())
            .limit(5)
        )
    ).scalars().all()
    recent = [
        RecentDetection(
            detection_type=r.detection_type,
            risk_level=r.risk_level,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in recent_rows
    ]

    # fact check count
    fc_count = await db.scalar(
        select(func.count()).select_from(FactCheckHistory).where(
            FactCheckHistory.checked_by == username
        )
    ) or 0

    # report count
    rp_count = await db.scalar(
        select(func.count()).select_from(Report).where(
            Report.reported_by == username
        )
    ) or 0

    # evidence count
    ev_count = await db.scalar(
        select(func.count()).select_from(Evidence).where(
            Evidence.submitted_by == username
        )
    ) or 0

    # chat count
    ch_count = await db.scalar(
        select(func.count()).select_from(Chat).where(
            Chat.user_id == user_id
        )
    ) or 0

    return BehaviorStats(
        detection_count=det_count,
        fact_check_count=fc_count,
        report_count=rp_count,
        evidence_count=ev_count,
        chat_count=ch_count,
        recent_detections=recent,
    )


async def generate_suggestions(
    profile: ProfileData, stats: BehaviorStats
) -> list[str]:
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        return _fallback_suggestions(profile)

    profile_desc = (
        f"年龄段: {profile.age_group or '未设置'}, "
        f"性别: {profile.gender or '未设置'}, "
        f"职业: {profile.occupation or '未设置'}, "
        f"地区: {profile.region or '未设置'}, "
        f"关注领域: {', '.join(profile.concern_tags) if profile.concern_tags else '未设置'}"
    )
    stats_desc = (
        f"检测次数: {stats.detection_count}, "
        f"核查次数: {stats.fact_check_count}, "
        f"举报次数: {stats.report_count}, "
        f"社区贡献: {stats.evidence_count}, "
        f"AI咨询次数: {stats.chat_count}"
    )

    prompt = (
        "你是一个专业的反诈防护顾问。根据以下用户画像和行为数据，"
        "生成 5 条个性化的反诈防护建议。每条建议用一句话表达，简洁实用。\n\n"
        f"用户画像: {profile_desc}\n"
        f"行为数据: {stats_desc}\n\n"
        "请直接返回 5 条建议，每条一行，不要加编号或前缀。"
    )

    api_url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 512,
    }
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(api_url, json=payload, headers=headers)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            lines = [
                line.strip().lstrip("0123456789.、·- ")
                for line in content.strip().splitlines()
                if line.strip()
            ]
            return lines[:5] if lines else _fallback_suggestions(profile)
    except Exception as e:
        logger.error("generate_suggestions error: %s", e)
        return _fallback_suggestions(profile)


def _fallback_suggestions(profile: ProfileData) -> list[str]:
    base = [
        "不要向陌生人透露短信验证码或银行密码",
        "接到自称公检法的电话要求转账时，请立即挂断并报警",
        "网购退款请通过官方渠道操作，不要点击不明链接",
        "高收益投资承诺多为骗局，理性投资防范风险",
        "遇到可疑信息，可使用本平台的检测功能进行核验",
    ]
    if profile.concern_tags:
        tag_tips: dict[str, str] = {
            "电信诈骗": "警惕陌生来电，不轻信任何要求转账的理由",
            "投资理财": "正规投资平台有监管备案，警惕'稳赚不赔'的承诺",
            "网购退款": "退款请在电商平台内操作，不下载陌生APP",
            "杀猪盘": "网恋对象要求投资或借钱时，极大概率是诈骗",
            "冒充公检法": "公检法不会通过电话要求转账到'安全账户'",
            "网络赌博": "网络赌博必输，远离一切赌博平台",
            "刷单返利": "刷单本身违法，任何要求先垫资的刷单都是诈骗",
            "虚假招聘": "正规招聘不收费，要求交培训费的一律是骗局",
        }
        for tag in profile.concern_tags:
            if tag in tag_tips and tag_tips[tag] not in base:
                base.append(tag_tips[tag])
    return base[:5]


async def record_detection(
    db: AsyncSession,
    user_id: int,
    detection_type: str,
    risk_level: Optional[str] = None,
) -> None:
    record = DetectionHistory(
        user_id=user_id,
        detection_type=detection_type,
        risk_level=risk_level,
    )
    db.add(record)
    await db.flush()
