from fastapi import APIRouter, HTTPException

from app.schemas.education import (
    EducationQuestion,
    EducationQuestionPublic,
    EducationQuestionsResponse,
    EducationStage,
    EducationStageDetailResponse,
    SubmitTestRequest,
    SubmitTestResponse,
)

router = APIRouter()

_STAGES = [
    EducationStage(stage_id="beginner", name="初级", description="认识常见谣言类型与基础辨别方法"),
    EducationStage(stage_id="intermediate", name="中级", description="学习信息溯源、交叉验证和证据评估"),
    EducationStage(stage_id="advanced", name="高级", description="掌握复杂传播链分析与风险研判技巧"),
]

_STAGE_CASES = {
    "beginner": {
        "stage_id": "beginner",
        "name": "初级",
        "description": "认识常见谣言类型与基础辨别方法",
        "cases": [
            {
                "case_id": "b1",
                "title": "群聊截图式谣言",
                "summary": "截图声称某地将全面封控，但无官方来源。",
                "analysis": "先查找官方渠道和权威媒体是否同步发布，再核验截图时间和上下文。",
                "tips": ["优先核验原始来源", "警惕断章取义截图"],
            },
            {
                "case_id": "b2",
                "title": "旧闻翻炒",
                "summary": "旧新闻被重新包装成最新突发事件。",
                "analysis": "核对发布时间、事件地点与最新权威通报，防止时间错配。",
                "tips": ["先看发布时间", "对照官方最新通报"],
            },
        ],
    },
    "intermediate": {
        "stage_id": "intermediate",
        "name": "中级",
        "description": "学习信息溯源、交叉验证和证据评估",
        "cases": [
            {
                "case_id": "i1",
                "title": "断章取义数据图",
                "summary": "图表只截取有利区间，误导结论。",
                "analysis": "获取完整数据集，检查统计口径与采样周期。",
                "tips": ["核对统计口径", "查看完整时间序列"],
            }
        ],
    },
    "advanced": {
        "stage_id": "advanced",
        "name": "高级",
        "description": "掌握复杂传播链分析与风险研判技巧",
        "cases": [
            {
                "case_id": "a1",
                "title": "跨平台协同传播",
                "summary": "同一叙事在多个平台短时间内集中扩散。",
                "analysis": "比较首发时间、账号关系和内容相似度，识别异常传播链。",
                "tips": ["识别首发节点", "分析转发网络"],
            }
        ],
    },
}

_QUESTIONS: list[EducationQuestion] = [
    EducationQuestion(
        question_id="q1",
        question="看到‘紧急通知’截图时，第一步最合理的是？",
        options=["立即转发提醒亲友", "核验发布主体和来源", "相信转发量最多的版本", "等待自媒体解读"],
        answer=1,
        explanation="先核验发布主体和原始来源是基础步骤。",
    ),
    EducationQuestion(
        question_id="q2",
        question="判断一条新闻是否旧闻翻炒，最关键的是？",
        options=["看标题是否耸动", "看评论区态度", "核对发布时间和事件时间", "看转发平台"],
        answer=2,
        explanation="发布时间与事件时间错位是旧闻翻炒的常见特征。",
    ),
    EducationQuestion(
        question_id="q3",
        question="面对互相矛盾的两条消息，应优先采用哪种策略？",
        options=["选择更符合直觉的一条", "参考熟人意见", "交叉查证权威渠道", "等待热度下降"],
        answer=2,
        explanation="交叉查证权威渠道可降低误判概率。",
    ),
]


@router.get("/stages", response_model=list[EducationStage])
async def get_education_stages():
    return _STAGES


@router.get("/stage/{stage_id}", response_model=EducationStageDetailResponse)
async def get_education_stage(stage_id: str):
    data = _STAGE_CASES.get(stage_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"学习阶段 {stage_id} 不存在")
    return EducationStageDetailResponse(**data)


@router.get("/questions", response_model=EducationQuestionsResponse)
async def get_education_questions():
    items = [
        EducationQuestionPublic(
            question_id=q.question_id,
            question=q.question,
            options=q.options,
        )
        for q in _QUESTIONS
    ]
    return EducationQuestionsResponse(items=items)


@router.post("/submit-test", response_model=SubmitTestResponse)
async def submit_education_test(req: SubmitTestRequest):
    total = len(_QUESTIONS)
    if total == 0:
        return SubmitTestResponse(total=0, correct=0, score=0.0, passed=False, details=[])

    details = []
    correct = 0
    for question in _QUESTIONS:
        selected = req.answers.get(question.question_id)
        is_correct = selected == question.answer
        if is_correct:
            correct += 1

        details.append(
            {
                "question_id": question.question_id,
                "selected": selected,
                "correct_answer": question.answer,
                "is_correct": is_correct,
                "explanation": question.explanation,
            }
        )

    score = round((correct / total) * 100, 2)
    return SubmitTestResponse(
        total=total,
        correct=correct,
        score=score,
        passed=score >= 60,
        details=details,
    )
