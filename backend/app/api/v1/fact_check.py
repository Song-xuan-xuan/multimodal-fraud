from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.base import get_db
from app.db.models.fact_check_history import FactCheckHistory
from app.schemas.fact_check import (
    FactCheckEvidenceOnlyRequest,
    FactCheckEvidenceResponse,
    FactCheckHistoryItem,
    FactCheckHistoryResponse,
    FactCheckMultiSourceRequest,
    FactCheckRequest,
    FactCheckResponse,
    FactCheckSaveRequest,
    FactCheckSource,
)
from app.services.fact_check_service import check_fact

router = APIRouter()


@router.post("/check", response_model=FactCheckResponse)
async def fact_check_api(req: FactCheckRequest, user=Depends(get_current_user)):
    result = await check_fact(req.text, req.use_advanced)
    if result.get("evidence_unavailable"):
        raise HTTPException(status_code=503, detail=result.get("explanation", "Fact-check unavailable"))
    return FactCheckResponse(**result)


@router.post("/multi-source", response_model=FactCheckResponse)
async def multi_source_check_api(req: FactCheckMultiSourceRequest, user=Depends(get_current_user)):
    result = await check_fact(req.text, use_advanced=True)
    if req.sources:
        result["explanation"] = (
            f"Checked against sources: {', '.join(req.sources)}. " + result.get("explanation", "")
        )
    return FactCheckResponse(**result)


@router.post("/evidence-only", response_model=FactCheckEvidenceResponse)
async def evidence_only_api(req: FactCheckEvidenceOnlyRequest, user=Depends(get_current_user)):
    result = await check_fact(req.text, use_advanced=True)
    sources = [FactCheckSource(**s) for s in result.get("sources", [])]
    return FactCheckEvidenceResponse(
        query=result.get("query", req.text),
        evidence=sources,
        total_sources=len(sources),
    )


@router.post("/save")
async def save_fact_check_result(
    req: FactCheckSaveRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record_id = f"fc_{uuid4().hex[:12]}"
    row = FactCheckHistory(
        id=record_id,
        query=req.query,
        verdict=req.verdict,
        confidence=req.confidence,
        explanation=req.explanation,
        save_type=req.save_type,
        checked_by=user.username,
        checked_at=datetime.now(timezone.utc),
    )
    db.add(row)
    await db.flush()
    return {"id": record_id, "message": "Result saved"}


@router.get("/history", response_model=FactCheckHistoryResponse)
async def get_fact_check_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    verdict: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    base_query = select(FactCheckHistory).where(FactCheckHistory.checked_by == user.username)

    if verdict:
        base_query = base_query.where(FactCheckHistory.verdict == verdict)
    if keyword:
        kw = f"%{keyword.strip()}%"
        if kw != "%%":
            base_query = base_query.where(FactCheckHistory.query.ilike(kw))

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    effective_page = min(page, total_pages) if total_pages > 0 else 1

    offset = (effective_page - 1) * page_size
    q = await db.execute(base_query.order_by(desc(FactCheckHistory.checked_at)).offset(offset).limit(page_size))
    rows = q.scalars().all()
    items = [
        FactCheckHistoryItem(
            id=r.id,
            query=r.query,
            verdict=r.verdict,
            confidence=r.confidence,
            checked_at=r.checked_at.isoformat(),
        )
        for r in rows
    ]

    return FactCheckHistoryResponse(
        items=items,
        total=total,
        page=effective_page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.delete("/history/{record_id}")
async def delete_fact_check_history(
    record_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row_q = await db.execute(select(FactCheckHistory).where(FactCheckHistory.id == record_id))
    row = row_q.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Record not found")
    if row.checked_by != user.username:
        raise HTTPException(status_code=403, detail="Not your record")
    await db.delete(row)
    return {"message": "Record deleted"}
