from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.base import get_db
from app.db.models.evidence import Evidence
from app.db.models.forum import ForumPost
from app.schemas.community import (
    CreateForumPostRequest,
    ForumPostListResponse,
    ForumPostResponse,
    LeaderboardItem,
    LeaderboardResponse,
    SubmitEvidenceRequest,
)
from app.schemas.evidence import EvidenceItem, EvidenceSubmissionListResponse, MyEvidenceStatsResponse
from app.services.evidence_service import build_user_evidence_stats, serialize_evidence_item

router = APIRouter()

@router.post("/evidence", response_model=EvidenceItem)
async def submit_evidence(
    req: SubmitEvidenceRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    evidence = Evidence(
        news_id=req.news_id,
        content=req.content,
        source=req.source,
        submitted_by=user.username,
    )
    db.add(evidence)
    await db.flush()
    return EvidenceItem(**serialize_evidence_item(evidence))


@router.get("/evidence/my", response_model=EvidenceSubmissionListResponse)
async def list_my_evidence_submissions(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await db.execute(
        select(Evidence)
        .where(Evidence.submitted_by == user.username)
        .order_by(Evidence.submitted_at.desc())
        .limit(200)
    )
    items = result.scalars().all()
    payload = [EvidenceItem(**serialize_evidence_item(item)) for item in items]
    return EvidenceSubmissionListResponse(items=payload, total=len(payload))


@router.get("/evidence/my/stats", response_model=MyEvidenceStatsResponse)
async def get_my_evidence_stats(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    stats = await build_user_evidence_stats(db, user.username)
    return MyEvidenceStatsResponse(**stats)

@router.get("/evidence/{news_id}", response_model=list[EvidenceItem])
async def list_evidence(news_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Evidence).where(Evidence.news_id == news_id).order_by(Evidence.submitted_at.desc())
    )
    evidences = result.scalars().all()
    return [EvidenceItem(**serialize_evidence_item(item)) for item in evidences]

@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Evidence.submitted_by, func.count(Evidence.id))
        .where(Evidence.submitted_by.is_not(None))
        .group_by(Evidence.submitted_by)
        .order_by(func.count(Evidence.id).desc())
        .limit(20)
    )
    items = [
        LeaderboardItem(username=row[0] or "匿名用户", contributions=row[1])
        for row in result.all()
    ]
    return LeaderboardResponse(items=items)


@router.get("/forum/posts", response_model=ForumPostListResponse)
async def list_forum_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ForumPost).order_by(ForumPost.id.desc()).limit(100))
    posts = result.scalars().all()
    items = [
        ForumPostResponse(
            id=p.id,
            title=p.title,
            content=p.content,
            author=p.author,
            created_at=p.created_at.isoformat(),
        )
        for p in posts
    ]
    return ForumPostListResponse(items=items, total=len(items))


@router.post("/forum/posts", response_model=ForumPostResponse)
async def create_forum_post(
    req: CreateForumPostRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    post = ForumPost(title=req.title, content=req.content, author=user.username)
    db.add(post)
    await db.flush()
    return ForumPostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        author=post.author,
        created_at=post.created_at.isoformat(),
    )
