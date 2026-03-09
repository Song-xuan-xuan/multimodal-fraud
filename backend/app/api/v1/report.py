from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.base import get_db
from app.db.models.evidence import Evidence
from app.db.models.news import NewsArticle
from app.db.models.report import Report
from app.schemas.report import (
    ReportExportResponse,
    ReportListResponse,
    ReportReviewRequest,
    ReportReviewResponse,
    ReportSubmitRequest,
    ReportSubmitResponse,
)

router = APIRouter()


@router.post("/submit", response_model=ReportSubmitResponse)
async def submit_report(
    req: ReportSubmitRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    report_id = f"rpt_{uuid4().hex[:12]}"
    report = Report(
        report_id=report_id,
        type=req.type,
        url=req.url,
        description=req.description,
        reported_by=user.username,
        status="pending",
        created_at=datetime.now(timezone.utc),
    )
    db.add(report)
    await db.flush()
    return ReportSubmitResponse(report_id=report_id, message="举报提交成功")


@router.get("/my", response_model=ReportListResponse)
async def list_my_reports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    base_query = select(Report).where(Report.reported_by == user.username)

    if type:
        base_query = base_query.where(Report.type == type)
    if status:
        base_query = base_query.where(Report.status == status)
    if keyword:
        kw = f"%{keyword.strip()}%"
        if kw != "%%":
            base_query = base_query.where(Report.description.ilike(kw))

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    effective_page = min(page, total_pages) if total_pages > 0 else 1

    offset = (effective_page - 1) * page_size
    q = await db.execute(base_query.order_by(desc(Report.created_at)).offset(offset).limit(page_size))
    items = q.scalars().all()

    return ReportListResponse(
        items=[
            {
                "id": r.id,
                "report_id": r.report_id,
                "type": r.type,
                "url": r.url or "",
                "description": r.description,
                "reported_by": r.reported_by or "",
                "status": r.status,
                "review_reason": r.review_reason or "",
                "reviewed_by": r.reviewed_by or "",
                "reviewed_at": r.reviewed_at.isoformat() if r.reviewed_at else "",
                "created_at": r.created_at.isoformat(),
            }
            for r in items
        ],
        total=total,
        page=effective_page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/export/{news_id}", response_model=ReportExportResponse)
async def export_report(news_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    news_result = await db.execute(select(NewsArticle).where(NewsArticle.news_id == news_id))
    news = news_result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail=f"新闻 {news_id} 不存在")

    evidence_result = await db.execute(select(Evidence).where(Evidence.news_id == news_id))
    evidences = evidence_result.scalars().all()

    evidence_list = [
        {
            "id": item.id,
            "content": item.content,
            "source": item.source or "",
            "submitted_by": item.submitted_by or "",
            "submitted_at": item.submitted_at.isoformat(),
            "status": item.status,
        }
        for item in evidences
    ]

    return ReportExportResponse(
        news_id=news.news_id,
        title=news.title or "",
        label=news.label or "",
        location=news.location or "",
        platform=news.platform or "",
        publish_time=news.publish_time or "",
        summary=news.summary or "",
        conclusion=news.conclusion or "",
        evidence_count=len(evidence_list),
        evidences=evidence_list,
    )


@router.get("/admin/submissions", response_model=ReportListResponse)
async def list_report_submissions(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Report).where(Report.status == "pending").order_by(desc(Report.created_at)).limit(50))
    items = result.scalars().all()
    return ReportListResponse(
        items=[
            {
                "id": r.id,
                "report_id": r.report_id,
                "type": r.type,
                "url": r.url or "",
                "description": r.description,
                "reported_by": r.reported_by or "",
                "status": r.status,
                "review_reason": r.review_reason or "",
                "reviewed_by": r.reviewed_by or "",
                "reviewed_at": r.reviewed_at.isoformat() if r.reviewed_at else "",
                "created_at": r.created_at.isoformat(),
            }
            for r in items
        ],
        total=len(items),
        page=1,
        page_size=50,
        total_pages=1,
    )


@router.post("/admin/submissions/{submission_id}/review", response_model=ReportReviewResponse)
async def review_report_submission(
    submission_id: int,
    req: ReportReviewRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Report).where(Report.id == submission_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="举报记录不存在")

    report.status = req.status
    report.review_reason = req.reason or None
    report.reviewed_by = user.username
    report.reviewed_at = datetime.now(timezone.utc)
    await db.flush()

    item = {
        "id": report.id,
        "report_id": report.report_id,
        "type": report.type,
        "url": report.url or "",
        "description": report.description,
        "reported_by": report.reported_by or "",
        "status": report.status,
        "review_reason": report.review_reason or "",
        "reviewed_by": report.reviewed_by or "",
        "reviewed_at": report.reviewed_at.isoformat() if report.reviewed_at else "",
        "created_at": report.created_at.isoformat(),
    }
    return ReportReviewResponse(message="审核完成", item=item)
