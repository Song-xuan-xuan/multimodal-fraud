import json
import logging
import random
import re
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import httpx

from app.core.config import get_settings
from app.schemas.education import (
    EducationCoachResponse,
    EducationCase,
    EducationQuestion,
    EducationQuestionPublic,
    EducationStage,
    EducationStageDetailResponse,
    SubmitTestDetail,
    SubmitTestResponse,
    TrendPoint,
    WeaknessItem,
)
from app.services.rag_service import retrieve_relevant_sources

logger = logging.getLogger(__name__)

_STAGES: list[EducationStage] = [
    EducationStage(stage_id="beginner", name="基础识诈", description="识别高频诈骗入口、紧急诱导和信息核验的第一步。"),
    EducationStage(stage_id="intermediate", name="情境拆解", description="学习从转账诱导、关系操控和平台伪装中识别风险。"),
    EducationStage(stage_id="advanced", name="综合研判", description="面对 AI 合成、跨平台协同和复合型诈骗时做出判断。"),
]

_STAGE_DETAILS: dict[str, EducationStageDetailResponse] = {
    "beginner": EducationStageDetailResponse(
        stage_id="beginner",
        name="基础识诈",
        description="先建立正确的反诈直觉，学会在陌生链接、紧急通知、验证码和付款要求前停一步。",
        cases=[
            EducationCase(
                case_id="b1",
                title="冒充客服退款",
                summary="骗子冒充电商客服，以商品质量问题为由诱导你点击退款链接。",
                analysis="正规退款不会要求你离开平台，也不会让你下载会议软件或共享屏幕。",
                tips=["先回到原购物平台核验订单", "拒绝屏幕共享", "验证码只输入在官方页面"],
            ),
            EducationCase(
                case_id="b2",
                title="群聊紧急通知截图",
                summary="群里流传某地封控截图，看起来像官方群消息，但没有正式落款和发布日期。",
                analysis="截图类消息最容易断章取义，先核验发布时间、发布主体和官方通报。",
                tips=["先查权威媒体和政府账号", "警惕只给截图不给链接", "不盲目转发"],
            ),
            EducationCase(
                case_id="b3",
                title="验证码协助登录",
                summary="对方以实名认证、取消扣费、平台风控为由索要短信验证码。",
                analysis="验证码本质上就是账户控制权，任何索要验证码的说辞都应默认高风险。",
                tips=["验证码绝不口述", "先挂断再联系官方", "核查账户登录记录"],
            ),
        ],
    ),
    "intermediate": EducationStageDetailResponse(
        stage_id="intermediate",
        name="情境拆解",
        description="理解诈骗如何组合身份伪装、利益承诺和时间压力，训练自己拆解情境的能力。",
        cases=[
            EducationCase(
                case_id="i1",
                title="刷单返利连环诱导",
                summary="先返小额佣金建立信任，再引导大额垫资和连续任务。",
                analysis="刷单骗局靠阶段性返利来制造可持续盈利错觉，本质上是不断提高你的沉没成本。",
                tips=["只要先垫资就是高危信号", "不要相信导师带单", "及时保存聊天和流水"],
            ),
            EducationCase(
                case_id="i2",
                title="虚假征信修复",
                summary="自称金融平台客服，声称你的征信异常，需要按指引操作才能撤销。",
                analysis="骗子会用专业术语制造恐慌，再诱导贷款转账或共享屏幕完成远程操控。",
                tips=["征信问题通过官方银行渠道核验", "拒绝共享屏幕", "不要按指令贷款转账"],
            ),
            EducationCase(
                case_id="i3",
                title="游戏交易中介担保",
                summary="骗子伪装成玩家或中介，要求脱离平台私下交易并支付保证金。",
                analysis="离开平台就失去申诉保障，所谓担保链接和客服页面常是伪造站点。",
                tips=["只在官方平台交易", "不扫陌生二维码", "不提前支付保证金"],
            ),
        ],
    ),
    "advanced": EducationStageDetailResponse(
        stage_id="advanced",
        name="综合研判",
        description="训练多线索整合能力，在复杂诈骗剧本中识别核心风险和正确处置方式。",
        cases=[
            EducationCase(
                case_id="a1",
                title="AI 语音冒充亲友",
                summary="骗子用合成语音伪装成家人求助，强调手机损坏、事情紧急，只能先打钱。",
                analysis="AI 语音会提升真实性，但转账逻辑、沟通环境和验证机制仍然可以被拆穿。",
                tips=["改用视频或已知号码回拨", "设置家庭核验暗号", "延迟支付并联系其他亲属"],
            ),
            EducationCase(
                case_id="a2",
                title="投资群控盘诱导",
                summary="通过社群包装老师、学员和盈利截图，逐步把受害者导入假投资平台。",
                analysis="这类骗局的关键是用群体氛围压低警惕，再用小额盈利诱导更大投入。",
                tips=["平台资质先核验", "盈利截图不可信", "提现失败即刻止损并报警"],
            ),
            EducationCase(
                case_id="a3",
                title="跨平台钓鱼链路",
                summary="短信引流到社交平台，再发送假客服页面和伪造支付链接。",
                analysis="跨平台切换是为了绕开原平台风控，你需要盯住最初需求是否合理、最终动作是否涉及转账或授权。",
                tips=["不随意跨平台沟通", "检查域名和证书", "支付前回到原平台核验"],
            ),
        ],
    ),
}

