import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.profile import ProfileData
from app.services.detection_service import detect_ai_image, detect_ai_text, detect_audio_risk
from app.services.profile_service import (
    _profile_to_data,
    generate_suggestions,
    get_behavior_stats,
    get_or_create_profile,
    record_detection,
)
from app.services.rag_service import ask_question
from app.services.vision_service import analyze_image_fraud_risk

logger = logging.getLogger(__name__)


TEXT_SIGNAL_WEIGHTS = {
    '转账': 0.12,
    '汇款': 0.12,
    '打款': 0.10,
    '保证金': 0.18,
    '解冻': 0.16,
    '解冻费': 0.18,
    '手续费': 0.14,
    '验证金': 0.14,
    '安全账户': 0.20,
    '充值': 0.10,
    '垫付': 0.12,
    '刷流水': 0.16,
    '贷款': 0.08,
    '放款': 0.10,
    '刷单': 0.16,
    '返利': 0.12,
    '退款': 0.08,
    '赔付': 0.08,
    '投资': 0.08,
    '理财': 0.08,
    '高收益': 0.12,
    '客服': 0.08,
    '公安': 0.12,
    '警察': 0.12,
    '法院': 0.12,
    '检察院': 0.12,
    '验证码': 0.12,
    '共享屏幕': 0.18,
    '立即': 0.05,
    '马上': 0.05,
    '否则': 0.06,
    '超时': 0.06,
}

TEXT_SIGNAL_PATTERNS = [
    ('先交钱再处理', ['保证金', '放款'], 0.20),
    ('账户异常诱导转账', ['冻结', '转账'], 0.22),
    ('客服退款赔付诱导', ['客服', '退款'], 0.18),
    ('贷款收费骗局', ['贷款', '手续费'], 0.18),
    ('刷单返利骗局', ['刷单', '垫付'], 0.20),
    ('公检法资金核验骗局', ['公安', '安全账户'], 0.25),
]

FRAUD_TYPE_RULES = [
    {
        'code': 'investment_fraud',
        'label': '投资理财诈骗',
        'keywords': ['投资', '理财', '收益', '稳赚', '内幕消息'],
    },
    {
        'code': 'part_time_rebate',
        'label': '兼职刷单诈骗',
        'keywords': ['刷单', '返利', '垫付', '兼职', '做任务'],
    },
    {
        'code': 'fake_loan',
        'label': '虚假贷款诈骗',
        'keywords': ['贷款', '放款', '保证金', '解冻', '手续费'],
    },
    {
        'code': 'credit_repair',
        'label': '虚假征信修复诈骗',
        'keywords': ['征信', '修复', '洗白', '信用分', '消除记录'],
    },
    {
        'code': 'customer_service_impersonation',
        'label': '冒充客服诈骗',
        'keywords': ['客服', '退款', '赔付', '订单', '售后'],
    },
    {
        'code': 'authority_impersonation',
        'label': '冒充公检法诈骗',
        'keywords': ['公安', '警察', '法院', '检察院', '安全账户'],
    },
    {
        'code': 'romance_fraud',
        'label': '婚恋交友诈骗',
        'keywords': ['交友', '恋爱', '网恋', '见面', '感情'],
    },
    {
        'code': 'phishing_takeover',
        'label': '钓鱼控号诈骗',
        'keywords': ['验证码', '共享屏幕', '链接', '验证', '账号'],
    },
    {
        'code': 'fake_refund',
        'label': '退款退费诈骗',
        'keywords': ['退款', '退费', '赔付', '客服', '退款通道'],
    },
    {
        'code': 'ai_voice_impersonation',
        'label': 'AI合成语音诈骗',
        'keywords': ['语音', '录音', '合成', '领导来电', '家属来电'],
    },
]

INTENT_RULES = [
    ('fraud_risk_analysis', '诈骗风险分析', ['诈骗', '被骗', '风险', '可疑', '检测', '识别']),
    ('credibility_verification', '可信度核验', ['真假', '是真的吗', '核实', '谣言', '可信吗']),
    ('emergency_guidance', '应急处置咨询', ['怎么办', '报警', '阻止', '处理', '联系家人']),
]

