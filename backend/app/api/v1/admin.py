from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_admin_user
from app.db.base import get_db
from app.db.models.news import NewsArticle
from app.db.models.report import Report
from app.db.models.user import User
from app.services.knowledge_service import create_knowledge_from_report, serialize_knowledge_item

router = APIRouter()


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db), user=Depends(get_current_admin_user)):
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    total_news = (await db.execute(select(func.count()).select_from(NewsArticle))).scalar() or 0
    total_fake = (
        await db.execute(
            select(func.count())
            .select_from(NewsArticle)
            .where(NewsArticle.label.ilike("%谣%") | NewsArticle.label.ilike("%假%") | NewsArticle.label.ilike("%fake%"))
        )
    ).scalar() or 0
    total_verified = (
        await db.execute(select(func.count()).select_from(NewsArticle).where(NewsArticle.verified == True))
    ).scalar() or 0
    pending_evidence = (
        await db.execute(select(func.count()).select_from(Report).where(Report.status == "pending"))
    ).scalar() or 0

    return {
        "total_users": total_users,
        "total_news": total_news,
        "total_fake": total_fake,
        "total_verified": total_verified,
        "pending_reviews": pending_evidence,
    }


@router.get("/submissions")
async def list_submissions(db: AsyncSession = Depends(get_db), user=Depends(get_current_admin_user)):
    result = await db.execute(select(Report).order_by(Report.created_at.desc()).limit(100))
    items = result.scalars().all()
    return {
        "items": [
            {
                "id": item.id,
                "report_id": item.report_id,
                "type": item.type,
                "url": item.url or "",
                "description": item.description,
                "reported_by": item.reported_by or "",
                "status": item.status,
                "review_reason": item.review_reason or "",
                "reviewed_by": item.reviewed_by or "",
                "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else "",
                "created_at": item.created_at.isoformat(),
            }
            for item in items
        ],
        "total": len(items),
    }


@router.post("/submissions/{submission_id}/review")
async def review_submission(
    submission_id: int,
    req: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_admin_user),
):
    result = await db.execute(select(Report).where(Report.id == submission_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="举报记录不存在")

    item.status = req.get("status", item.status)
    item.review_reason = req.get("reason") or None
    item.reviewed_by = user.username
    item.reviewed_at = datetime.now(timezone.utc)
    await db.flush()

    return {
        "message": "审核完成",
        "item": {
            "id": item.id,
            "report_id": item.report_id,
            "type": item.type,
            "url": item.url or "",
            "description": item.description,
            "reported_by": item.reported_by or "",
            "status": item.status,
            "review_reason": item.review_reason or "",
            "reviewed_by": item.reviewed_by or "",
            "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else "",
            "created_at": item.created_at.isoformat(),
        },
    }


@router.post("/submissions/{submission_id}/promote-to-knowledge")
async def promote_submission_to_knowledge(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_admin_user),
):
    try:
        knowledge_item = await create_knowledge_from_report(db, submission_id, submitted_by=user.username)
        return {
            "message": "举报已加入知识库候选列表",
            "item": serialize_knowledge_item(knowledge_item),
        }
    except HTTPException:
        raise