_STATIC_QUESTION_BANK: list[EducationQuestion] = [
    EducationQuestion(
        question_id="sq_beginner_01",
        question="陌生客服来电称你的会员即将自动扣费，要求你立刻下载会议软件操作，最合理的处理方式是？",
        options=["按照对方要求共享屏幕", "先挂断电话，再从官方 App 或客服电话核验", "让对方远程帮你操作", "把验证码发给对方确认"],
        answer=1,
        explanation="正规平台不会要求用户下载会议软件或共享屏幕处理扣费问题，正确做法是回到官方渠道核验。",
        category="冒充客服",
        difficulty="beginner",
        fraud_type="虚假客服退款",
        source_type="static",
    ),
    EducationQuestion(
        question_id="sq_beginner_02",
        question="看到“紧急通知”截图时，第一步最合理的是？",
        options=["立即转发提醒亲友", "核验发布主体和来源", "相信转发量最多的版本", "等待自媒体解读"],
        answer=1,
        explanation="截图内容最容易被断章取义，核验发布主体和原始来源是最基础的步骤。",
        category="信息核验",
        difficulty="beginner",
        fraud_type="虚假通知",
        source_type="static",
    ),
    EducationQuestion(
        question_id="sq_beginner_03",
        question="下列哪一项最可能是诈骗消息中的高危信号？",
        options=["提醒你保管个人信息", "要求你在几分钟内完成转账", "建议你去官方渠道核实", "附带完整官方公告链接"],
        answer=1,
        explanation="利用时间压力催促转账是典型诈骗特征，目的就是阻止你思考和核验。",
        category="高危信号",
        difficulty="beginner",
        fraud_type="通用诈骗话术",
        source_type="static",
    ),
    EducationQuestion(
        question_id="sq_beginner_04",
        question="判断一条新闻是否旧闻翻炒，最关键的是？",
        options=["看标题是否耸动", "看评论区态度", "核对发布时间和事件时间", "看转发平台"],
        answer=2,
        explanation="旧闻翻炒最常见的手法就是故意模糊发布时间，让旧事件伪装成最新信息。",
        category="信息核验",
        difficulty="beginner",
        fraud_type="旧闻翻炒",
        source_type="static",
    ),
    EducationQuestion(
        question_id="sq_intermediate_01",
        question="刷单返利骗局中，哪一步最容易让受害者掉入更深陷阱？",
        options=["第一次任务返利成功", "对方发送平台首页截图", "客服回复速度很快", "任务要求截图留档"],
        answer=0,
        explanation="先返小额佣金是刷单骗局的关键设计，用来制造“真能赚钱”的错觉并诱导更大额垫资。",
        category="刷单返利",
        difficulty="intermediate",
        fraud_type="兼职刷单",
        source_type="static",
    ),
    EducationQuestion(
        question_id="sq_intermediate_02",
        question="对方称你的征信异常，需要你配合“刷流水”才能消除记录，这类说法最大的风险是什么？",
        options=["可能泄露通讯录", "会诱导你贷款并把钱转走", "会降低手机性能", "会导致社交账号封号"],
        answer=1,
        explanation="虚假征信修复骗局通常会引导受害者贷款、转账或共享屏幕，本质是骗钱。",
        category="征信修复",
        difficulty="intermediate",
        fraud_type="虚假征信",
        source_type="static",
    ),
    EducationQuestion(
        question_id="sq_intermediate_03",
        question="游戏账号交易时，对方要求你离开官方平台，通过“担保客服”私下交易，最合理的判断是？",
        options=["对方更专业，可信度更高", "这是为了节省手续费，可以接受", "离开官方平台意味着风险显著上升", "只要担保客服头像正规就没问题"],
        answer=2,
        explanation="脱离官方平台就失去平台担保和申诉链路，是游戏交易骗局的高风险信号。",
        category="平台外交易",
        difficulty="intermediate",
        fraud_type="游戏交易诈骗",
        source_type="static",
    ),
    EducationQuestion(
        question_id="sq_intermediate_04",
        question="面对互相矛盾的两条消息，应优先采用哪种策略？",
        options=["选择更符合直觉的一条", "参考熟人意见", "交叉查证权威渠道", "等待热度下降"],
        answer=2,
        explanation="交叉查证权威渠道能有效降低被伪造截图、情绪化信息误导的概率。",
        category="交叉验证",
        difficulty="intermediate",
        fraud_type="信息误导",
        source_type="static",
    ),
    EducationQuestion(
        question_id="sq_advanced_01",
        question="接到“家人”语音求助说自己手机坏了、只能借别人手机联系你并急需转账，最可靠的核验方式是什么？",
        options=["直接相信语音内容", "让对方继续发语音说明情况", "通过你已知的号码或其他家人再次核验", "先转一半再核实"],
        answer=2,
        explanation="AI 语音或冒充语音都可能伪造身份，必须切换到你已知可信的联系方式重新核验。",
        category="身份核验",
        difficulty="advanced",
        fraud_type="AI 语音冒充",
        source_type="static",
    ),
    EducationQuestion(
        question_id="sq_advanced_02",
        question="投资群里先让你小额盈利、再鼓励你加大投入，这种设计最核心的诈骗机制是？",
        options=["提高平台知名度", "制造信任并放大沉没成本", "测试用户网速", "方便后台统计收益"],
        answer=1,
        explanation="先让你尝到甜头再加码，是典型投资诈骗的心理操控手法。",
        category="投资理财",
        difficulty="advanced",
        fraud_type="投资理财诈骗",
        source_type="static",
    ),
    EducationQuestion(
        question_id="sq_advanced_03",
        question="短信把你引导到社交软件，再由“客服”发支付链接，这种跨平台流程最大的目的通常是什么？",
        options=["节省沟通时间", "绕开原平台风控和用户警惕", "方便保存聊天记录", "提高客服服务质量"],
        answer=1,
        explanation="跨平台切换是常见的风控绕过手法，目的是让你脱离原平台的安全约束。",
        category="跨平台诱导",
        difficulty="advanced",
        fraud_type="钓鱼链接诈骗",
        source_type="static",
    ),
    EducationQuestion(
        question_id="sq_advanced_04",
        question="如果一个案例同时出现“高收益承诺”“导师带单”“提现受限”三个信号，你应优先把它判断为哪类高危场景？",
        options=["普通广告营销", "投资理财诈骗", "售后纠纷", "二手交易沟通不畅"],
        answer=1,
        explanation="这三个信号叠加，基本就是投资理财诈骗的典型剧本。",
        category="复合信号识别",
        difficulty="advanced",
        fraud_type="投资理财诈骗",
        source_type="static",
    ),
]

