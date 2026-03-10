"""Profile service — user profile CRUD, behavior stats, and role-based defense."""
import json
import logging
from typing import Optional

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models.chat import Chat, ChatMessage
from app.db.models.detection_history import DetectionHistory
from app.db.models.evidence import Evidence
from app.db.models.fact_check_history import FactCheckHistory
from app.db.models.report import Report
from app.db.models.user_profile import UserProfile
from app.schemas.profile import (
    BehaviorStats,
    ProfileData,
    RecentChat,
    RecentDetection,
    RecentEvidence,
    RecentReport,
    RoleDefenseStrategy,
    UserProfileUpdate,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Role-based defense knowledge (offline, no LLM needed)
# ---------------------------------------------------------------------------
_ROLE_DEFENSE: dict[str, dict] = {
    "青少年": {
        "risk_summary": "青少年群体是网络游戏充值诈骗、虚假追星、社交软件交友陷阱的高发对象。",
        "high_risk_types": ["游戏充值诈骗", "虚假追星打榜", "社交交友陷阱", "刷单返利"],
        "defense_tips": [
            "不在任何非官方渠道充值游戏货币，不相信'低价代充'",
            "追星打榜不需要向陌生人转账，任何以明星名义要钱的都是骗子",
            "网上交友不要轻易透露家庭住址、学校、父母工作等信息",
            "遇到'刷单赚零花钱'的邀请立即拒绝，这是违法行为",
            "收到可疑链接先截图给父母或老师确认，不要自行点击",
        ],
    },
    "青年": {
        "risk_summary": "青年群体面临刷单返利、杀猪盘、虚假招聘、网贷套路等高频诈骗类型。",
        "high_risk_types": ["刷单返利", "杀猪盘", "虚假招聘", "网贷套路", "投资理财"],
        "defense_tips": [
            "任何要求先垫资再返利的'兼职'都是刷单诈骗",
            "网恋对象引导你投资或借钱时，极大概率是'杀猪盘'",
            "正规招聘不会收取培训费、服装费、押金等任何费用",
            "警惕'低息贷款'和'以贷养贷'，非正规网贷利滚利会失控",
            "投资理财只选正规持牌机构，'稳赚不赔'都是骗局",
        ],
    },
    "中年": {
        "risk_summary": "中年群体是投资理财诈骗、冒充公检法、保健品骗局的主要受害人群。",
        "high_risk_types": ["投资理财", "冒充公检法", "冒充领导", "保健品骗局"],
        "defense_tips": [
            "不相信任何'内部渠道''高额回报'的投资推荐，正规理财有备案",
            "公检法机关不会通过电话办案，更不会要求你转账到'安全账户'",
            "收到'领导'要求转账的微信或短信，务必电话确认本人",
            "网络上推荐的保健品大多为三无产品，购买药品请去正规医院或药店",
            "家庭重要资金操作前与家人商量，不要在压力下仓促转账",
        ],
    },
    "老年": {
        "risk_summary": "老年群体最易受电信诈骗、保健养生骗局、冒充亲友求助等手段侵害。",
        "high_risk_types": ["电信诈骗", "保健养生骗局", "冒充亲友", "假冒公检法", "中奖诈骗"],
        "defense_tips": [
            "接到陌生电话不要慌张，特别是说'涉及案件'的一律先挂断",
            "任何电话或短信让你转账的，先打给子女或110确认",
            "免费送鸡蛋、送体检、送旅游的'讲座'大多是保健品骗局",
            "不下载陌生人推荐的APP，不给陌生人开启屏幕共享",
            "银行卡密码、验证码是最后防线，任何人索要都不能给",
        ],
    },
}

_OCCUPATION_TIPS: dict[str, list[str]] = {
    "学生": [
        "校园贷是高利贷陷阱，正规助学贷只通过学校渠道办理",
        "不参与任何'帮忙接收转账'的行为，这可能让你成为帮信罪嫌疑人",
    ],
    "上班族": [
        "收到'老板/财务'要求紧急转账的信息，务必当面或电话核实",
        "不在工作邮箱点击来源不明的链接，警惕钓鱼邮件",
    ],
    "自由职业": [
        "接单平台之外的私下交易没有保障，不要提前垫付大额资金",
        "警惕'高薪兼职'信息，正规平台有评价体系和担保机制",
    ],
    "退休": [
        "投资理财一定要通过银行等正规渠道，不听信'高回报'电话推荐",
        "对以'政府补贴''养老金调整'为由索要个人信息的来电保持警惕",
    ],
}

_GENDER_TIPS: dict[str, list[str]] = {
    "女": [
        "警惕'甜蜜陷阱'：网恋对象过快表白并引导投资是杀猪盘典型特征",
        "购物退款请在官方平台操作，不要扫陌生人发来的二维码",
    ],
    "男": [
        "警惕'美女荐股'和'交友平台充值'，这些是常见诈骗入口",
        "网络赌博十赌十输，不要相信'必赢策略'和'内部消息'",
    ],
}


def build_role_defense(profile: ProfileData) -> RoleDefenseStrategy:
    """Build role-specific defense strategy based on user profile (no LLM needed)."""
    age = profile.age_group or "青年"
    base = _ROLE_DEFENSE.get(age, _ROLE_DEFENSE["青年"])

    role_label_parts = []
    if profile.age_group:
        role_label_parts.append(profile.age_group)
    if profile.gender and profile.gender != "保密":
        role_label_parts.append(profile.gender + "性")
    if profile.occupation:
        role_label_parts.append(profile.occupation)
    role_label = " · ".join(role_label_parts) if role_label_parts else "通用用户"

    tips = list(base["defense_tips"])

    # Layer on occupation-specific tips
    if profile.occupation and profile.occupation in _OCCUPATION_TIPS:
        tips.extend(_OCCUPATION_TIPS[profile.occupation])

    # Layer on gender-specific tips
    if profile.gender and profile.gender in _GENDER_TIPS:
        tips.extend(_GENDER_TIPS[profile.gender])

    return RoleDefenseStrategy(
        role_label=role_label,
        risk_summary=base["risk_summary"],
        high_risk_types=base["high_risk_types"],
        defense_tips=tips[:8],
    )


# ---------------------------------------------------------------------------
# Profile CRUD
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Behavior stats with activity details
# ---------------------------------------------------------------------------

async def get_behavior_stats(
    db: AsyncSession, username: str, user_id: int
) -> BehaviorStats:
    # --- detection ---
    det_count = await db.scalar(
        select(func.count()).select_from(DetectionHistory).where(
            DetectionHistory.user_id == user_id
        )
    ) or 0

    recent_det_rows = (
        await db.execute(
            select(DetectionHistory)
            .where(DetectionHistory.user_id == user_id)
            .order_by(DetectionHistory.created_at.desc())
            .limit(5)
        )
    ).scalars().all()
    recent_detections = [
        RecentDetection(
            detection_type=r.detection_type,
            risk_level=r.risk_level,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in recent_det_rows
    ]

    # --- fact check ---
    fc_count = await db.scalar(
        select(func.count()).select_from(FactCheckHistory).where(
            FactCheckHistory.checked_by == username
        )
    ) or 0

    # --- reports (with detail list) ---
    rp_count = await db.scalar(
        select(func.count()).select_from(Report).where(
            Report.reported_by == username
        )
    ) or 0

    recent_rp_rows = (
        await db.execute(
            select(Report)
            .where(Report.reported_by == username)
            .order_by(Report.created_at.desc())
            .limit(10)
        )
    ).scalars().all()
    recent_reports = [
        RecentReport(
            report_id=r.report_id,
            type=r.type,
            description=r.description[:80] if r.description else "",
            status=r.status,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in recent_rp_rows
    ]

    # --- evidence (with detail list) ---
    ev_count = await db.scalar(
        select(func.count()).select_from(Evidence).where(
            Evidence.submitted_by == username
        )
    ) or 0

    recent_ev_rows = (
        await db.execute(
            select(Evidence)
            .where(Evidence.submitted_by == username)
            .order_by(Evidence.submitted_at.desc())
            .limit(10)
        )
    ).scalars().all()
    recent_evidences = [
        RecentEvidence(
            id=e.id,
            news_id=e.news_id,
            content=e.content[:80] if e.content else "",
            status=e.status,
            submitted_at=e.submitted_at.isoformat() if e.submitted_at else "",
        )
        for e in recent_ev_rows
    ]

    # --- chats (with detail list) ---
    ch_count = await db.scalar(
        select(func.count()).select_from(Chat).where(
            Chat.user_id == user_id
        )
    ) or 0

    recent_ch_rows = (
        await db.execute(
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(Chat.created_at.desc())
            .limit(10)
        )
    ).scalars().all()
    recent_chats = []
    for c in recent_ch_rows:
        msg_count = await db.scalar(
            select(func.count()).select_from(ChatMessage).where(
                ChatMessage.chat_id == c.id
            )
        ) or 0
        recent_chats.append(RecentChat(
            id=str(c.id),
            title=c.title or "对话",
            message_count=msg_count,
            created_at=c.created_at.isoformat() if c.created_at else "",
        ))

    return BehaviorStats(
        detection_count=det_count,
        fact_check_count=fc_count,
        report_count=rp_count,
        evidence_count=ev_count,
        chat_count=ch_count,
        recent_detections=recent_detections,
        recent_reports=recent_reports,
        recent_evidences=recent_evidences,
        recent_chats=recent_chats,
    )


# ---------------------------------------------------------------------------
# LLM-based personalized suggestions
# ---------------------------------------------------------------------------

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
        "生成 5 条个性化的反诈防护建议。\n\n"
        "要求：\n"
        "- 每条建议必须针对该用户的角色特点（年龄、性别、职业）\n"
        "- 结合行为数据：如果检测次数少，建议多使用检测功能；如果举报次数多，肯定积极行为\n"
        "- 如果有关注领域，优先围绕这些领域给建议\n"
        "- 每条一句话，简洁实用\n\n"
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


# ---------------------------------------------------------------------------
# Detection history recording (called from detection endpoints)
# ---------------------------------------------------------------------------

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
