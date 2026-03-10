from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.base import get_db
from app.db.models.news import NewsArticle
from app.schemas.news import (
    KnowledgeGraphResponse,
    NewsAnalyzeRequest,
    NewsAnalyzeResponse,
    NewsDetailResponse,
    NewsListResponse,
    NewsResponse,
    NewsSearchRequest,
    NewsTimelineRequest,
    NewsTimelineResponse,
    TimelineEvent,
)
from app.services.news_service import build_knowledge_graph, get_news_aggregated_detail, get_news_detail, normalize_credibility_dimensions, search_news

router = APIRouter()


@router.get("/stats")
async def get_news_stats(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count()).select_from(NewsArticle))).scalar() or 0
    fake = (
        await db.execute(
            select(func.count())
            .select_from(NewsArticle)
            .where(NewsArticle.label.ilike("%谣%") | NewsArticle.label.ilike("%假%") | NewsArticle.label.ilike("%fake%"))
        )
    ).scalar() or 0
    verified = (
        await db.execute(select(func.count()).select_from(NewsArticle).where(NewsArticle.verified == True))
    ).scalar() or 0
    pending = total - fake - verified if total > fake + verified else 0
    return {"total": total, "fake": fake, "verified": verified, "pending": pending}


@router.get("/", response_model=NewsListResponse)
async def list_news_api(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    keyword: str | None = Query(None),
    province: str | None = Query(None),
    label: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await search_news(db, page, per_page, keyword, province, label)
    news_items = []
    for item in result["items"]:
        news_items.append(_to_response(item))
    return NewsListResponse(
        items=news_items,
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        total_pages=result["total_pages"],
    )


@router.get("/aggregate", response_model=NewsListResponse)
async def aggregate_news_api(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    keyword: str | None = Query(None),
    province: str | None = Query(None),
    label: str | None = Query(None),
    platform: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await search_news(db, page, per_page, keyword, province, label, platform)
    news_items = []
    for item in result["items"]:
        news_items.append(_to_response(item))
    return NewsListResponse(
        items=news_items,
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        total_pages=result["total_pages"],
    )


@router.get("/{news_id}/graph", response_model=KnowledgeGraphResponse)
async def get_news_graph_api(
    news_id: str,
    depth: int = Query(default=2, ge=1, le=3),
    max_nodes: int = Query(default=60, ge=10, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Build a multi-hop knowledge graph from a seed news article."""
    try:
        return await build_knowledge_graph(db, news_id, max_depth=depth, max_nodes=max_nodes)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{news_id}/detail", response_model=NewsDetailResponse)
async def get_news_detail_api(news_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await get_news_aggregated_detail(db, news_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_api(news_id: str, db: AsyncSession = Depends(get_db)):
    try:
        news = await get_news_detail(db, news_id)
        return _to_response(news)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


def _to_response(item) -> NewsResponse:
    from app.schemas.news import CredibilityDimensionScores, CredibilityInfo

    dims = normalize_credibility_dimensions(item.credibility_dimensions or {})
    return NewsResponse(
        news_id=item.news_id,
        title=item.title or "",
        content=item.content or "",
        url=item.url or "",
        pic_url=item.pic_url or "",
        label=item.label or "未知",
        platform=item.platform or "",
        hashtag=item.hashtag or "",
        summary=item.summary or "",
        location=item.location or "",
        conclusion=item.conclusion or "",
        publish_time=item.publish_time or "",
        check_time=item.check_time or "",
        iscredit=item.iscredit or False,
        credibility=CredibilityInfo(
            score=item.credibility_score or 0.0,
            dimension_scores=CredibilityDimensionScores(**dims) if dims else CredibilityDimensionScores(),
            verification_progress=item.verification_progress or 0,
            verified=item.verified or False,
        ),
        propagation_data=item.propagation_data or {},
        relations_data=item.relations_data or {},
    )


@router.post("/search", response_model=NewsListResponse)
async def search_news_api(
    req: NewsSearchRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    result = await search_news(db, 1, 20, req.keyword)
    news_items = [_to_response(item) for item in result["items"]]
    return NewsListResponse(
        items=news_items,
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
        total_pages=result["total_pages"],
    )


@router.post("/analyze", response_model=NewsAnalyzeResponse)
async def analyze_news_api(
    req: NewsAnalyzeRequest,
    user=Depends(get_current_user),
):
    import asyncio

    text = req.content or req.title or ""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Title or content is required")

    # Simple keyword extraction and sentiment analysis
    def _analyze(text: str) -> dict:
        import re

        # Basic keyword extraction (top frequency words, filtering short/stop words)
        words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        word_freq: dict[str, int] = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1
        keywords = sorted(word_freq, key=word_freq.get, reverse=True)[:10]

        # Simple sentiment heuristic
        negative_words = ["假", "谣", "虚假", "欺骗", "造假", "骗", "危险", "死亡", "恐怖", "灾难"]
        positive_words = ["真实", "可信", "权威", "官方", "证实", "安全", "成功", "进步"]
        neg_count = sum(1 for w in negative_words if w in text)
        pos_count = sum(1 for w in positive_words if w in text)

        if neg_count > pos_count:
            sentiment = "negative"
            sentiment_score = -min(neg_count / 10, 1.0)
        elif pos_count > neg_count:
            sentiment = "positive"
            sentiment_score = min(pos_count / 10, 1.0)
        else:
            sentiment = "neutral"
            sentiment_score = 0.0

        text_len = len(text)
        if text_len > 2000:
            impact = "high"
        elif text_len > 500:
            impact = "medium"
        else:
            impact = "low"

        return {
            "title": req.title or text[:50],
            "keywords": keywords,
            "sentiment": sentiment,
            "sentiment_score": round(sentiment_score, 2),
            "summary": text[:200] + "..." if len(text) > 200 else text,
            "related_count": 0,
            "impact_level": impact,
            "details": {"word_count": len(words), "char_count": text_len},
        }

    result = await asyncio.to_thread(_analyze, text)
    return NewsAnalyzeResponse(**result)


@router.post("/timeline", response_model=NewsTimelineResponse)
async def news_timeline_api(
    req: NewsTimelineRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    # If news_id provided, get propagation data from DB
    if req.news_id:
        news_result = await db.execute(
            select(NewsArticle).where(NewsArticle.news_id == req.news_id)
        )
        news = news_result.scalar_one_or_none()
        if not news:
            raise HTTPException(status_code=404, detail=f"News {req.news_id} not found")

        prop_data = news.propagation_data or {}
        timeline_raw = prop_data.get("timeline", [])
        timeline = [
            TimelineEvent(
                timestamp=e.get("timestamp", ""),
                platform=e.get("platform", ""),
                description=e.get("description", ""),
                shares=e.get("shares", 0),
            )
            for e in timeline_raw
        ]
        return NewsTimelineResponse(
            news_id=news.news_id,
            title=news.title or "",
            timeline=timeline,
            platform_similarity=prop_data.get("platform_similarity", {}),
        )

    # Fallback: return empty timeline
    return NewsTimelineResponse(
        news_id=req.news_id,
        title=req.title or "",
        timeline=[],
        platform_similarity={},
    )