_STAGE_DIFFICULTY_MAP = {
    "beginner": {"beginner"},
    "intermediate": {"beginner", "intermediate"},
    "advanced": {"intermediate", "advanced"},
}

_GENERATED_CACHE_FILE = "education_generated_questions.json"
_GENERATED_CACHE_LIMIT = 120
_TEST_HISTORY_FILE = "education_test_history.json"
_TEST_HISTORY_LIMIT = 200
_FRAUD_SUGGESTIONS: dict[str, str] = {
    "投资理财诈骗": "遇到高收益承诺时先核验平台资质，优先验证提现链路。",
    "兼职刷单": "凡是先垫资、连环任务、导师带单都默认高风险。",
    "虚假客服退款": "退款只走原平台，不下载会议软件，不共享屏幕。",
    "虚假征信": "征信异常只通过银行或官方机构核验，不按指令贷款转账。",
    "AI 语音冒充": "转账前必须二次核验身份，优先视频/已知号码回拨。",
    "钓鱼链接诈骗": "不要跨平台跳转支付，检查域名和证书再操作。",
    "游戏交易诈骗": "账号交易只走官方担保，不私下支付保证金。",
}
_COMMON_MISTAKE_LIBRARY: dict[str, str] = {
    "虚假客服退款": "把“紧急退款/取消扣费”当成必须立刻处理，忽略了官方渠道核验。",
    "兼职刷单": "被小额返利建立信任后继续加码，忽略先垫资就是高危信号。",
    "虚假征信": "被“征信异常”恐慌驱动，按对方指令进行贷款或转账。",
    "AI 语音冒充": "只凭语音内容确认身份，没有进行二次联系核验。",
    "钓鱼链接诈骗": "跨平台跳转后直接点击链接，未校验域名真实性。",
    "投资理财诈骗": "把“导师带单+高收益”当作专业建议，忽略提现验证。",
}