MODALITY_LABELS = {
    'text': '文本',
    'image': '图片',
    'audio': '语音',
}


def _truncate(value: str, limit: int = 120) -> str:
    text = (value or '').strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + '…'


def _score_text_fraud_signals(text: str) -> dict[str, Any]:
    content = (text or '').strip()
    if not content:
        return {
            'matched_keywords': [],
            'matched_patterns': [],
            'keyword_score': 0.0,
            'pattern_bonus': 0.0,
            'score': 0.0,
        }

    matched_keywords: list[str] = []
    keyword_sum = 0.0
    for keyword, weight in TEXT_SIGNAL_WEIGHTS.items():
        if keyword in content:
            matched_keywords.append(keyword)
            keyword_sum += weight

    matched_patterns: list[str] = []
    pattern_sum = 0.0
    for pattern_name, keywords, bonus in TEXT_SIGNAL_PATTERNS:
        if all(keyword in content for keyword in keywords):
            matched_patterns.append(pattern_name)
            pattern_sum += bonus

    keyword_score = min(0.45, keyword_sum)
    pattern_bonus = min(0.30, pattern_sum)
    score = min(1.0, keyword_score + pattern_bonus)
    return {
        'matched_keywords': matched_keywords,
        'matched_patterns': matched_patterns,
        'keyword_score': round(keyword_score, 4),
        'pattern_bonus': round(pattern_bonus, 4),
        'score': round(score, 4),
    }


async def _resolve_profile(db: AsyncSession, user) -> tuple[ProfileData, list[str]]:
    profile = await get_or_create_profile(db, user.id)
    profile_data = _profile_to_data(profile)
    stats = await get_behavior_stats(db, user.username, user.id)
    suggestions = await generate_suggestions(profile_data, stats)
    return profile_data, suggestions


def _infer_risk_level(risk_score: float) -> str:
    if risk_score >= 0.75:
        return 'high'
    if risk_score >= 0.4:
        return 'medium'
    return 'low'


def _collect_fraud_type_candidates(text: str, transcript: str, image_label: str) -> list[dict[str, Any]]:
    corpus = ' '.join([text, transcript, image_label]).lower()
    candidates: list[dict[str, Any]] = []

    for rule in FRAUD_TYPE_RULES:
        matched_keywords = [keyword for keyword in rule['keywords'] if keyword.lower() in corpus]
        if not matched_keywords:
            continue

        coverage = len(matched_keywords) / max(len(rule['keywords']), 1)
        confidence = round(min(0.98, 0.45 + coverage * 0.5), 4)
        candidates.append(
            {
                'code': rule['code'],
                'label': rule['label'],
                'confidence': confidence,
                'matched_keywords': matched_keywords,
                'rationale': f"命中关键词：{'、'.join(matched_keywords[:4])}",
            }
        )

    candidates.sort(key=lambda item: item['confidence'], reverse=True)
    return candidates


