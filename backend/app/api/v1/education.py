from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.deps import get_current_user
from app.schemas.education import (
    EducationCoachRequest,
    EducationCoachResponse,
    EducationQuestionsResponse,
    EducationStage,
    EducationStageDetailResponse,
    SubmitTestRequest,
    SubmitTestResponse,
)
from app.services.education_service import (
    coach_reply,
    get_question_batch,
    get_stage_detail,
    get_stages,
    submit_test_answers,
)

router = APIRouter()


@router.get("/stages", response_model=list[EducationStage])
async def get_education_stages():
    return get_stages()


@router.get("/stage/{stage_id}", response_model=EducationStageDetailResponse)
async def get_education_stage(stage_id: str):
    detail = get_stage_detail(stage_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"学习阶段 {stage_id} 不存在")
    return detail


@router.get("/questions", response_model=EducationQuestionsResponse)
async def get_education_questions(
    count: int = Query(default=5, ge=1, le=10),
    stage_id: str | None = Query(default=None),
    refresh: bool = Query(default=False),
):
    items = await get_question_batch(count=count, stage_id=stage_id, refresh=refresh)
    return EducationQuestionsResponse(items=items, total=len(items))


@router.post("/submit-test", response_model=SubmitTestResponse)
async def submit_education_test(req: SubmitTestRequest, user=Depends(get_current_user)):
    username = getattr(user, "username", None) or "anonymous"
    return await submit_test_answers(req.question_ids, req.answers, username=username)


@router.post("/coach", response_model=EducationCoachResponse)
async def education_coach(req: EducationCoachRequest, user=Depends(get_current_user)):
    _ = getattr(user, "username", None) or "anonymous"
    return await coach_reply(
        question=req.question,
        stage_id=req.stage_id,
        score=req.score,
        wrong_topics=req.wrong_topics,
    )