def get_stages() -> list[EducationStage]:
    return _STAGES


def get_stage_detail(stage_id: str) -> EducationStageDetailResponse | None:
    return _STAGE_DETAILS.get(stage_id)


def _cache_path() -> Path:
    settings = get_settings()
    return settings.data_path / _GENERATED_CACHE_FILE


def _history_path() -> Path:
    settings = get_settings()
    return settings.data_path / _TEST_HISTORY_FILE


def _load_test_history() -> list[dict]:
    history_path = _history_path()
    if not history_path.exists():
        return []

    try:
        payload = json.loads(history_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.warning("Failed to read education test history from %s", history_path)
        return []

    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def _persist_test_history(items: list[dict]) -> None:
    history_path = _history_path()
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(
        json.dumps(items[-_TEST_HISTORY_LIMIT:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _append_test_history(score: float, passed: bool, username: str) -> list[dict]:
    history = _load_test_history()
    history.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "score": round(float(score), 2),
            "passed": bool(passed),
            "username": username or "anonymous",
        }
    )
    _persist_test_history(history)
    return history


def _build_recent_trend(history: list[dict], username: str, limit: int = 3) -> list[TrendPoint]:
    points: list[TrendPoint] = []
    user_history = [item for item in history if str(item.get("username", "anonymous")) == (username or "anonymous")]
    for item in user_history[-limit:]:
        try:
            points.append(
                TrendPoint(
                    timestamp=str(item.get("timestamp", "")),
                    score=round(float(item.get("score", 0.0)), 2),
                    passed=bool(item.get("passed", False)),
                )
            )
        except (TypeError, ValueError):
            continue
    return points


def _calculate_trend_delta(points: list[TrendPoint]) -> float | None:
    if len(points) < 2:
        return None
    return round(points[-1].score - points[-2].score, 2)


def _default_learning_objective(recommended_stage: str) -> str:
    if recommended_stage == "beginner":
        return "建立基础反诈动作：先核验来源，再处理资金操作。"
    if recommended_stage == "intermediate":
        return "强化情境拆解能力：识别诱导话术与错误处置顺序。"
    return "提升综合研判能力：在复杂场景中做出稳健防护决策。"


def _build_learning_insights(
    score: float,
    weaknesses: list[WeaknessItem],
    recommended_stage: str,
) -> tuple[str, list[str], list[str], list[str], str, list[str]]:
    learning_objective = _default_learning_objective(recommended_stage)
    knowledge_gaps = [f"{item.fraud_type}（正确率 {item.accuracy}%）" for item in weaknesses[:3]]
    micro_lessons = [item.suggestion for item in weaknesses[:3]]
    common_mistakes = [_COMMON_MISTAKE_LIBRARY.get(item.fraud_type, f"{item.fraud_type}场景下容易忽略关键核验动作。") for item in weaknesses[:3]]

    if not knowledge_gaps:
        knowledge_gaps = ["暂无明显知识盲区，建议继续巩固综合题。"]
    if not micro_lessons:
        micro_lessons = ["继续保持每次训练后复盘，形成固定核验清单。"]
    if not common_mistakes:
        common_mistakes = ["注意在时间压力场景下保持“先核验后操作”的节奏。"]

    if score >= 85:
        coach_feedback = "你的反诈学习表现稳定，建议把重点放在复杂复合场景的决策顺序上。"
    elif score >= 60:
        coach_feedback = "你已具备基础识别能力，下一步应重点训练高频薄弱场景的处置动作。"
    else:
        coach_feedback = "当前基础仍需巩固，建议先完成基础识诈微课，再进行阶段题训练。"

    next_plan = [
        f"优先完成【{recommended_stage}】阶段训练并复盘错题。",
        "针对薄弱点各练习 3-5 题，记录触发词与正确处置顺序。",
        "下一轮训练后对比趋势分数，确认是否稳定提升。",
    ]
    return learning_objective, knowledge_gaps, micro_lessons, common_mistakes, coach_feedback, next_plan


async def _generate_learning_insights_via_llm(
    score: float,
    recommended_stage: str,
    weaknesses: list[WeaknessItem],
) -> dict | None:
    settings = get_settings()
    if not settings.OPENAI_API_KEY or not settings.OPENAI_BASE_URL or not settings.OPENAI_MODEL:
        return None

    weakness_brief = "\n".join([f"- {w.fraud_type}: 错{w.wrong_count}/{w.total}, 准确率{w.accuracy}%" for w in weaknesses]) or "- 暂无明显薄弱项"
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是反诈训练教练。请基于用户测验表现，输出教育向复盘建议。"
                    "必须仅返回JSON对象，字段为：learning_objective, knowledge_gaps, micro_lessons, common_mistakes, coach_feedback, next_plan。"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"用户得分：{score}\n"
                    f"推荐阶段：{recommended_stage}\n"
                    f"薄弱项：\n{weakness_brief}\n"
                    "要求：每个列表字段给3条以内，中文、简洁、可执行。"
                ),
            },
        ],
        "temperature": 0.4,
        "max_tokens": 900,
    }
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
        parsed = json.loads(_strip_code_fence(content))
        return parsed if isinstance(parsed, dict) else None
    except Exception as exc:
        logger.warning("LLM learning insight generation failed: %s", exc)
        return None