def _resolve_primary_fraud_type(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    if candidates:
        return candidates[0]
    return {
        'code': 'suspicious_script',
        'label': '可疑诈骗话术',
        'confidence': 0.35,
        'matched_keywords': [],
        'rationale': '当前未命中特定高发剧本，系统判定为待进一步复核的可疑话术。',
    }


def _infer_intent(
    text: str,
    modalities_received: list[str],
    risk_level: str,
    primary_fraud_type: dict[str, Any],
) -> dict[str, Any]:
    content = (text or '').strip().lower()
    best_match = {
        'code': 'general_consultation',
        'label': '一般咨询',
        'confidence': 0.58,
        'reason': '当前输入以一般风险咨询为主，未触发更明确的专用意图模板。',
    }

    for code, label, keywords in INTENT_RULES:
        matched = [keyword for keyword in keywords if keyword.lower() in content]
        if not matched:
            continue
        confidence = min(0.96, 0.62 + len(matched) * 0.08 + (0.06 if len(modalities_received) > 1 else 0.0))
        best_match = {
            'code': code,
            'label': label,
            'confidence': round(confidence, 4),
            'reason': f"命中用户表达：{'、'.join(matched[:3])}，结合{len(modalities_received)}种模态输入进入专项研判。",
        }
        break

    if best_match['code'] == 'general_consultation' and risk_level in {'medium', 'high'}:
        best_match = {
            'code': 'fraud_risk_analysis',
            'label': '诈骗风险分析',
            'confidence': 0.82 if risk_level == 'high' else 0.72,
            'reason': f"系统检测到明显风险信号，主判定类型为{primary_fraud_type['label']}。",
        }

    return best_match


def _build_guardian_action(
    risk_level: str,
    guardian_action_needed: bool,
    fraud_types: list[str],
    profile_summary: ProfileData,
) -> dict[str, Any]:
    target_role = '监护人/家属'
    fraud_summary = '、'.join(fraud_types[:3]) if fraud_types else '可疑诈骗风险'

    if not guardian_action_needed:
        return {
            'priority': 'none',
            'notice': '当前风险尚未达到必须联动监护人的阈值。',
            'triggered': False,
            'target_role': target_role,
            'message_template': '当前事件暂未达到自动联动阈值，建议持续观察并保留相关证据。',
            'next_step': '保持会话观察，必要时升级为人工复核。',
            'checklist': [],
        }

    age_group = profile_summary.age_group or '重点保护对象'
    priority = 'urgent' if risk_level == 'high' else 'recommended'
    notice = (
        f'系统检测到高风险场景，疑似涉及{fraud_summary}，当前用户属于{age_group}重点防护群体，'
        '建议监护人立即联系当事人核实，暂停转账或进一步操作。'
    )

    return {
        'priority': priority,
        'notice': notice,
        'triggered': True,
        'target_role': target_role,
        'message_template': (
            f'【反诈智能助手提醒】检测到疑似{fraud_summary}高风险事件，请尽快联系当事人，'
            '确认是否存在转账、验证码提供、共享屏幕或下载陌生应用行为。'
        ),
        'next_step': '建议优先电话核实，再根据情况执行止付、留证和报警。',
        'checklist': [
            '立即联系当事人，确认是否正在进行转账、充值或验证操作。',
            '要求当事人暂停所有付款、共享屏幕和验证码提供行为。',
            '保留聊天记录、截图、语音和支付凭证等证据。',
            '如已付款，立即联系银行或支付平台并尽快报警。',
        ],
    }


def _build_evidence_items(
    signals: list[dict[str, Any]],
    rag_sources: list[dict[str, Any]],
    profile_summary: ProfileData,
    text_result: dict[str, Any],
    image_result: dict[str, Any],
    audio_result: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []

    for signal in signals[:3]:
        modality = signal.get('modality', '')
        evidence.append(
            {
                'title': f"{MODALITY_LABELS.get(modality, modality or '输入')}风险信号",
                'source': '多模态判别引擎',
                'snippet': _truncate(signal.get('signal', '')),
                'score': round(float(signal.get('score') or 0.0), 4),
                'modality': modality,
                'kind': 'model_signal',
            }
        )

    for result, modality in ((text_result, 'text'), (image_result, 'image'), (audio_result, 'audio')):
        matched_keywords = result.get('matched_keywords') or []
        matched_patterns = result.get('matched_patterns') or []
        if matched_keywords:
            evidence.append(
                {
                    'title': f"{MODALITY_LABELS.get(modality, modality)}命中关键词",
                    'source': '风险规则库',
                    'snippet': f"命中关键词：{'、'.join(matched_keywords[:6])}",
                    'score': round(float(result.get('text_rule_score') or result.get('confidence') or 0.0), 4),
                    'modality': modality,
                    'kind': 'rule_match',
                }
            )
        if matched_patterns:
            evidence.append(
                {
                    'title': f"{MODALITY_LABELS.get(modality, modality)}命中模式",
                    'source': '诈骗剧本模板',
                    'snippet': f"命中模式：{'、'.join(matched_patterns[:4])}",
                    'score': round(float(result.get('enhanced_text_score') or result.get('image_fused_score') or result.get('confidence') or 0.0), 4),
                    'modality': modality,
                    'kind': 'pattern_match',
                }
            )

    for source in rag_sources[:2]:
        metadata = source.get('metadata') or {}
        source_label = metadata.get('source') or '反诈知识库'
        evidence.append(
            {
                'title': metadata.get('fraud_type') or metadata.get('item_type') or '相似案例',
                'source': source_label,
                'snippet': _truncate(source.get('text', ''), 140),
                'score': round(float(source.get('score') or 0.0), 4),
                'modality': 'knowledge',
                'kind': 'rag_case',
            }
        )

    if profile_summary.age_group in {'老人', '学生', '儿童'} or profile_summary.occupation in {'财会人员'}:
        target = profile_summary.age_group or profile_summary.occupation or '重点群体'
        evidence.append(
            {
                'title': '画像风险加权',
                'source': '用户画像引擎',
                'snippet': f"当前用户属于{target}，系统已提高对资金诱导和身份冒充场景的风险阈值。",
                'score': 0.68,
                'modality': 'profile',
                'kind': 'profile_boost',
            }
        )

    evidence.sort(key=lambda item: item['score'], reverse=True)
    return evidence[:6]


def _build_intervention_plan(
    risk_level: str,
    primary_fraud_type: dict[str, Any],
    guardian_action_needed: bool,
) -> dict[str, Any]:
    if risk_level == 'high':
        return {
            'level': 'high',
            'headline': '建议立即阻断当前操作并启动人工复核',
            'summary': f"系统判定为{primary_fraud_type['label']}高风险场景，建议优先执行止付、核验和留证动作。",
            'recommended_channel': '弹窗强提醒 + 语音播报 + 监护人联动',
            'actions': [
                {'label': '立即暂停转账', 'description': '阻断继续付款、充值、验证码提供和屏幕共享。', 'priority': 'critical'},
                {'label': '执行身份核验', 'description': '通过官方电话或官方 App 核验对方身份与业务真实性。', 'priority': 'high'},
                {'label': '保留关键证据', 'description': '保存聊天记录、截图、录音和支付凭证，便于后续处置。', 'priority': 'high'},
                {'label': '启动监护人联动', 'description': '若为重点保护对象，通知家属或监护人同步介入。', 'priority': 'high' if guardian_action_needed else 'medium'},
            ],
        }

    if risk_level == 'medium':
        return {
            'level': 'medium',
            'headline': '建议进入谨慎核验模式',
            'summary': f"系统检测到{primary_fraud_type['label']}相关风险信号，建议在继续互动前完成身份与资金要素复核。",
            'recommended_channel': '弹窗提醒 + 人工确认',
            'actions': [
                {'label': '暂停关键操作', 'description': '暂缓付款、下载陌生应用或泄露验证码。', 'priority': 'high'},
                {'label': '核验业务真实性', 'description': '对订单、贷款、投资或退款信息进行官方渠道复核。', 'priority': 'high'},
                {'label': '记录风险线索', 'description': '保留可疑链接、账号、截图和语音内容。', 'priority': 'medium'},
            ],
        }

    return {
        'level': 'low',
        'headline': '暂未发现必须阻断的高危信号',
        'summary': '当前样本整体风险较低，但仍建议保持谨慎，不轻信陌生身份和资金诱导信息。',
        'recommended_channel': '轻量提醒',
        'actions': [
            {'label': '继续观察', 'description': '如出现转账催促、验证码索取或共享屏幕要求，立即重新检测。', 'priority': 'medium'},
            {'label': '保留上下文', 'description': '建议保留聊天与文件内容，便于后续复核。', 'priority': 'low'},
        ],
    }


def _build_summary(
    modalities_received: list[str],
    risk_level: str,
    risk_score: float,
    primary_fraud_type: dict[str, Any],
    intent: dict[str, Any],
    intervention_plan: dict[str, Any],
) -> str:
    modality_text = '、'.join(MODALITY_LABELS.get(item, item) for item in modalities_received) or '单一'
    return (
        f"系统已完成{modality_text}输入的联合研判，当前意图判定为“{intent['label']}”，"
        f"主判定类型为“{primary_fraud_type['label']}”，综合风险等级为{risk_level.upper()}，"
        f"风险分数 {risk_score * 100:.0f}%。{intervention_plan['headline']}。"
    )


def _build_report(
    summary: str,
    risk_level: str,
    primary_fraud_type: dict[str, Any],
    evidence: list[dict[str, Any]],
    intervention_plan: dict[str, Any],
    recommendations: list[str],
) -> dict[str, Any]:
    findings = [
        f"主诈骗类型判定：{primary_fraud_type['label']}（置信度 {primary_fraud_type['confidence'] * 100:.0f}%）",
        f"当前风险等级：{risk_level.upper()}",
    ]
    findings.extend(item['snippet'] for item in evidence[:3] if item.get('snippet'))

    return {
        'title': '多模态反诈安全监测报告',
        'executive_summary': summary,
        'findings': findings[:6],
        'disposition': intervention_plan.get('headline', ''),
        'recommended_actions': recommendations[:4]
        or [action['label'] for action in intervention_plan.get('actions', [])[:4]],
    }


async def analyze_multimodal_input(
    db: AsyncSession,
    user,
    text: str = '',
    image_bytes: bytes | None = None,
    image_filename: str = '',
    audio_bytes: bytes | None = None,
    audio_filename: str = '',
) -> dict[str, Any]:
    modalities_received: list[str] = []
    signals: list[dict[str, Any]] = []

    text = (text or '').strip()
    text_result: dict[str, Any] = {}
    image_result: dict[str, Any] = {}
    audio_result: dict[str, Any] = {}

    if text:
        modalities_received.append('text')
        text_result = await detect_ai_text(text)
        text_rule_result = _score_text_fraud_signals(text)
        text_base_score = float(text_result.get('confidence') or text_result.get('probability') or 0.0)
        text_enhanced_score = min(1.0, text_base_score * 0.35 + text_rule_result['score'])
        text_result['base_ai_score'] = round(text_base_score, 4)
        text_result['text_rule_score'] = text_rule_result['score']
        text_result['enhanced_text_score'] = round(text_enhanced_score, 4)
        text_result['matched_keywords'] = text_rule_result['matched_keywords']
        text_result['matched_patterns'] = text_rule_result['matched_patterns']
        signals.append(
            {
                'modality': 'text',
                'signal': text_result.get('summary') or '文本风险分析完成',
                'score': text_enhanced_score,
            }
        )

    if image_bytes:
        modalities_received.append('image')
        try:
            image_result = await analyze_image_fraud_risk(image_bytes, image_filename or 'upload-image')
            image_text_rule_result = _score_text_fraud_signals(str(image_result.get('ocr_text') or ''))
            image_base_score = float(image_result.get('risk_score') or 0.0)
            image_score = max(image_base_score, image_text_rule_result['score'])
            image_result['base_vision_score'] = round(image_base_score, 4)
            image_result['text_rule_score'] = image_text_rule_result['score']
            image_result['image_fused_score'] = round(image_score, 4)
            image_result['matched_keywords'] = image_text_rule_result['matched_keywords']
            image_result['matched_patterns'] = image_text_rule_result['matched_patterns']
        except Exception as exc:
            logger.warning('视觉 API 分析失败，回退本地图片检测: %s', exc)
            image_result = await detect_ai_image(image_bytes, image_filename or 'upload-image')
            image_text_rule_result = _score_text_fraud_signals(str(image_result.get('ocr_text') or ''))
            image_base_score = float(image_result.get('confidence') or image_result.get('probability') or 0.0)
            image_score = max(image_base_score, image_text_rule_result['score'])
            image_result['base_vision_score'] = round(image_base_score, 4)
            image_result['text_rule_score'] = image_text_rule_result['score']
            image_result['image_fused_score'] = round(image_score, 4)
            image_result['matched_keywords'] = image_text_rule_result['matched_keywords']
            image_result['matched_patterns'] = image_text_rule_result['matched_patterns']

        signals.append(
            {
                'modality': 'image',
                'signal': image_result.get('summary') or image_result.get('label') or '图片风险分析完成',
                'score': image_score,
            }
        )

    if audio_bytes:
        modalities_received.append('audio')
        audio_result = await detect_audio_risk(audio_bytes, audio_filename or 'upload-audio')
        audio_transcript = str(audio_result.get('transcript') or '')
        audio_rule_result = _score_text_fraud_signals(audio_transcript)
        audio_base_score = float(audio_result.get('confidence') or audio_result.get('probability') or 0.0)
        audio_enhanced_score = min(1.0, audio_base_score * 0.35 + audio_rule_result['score'])
        audio_result['base_ai_score'] = round(audio_base_score, 4)
        audio_result['text_rule_score'] = audio_rule_result['score']
        audio_result['enhanced_text_score'] = round(audio_enhanced_score, 4)
        audio_result['matched_keywords'] = audio_rule_result['matched_keywords']
        audio_result['matched_patterns'] = audio_rule_result['matched_patterns']
        signals.append(
            {
                'modality': 'audio',
                'signal': audio_result.get('summary') or audio_result.get('label') or '语音风险分析完成',
                'score': audio_enhanced_score,
            }
        )

    transcript = str(audio_result.get('transcript') or '')
    image_label = str(image_result.get('label') or '')
    image_ocr_text = str(image_result.get('ocr_text') or '')
    fused_context = '\n'.join(filter(None, [text, transcript, image_ocr_text, image_label]))

    if not fused_context:
        raise ValueError('至少需要提供一种有效输入')

    rag_result = await ask_question(fused_context)
    rag_sources = rag_result.get('sources', [])

    profile_summary, recommendations = await _resolve_profile(db, user)

    signal_scores = [float(signal['score']) for signal in signals]
    rag_boost = 0.12 if rag_sources else 0.0
    profile_boost = 0.08 if profile_summary.age_group in {'老人', '学生', '儿童'} or profile_summary.occupation in {'财会人员'} else 0.0
    risk_score = min(1.0, max(signal_scores or [0.2]) + rag_boost + profile_boost)
    risk_score = round(risk_score, 4)
    risk_level = _infer_risk_level(risk_score)

    fraud_type_candidates = _collect_fraud_type_candidates(text, transcript + '\n' + image_ocr_text, image_label)
    primary_fraud_type = _resolve_primary_fraud_type(fraud_type_candidates)
    fraud_types = [candidate['label'] for candidate in fraud_type_candidates[:3]] or [primary_fraud_type['label']]
    guardian_action_needed = risk_level == 'high' and profile_summary.age_group in {'老人', '儿童'}
    guardian_action = _build_guardian_action(risk_level, guardian_action_needed, fraud_types, profile_summary)
    intent = _infer_intent(text, modalities_received, risk_level, primary_fraud_type)
    evidence = _build_evidence_items(signals, rag_sources, profile_summary, text_result, image_result, audio_result)
    intervention_plan = _build_intervention_plan(risk_level, primary_fraud_type, guardian_action_needed)

    await record_detection(db, user.id, 'multimodal-agent', risk_level)

    summary = _build_summary(
        modalities_received=modalities_received,
        risk_level=risk_level,
        risk_score=risk_score,
        primary_fraud_type=primary_fraud_type,
        intent=intent,
        intervention_plan=intervention_plan,
    )
    report = _build_report(
        summary=summary,
        risk_level=risk_level,
        primary_fraud_type=primary_fraud_type,
        evidence=evidence,
        intervention_plan=intervention_plan,
        recommendations=recommendations,
    )

    return {
        'risk_level': risk_level,
        'risk_score': risk_score,
        'intent': intent,
        'fraud_type': {
            'code': primary_fraud_type['code'],
            'label': primary_fraud_type['label'],
            'confidence': primary_fraud_type['confidence'],
            'rationale': primary_fraud_type['rationale'],
        },
        'fraud_types': fraud_types,
        'evidence': evidence,
        'intervention_plan': intervention_plan,
        'modalities_received': modalities_received,
        'signals': signals,
        'text_result': text_result,
        'image_result': image_result,
        'audio_result': audio_result,
        'rag_sources': rag_sources,
        'profile_summary': profile_summary,
        'recommendations': recommendations,
        'guardian_action_needed': guardian_action_needed,
        'guardian_action': guardian_action,
        'report': report,
        'summary': summary,
    }