def _safe_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()][:3]


def _strip_code_fence(content: str) -> str:
    normalized = (content or "").strip()
    if normalized.startswith("```"):
        normalized = re.sub(r"^```(?:json)?", "", normalized).strip()
        normalized = re.sub(r"```$", "", normalized).strip()
    return normalized


def _normalize_options(options: list[object]) -> list[str]:
    normalized = [str(option).strip() for option in options if str(option).strip()]
    return normalized[:4]


def _question_from_payload(payload: dict, default_difficulty: str) -> EducationQuestion | None:
    question = str(payload.get("question", "") or "").strip()
    options = _normalize_options(payload.get("options") or [])
    answer = payload.get("answer")
    explanation = str(payload.get("explanation", "") or "").strip()
    category = str(payload.get("category", "") or "").strip() or "反诈训练"
    fraud_type = str(payload.get("fraud_type", "") or "").strip() or category
    difficulty = str(payload.get("difficulty", "") or "").strip().lower() or default_difficulty

    try:
        answer_index = int(answer)
    except (TypeError, ValueError):
        answer_index = -1

    if not question or len(options) != 4 or answer_index not in {0, 1, 2, 3} or not explanation:
        return None

    return EducationQuestion(
        question_id=f"gq_{uuid4().hex[:12]}",
        question=question,
        options=options,
        answer=answer_index,
        explanation=explanation,
        category=category,
        difficulty=difficulty,
        fraud_type=fraud_type,
        source_type="generated",
    )


def _serialize_question(question: EducationQuestion) -> dict:
    return question.model_dump()


def _load_generated_questions() -> list[EducationQuestion]:
    cache_path = _cache_path()
    if not cache_path.exists():
        return []

    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.warning("Failed to read generated education questions cache from %s", cache_path)
        return []

    questions: list[EducationQuestion] = []
    for item in payload if isinstance(payload, list) else []:
        try:
            questions.append(EducationQuestion(**item))
        except Exception:
            continue
    return questions


def _persist_generated_questions(questions: list[EducationQuestion]) -> None:
    cache_path = _cache_path()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps([_serialize_question(question) for question in questions], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _filter_questions_by_stage(questions: list[EducationQuestion], stage_id: str | None) -> list[EducationQuestion]:
    if not stage_id or stage_id not in _STAGE_DIFFICULTY_MAP:
        return list(questions)
    allowed = _STAGE_DIFFICULTY_MAP[stage_id]
    filtered = [question for question in questions if question.difficulty in allowed]
    return filtered or list(questions)


def _question_lookup() -> dict[str, EducationQuestion]:
    lookup: dict[str, EducationQuestion] = {}
    for question in [*_STATIC_QUESTION_BANK, *_load_generated_questions()]:
        lookup[question.question_id] = question
    return lookup


def _question_to_public(question: EducationQuestion) -> EducationQuestionPublic:
    return EducationQuestionPublic(
        question_id=question.question_id,
        question=question.question,
        options=question.options,
        category=question.category,
        difficulty=question.difficulty,
        fraud_type=question.fraud_type,
        source_type=question.source_type,
    )


def _sample_questions(pool: list[EducationQuestion], count: int) -> list[EducationQuestion]:
    if len(pool) <= count:
        shuffled = list(pool)
        random.shuffle(shuffled)
        return shuffled
    return random.sample(pool, count)


def _question_fingerprint(question: EducationQuestion) -> str:
    normalized_stem = re.sub(r"\s+", "", question.question).lower()
    normalized_options = "|".join(re.sub(r"\s+", "", option).lower() for option in question.options)
    return f"{normalized_stem}::{normalized_options}"


def _build_generation_prompt(stage_id: str | None, count: int, sources: list[dict]) -> tuple[str, str]:
    stage = get_stage_detail(stage_id) if stage_id else None
    stage_name = stage.name if stage else "综合"
    stage_desc = stage.description if stage else "覆盖多类高发诈骗套路"

    context_blocks: list[str] = []
    for index, source in enumerate(sources[:3], start=1):
        metadata = source.get("metadata") or {}
        context_blocks.append(
            "\n".join(
                [
                    f"资料{index}: {metadata.get('item_id') or metadata.get('title') or '未命名资料'}",
                    f"诈骗类型: {metadata.get('fraud_type') or '未标注'}",
                    f"来源: {metadata.get('source') or '未提供来源'}",
                    f"摘要: {str(source.get('text', '') or '').strip()}",
                ]
            )
        )

    system_prompt = (
        "你是反诈教育训练题生成器。"
        "请输出适合普通用户训练的单选题，要求题干清晰、选项互斥、答案唯一、解析专业。"
        "必须只返回 JSON 数组，不要返回 Markdown、解释或额外文本。"
    )
    user_prompt = (
        f"请为“{stage_name}”学习阶段生成 {count} 道反诈训练单选题。\n"
        f"阶段说明：{stage_desc}\n"
        "要求：\n"
        "1. 每题包含 question, options, answer, explanation, category, difficulty, fraud_type 字段\n"
        "2. options 必须是 4 个中文选项，answer 必须是 0-3 之间的整数\n"
        "3. 题目聚焦高发诈骗类型：投资理财、兼职刷单、冒充客服、虚假征信、AI语音冒充、钓鱼链接、游戏交易、虚假招聘等\n"
        "4. 题目要偏情境判断，不要纯概念记忆题\n"
        "5. explanation 必须解释为什么正确、错误选项为什么危险\n"
        "6. difficulty 只允许 beginner / intermediate / advanced\n"
        "7. category 用短词概括题目主题\n"
        "以下是可参考的反诈资料：\n"
        f"{chr(10).join(context_blocks) if context_blocks else '无额外资料，可根据反诈常识生成。'}"
    )
    return system_prompt, user_prompt


async def _generate_questions_via_llm(count: int, stage_id: str | None) -> list[EducationQuestion]:
    settings = get_settings()
    if not settings.OPENAI_API_KEY or not settings.OPENAI_BASE_URL or not settings.OPENAI_MODEL:
        return []

    stage = get_stage_detail(stage_id) if stage_id else None
    rag_query = f"{stage.name if stage else '综合'}阶段 反诈训练题 诈骗案例 风险信号"
    try:
        sources = retrieve_relevant_sources(rag_query, similarity_top_k=3)
    except Exception as exc:
        logger.warning("Education question generation RAG retrieval failed: %s", exc)
        sources = []

    system_prompt, user_prompt = _build_generation_prompt(stage_id=stage_id, count=count, sources=sources)
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.6,
        "max_tokens": 2200,
    }
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=80.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
    except Exception as exc:
        logger.error("Education question generation failed: %s", exc)
        return []

    normalized = _strip_code_fence(content)
    try:
        raw_items = json.loads(normalized)
    except json.JSONDecodeError:
        logger.error("Education question generation returned invalid JSON: %s", normalized[:500])
        return []

    stage_difficulty = stage_id if stage_id in {"beginner", "intermediate", "advanced"} else "intermediate"
    questions: list[EducationQuestion] = []
    for item in raw_items if isinstance(raw_items, list) else []:
        if not isinstance(item, dict):
            continue
        question = _question_from_payload(item, default_difficulty=stage_difficulty)
        if question:
            questions.append(question)
    return questions


async def get_question_batch(count: int = 5, stage_id: str | None = None, refresh: bool = False) -> list[EducationQuestionPublic]:
    generated_questions = _load_generated_questions()
    if refresh or not generated_questions:
        new_questions = await _generate_questions_via_llm(count=max(count, 6), stage_id=stage_id)
        if new_questions:
            deduped: dict[str, EducationQuestion] = {_question_fingerprint(question): question for question in generated_questions}
            for question in new_questions:
                deduped[_question_fingerprint(question)] = question
            generated_questions = list(deduped.values())[-_GENERATED_CACHE_LIMIT:]
            _persist_generated_questions(generated_questions)

    pool = _filter_questions_by_stage([*generated_questions, *_STATIC_QUESTION_BANK], stage_id)
    selected = _sample_questions(pool, count)
    return [_question_to_public(question) for question in selected]


async def submit_test_answers(question_ids: list[str], answers: dict[str, int], username: str = "anonymous") -> SubmitTestResponse:
    lookup = _question_lookup()
    ordered_questions = [lookup[question_id] for question_id in question_ids if question_id in lookup]
    total = len(ordered_questions)
    if total == 0:
        return SubmitTestResponse(total=0, correct=0, score=0.0, passed=False, details=[])

    details: list[SubmitTestDetail] = []
    correct = 0
    for question in ordered_questions:
        selected = answers.get(question.question_id)
        is_correct = selected == question.answer
        if is_correct:
            correct += 1
        details.append(
            SubmitTestDetail(
                question_id=question.question_id,
                question=question.question,
                options=question.options,
                selected=selected,
                correct_answer=question.answer,
                is_correct=is_correct,
                explanation=question.explanation,
                category=question.category,
                difficulty=question.difficulty,
                fraud_type=question.fraud_type,
                source_type=question.source_type,
            )
        )

    score = round((correct / total) * 100, 2)
    passed = score >= 60
    weaknesses = _build_weaknesses(details)
    recommended_stage = _recommend_stage(score, weaknesses)
    next_actions = _build_next_actions(weaknesses, recommended_stage)
    risk_profile = _risk_profile(score)
    summary = _build_summary(score, weaknesses, recommended_stage)
    normalized_user = username or "anonymous"
    history = _append_test_history(score=score, passed=passed, username=normalized_user)
    recent_trend = _build_recent_trend(history, username=normalized_user, limit=3)
    trend_delta = _calculate_trend_delta(recent_trend)
    learning_objective, knowledge_gaps, micro_lessons, common_mistakes, coach_feedback, next_plan = _build_learning_insights(
        score=score,
        weaknesses=weaknesses,
        recommended_stage=recommended_stage,
    )
    llm_payload = await _generate_learning_insights_via_llm(
        score=score,
        recommended_stage=recommended_stage,
        weaknesses=weaknesses,
    )
    if llm_payload:
        learning_objective = str(llm_payload.get("learning_objective") or learning_objective)
        knowledge_gaps = _safe_list(llm_payload.get("knowledge_gaps")) or knowledge_gaps
        micro_lessons = _safe_list(llm_payload.get("micro_lessons")) or micro_lessons
        common_mistakes = _safe_list(llm_payload.get("common_mistakes")) or common_mistakes
        coach_feedback = str(llm_payload.get("coach_feedback") or coach_feedback)
        next_plan = _safe_list(llm_payload.get("next_plan")) or next_plan

    return SubmitTestResponse(
        total=total,
        correct=correct,
        score=score,
        passed=passed,
        details=details,
        risk_profile=risk_profile,
        weaknesses=weaknesses,
        recommended_stage=recommended_stage,
        next_actions=next_actions,
        summary=summary,
        recent_trend=recent_trend,
        trend_delta=trend_delta,
        learning_objective=learning_objective,
        knowledge_gaps=knowledge_gaps,
        micro_lessons=micro_lessons,
        common_mistakes=common_mistakes,
        coach_feedback=coach_feedback,
        next_plan=next_plan,
    )


async def coach_reply(
    question: str,
    stage_id: str | None = None,
    score: float | None = None,
    wrong_topics: list[str] | None = None,
) -> EducationCoachResponse:
    prompt_question = (question or "").strip()
    if not prompt_question:
        return EducationCoachResponse(reply="请先输入你想咨询的训练问题。", actions=["例如：我总是分不清刷单和投资诈骗，怎么记？"])

    stage_text = stage_id or "intermediate"
    wrong_text = "、".join(wrong_topics or []) or "暂无"
    default_reply = f"作为反诈训练教练，建议你围绕【{stage_text}】阶段，优先复盘：{wrong_text}。先记住“先核验来源，再做资金动作”。"
    default_actions = [
        "把本次错题按诈骗类型分组，每组写1条触发词。",
        "针对最薄弱类型再练3题，并记录正确处置顺序。",
        "下次训练前先复述一次你的核验清单。",
    ]

    settings = get_settings()
    if not settings.OPENAI_API_KEY or not settings.OPENAI_BASE_URL or not settings.OPENAI_MODEL:
        return EducationCoachResponse(reply=default_reply, actions=default_actions)

    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是反诈训练教练，请给出教育导向建议，不做执法或真实案件裁定。"
                    "仅返回JSON对象，字段：reply, actions。actions最多3条。"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"用户问题：{prompt_question}\n"
                    f"阶段：{stage_text}\n"
                    f"得分：{score if score is not None else '未知'}\n"
                    f"薄弱主题：{wrong_text}\n"
                    "请给可执行学习建议。"
                ),
            },
        ],
        "temperature": 0.5,
        "max_tokens": 700,
    }
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
        parsed = json.loads(_strip_code_fence(content))
        if isinstance(parsed, dict):
            reply = str(parsed.get("reply") or default_reply)
            actions = _safe_list(parsed.get("actions")) or default_actions
            return EducationCoachResponse(reply=reply, actions=actions)
    except Exception as exc:
        logger.warning("Education coach reply failed: %s", exc)

    return EducationCoachResponse(reply=default_reply, actions=default_actions)


def _build_weaknesses(details: list[SubmitTestDetail]) -> list[WeaknessItem]:
    stats: dict[str, dict[str, int]] = {}
    for detail in details:
        fraud_type = detail.fraud_type or "综合诈骗"
        bucket = stats.setdefault(fraud_type, {"total": 0, "correct": 0})
        bucket["total"] += 1
        if detail.is_correct:
            bucket["correct"] += 1

    weaknesses: list[WeaknessItem] = []
    for fraud_type, item in stats.items():
        total = item["total"]
        correct = item["correct"]
        wrong = total - correct
        accuracy = round((correct / total) * 100, 2) if total else 0.0
        suggestion = _FRAUD_SUGGESTIONS.get(fraud_type, "优先复盘错题，提炼可执行的核验动作。")
        weaknesses.append(
            WeaknessItem(
                fraud_type=fraud_type,
                wrong_count=wrong,
                total=total,
                accuracy=accuracy,
                suggestion=suggestion,
            )
        )
    weaknesses.sort(key=lambda item: (item.wrong_count, -item.accuracy), reverse=True)
    return weaknesses[:3]


def _recommend_stage(score: float, weaknesses: list[WeaknessItem]) -> str:
    if score < 60:
        return "beginner"
    if score < 85:
        return "intermediate"
    if any(item.wrong_count > 0 for item in weaknesses):
        return "advanced"
    return "advanced"


def _build_next_actions(weaknesses: list[WeaknessItem], recommended_stage: str) -> list[str]:
    actions: list[str] = []
    if weaknesses:
        actions.append(f"优先复盘【{weaknesses[0].fraud_type}】相关错题并记录高危触发词。")
    actions.append("继续进行 5-8 题分阶段训练，保持题干情境拆解习惯。")
    if recommended_stage == "beginner":
        actions.append("先训练基础核验动作：来源核验、身份复核、资金操作延迟。")
    elif recommended_stage == "intermediate":
        actions.append("重点强化跨平台诱导和时间压力话术的识别能力。")
    else:
        actions.append("进入综合研判模式，训练多信号叠加场景下的决策能力。")
    return actions


def _risk_profile(score: float) -> str:
    if score >= 85:
        return "low"
    if score >= 60:
        return "medium"
    return "high"


def _build_summary(score: float, weaknesses: list[WeaknessItem], recommended_stage: str) -> str:
    if not weaknesses:
        return "本次训练未发现明显薄弱项，可继续保持综合训练。"
    top = weaknesses[0]
    return (
        f"当前得分 {score:.2f}，主要薄弱点集中在“{top.fraud_type}”，"
        f"建议下一阶段重点训练 {recommended_stage}。"
    )
