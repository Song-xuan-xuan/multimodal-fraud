import math
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.news_repo import get_news, get_news_by_ids, list_news
from app.schemas.news import (
    CredibilityDimensionScores,
    CredibilityInfo,
    NewsDetailResponse,
    NewsDetailUIFallbacks,
    PropagationInfo,
    PropagationPlatformItem,
    PropagationRegionItem,
    PropagationTrendPoint,
    RelatedNewsItem,
    RelationEdge,
    RelationNode,
    RelationsInfo,
)


async def search_news(
    db: AsyncSession,
    page: int,
    per_page: int,
    keyword: str | None = None,
    province: str | None = None,
    label: str | None = None,
    platform: str | None = None,
):
    items, total = await list_news(db, page, per_page, keyword, province, label, platform)
    total_pages = math.ceil(total / per_page) if per_page > 0 else 0
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_text(value: str | None, fallback: str = "") -> str:
    return value if isinstance(value, str) and value.strip() else fallback


def _collect_region_distribution(timeline: list[dict[str, Any]]) -> list[PropagationRegionItem]:
    region_count: dict[str, int] = {}
    for item in timeline:
        geo_distribution = item.get("geo_distribution") or {}
        if not isinstance(geo_distribution, dict):
            continue

        for region, count in geo_distribution.items():
            region_name = str(region or "")
            if not region_name:
                continue
            region_count[region_name] = region_count.get(region_name, 0) + _to_int(count)

    return [
        PropagationRegionItem(region=region, count=count)
        for region, count in sorted(region_count.items(), key=lambda x: x[1], reverse=True)
    ]


def _build_relations(
    news: Any,
    related_articles_by_id: dict[str, Any],
    related_ids: list[str],
) -> RelationsInfo:
    relations_raw = news.relations_data or {}
    if not isinstance(relations_raw, dict):
        relations_raw = {}

    knowledge_nodes = relations_raw.get("knowledge_nodes") or []
    nodes = [
        RelationNode(
            node_id=f"knowledge:{idx}",
            name=str(name or ""),
            category="knowledge",
            value=1.0,
        )
        for idx, name in enumerate(knowledge_nodes)
        if str(name or "")
    ]

    related_news: list[RelatedNewsItem] = []
    edges: list[RelationEdge] = []

    for related_id in related_ids:
        article = related_articles_by_id.get(related_id)
        if article:
            related_news.append(
                RelatedNewsItem(
                    news_id=article.news_id,
                    title=article.title or "",
                    similarity=0.0,
                    platform=article.platform or "",
                    publish_time=article.publish_time or "",
                    url=article.url or "",
                )
            )
        else:
            related_news.append(
                RelatedNewsItem(
                    news_id=related_id,
                    title="",
                    similarity=0.0,
                    platform="",
                    publish_time="",
                    url="",
                )
            )

        edges.append(
            RelationEdge(
                source=news.news_id,
                target=related_id,
                relation_type="related_rumor",
                weight=1.0,
            )
        )

    return RelationsInfo(related_news=related_news, nodes=nodes, edges=edges)


async def get_news_aggregated_detail(db: AsyncSession, news_id: str) -> NewsDetailResponse:
    news = await get_news(db, news_id)
    if not news:
        raise ValueError("新闻不存在")

    credibility_dimensions_raw = news.credibility_dimensions or {}
    if not isinstance(credibility_dimensions_raw, dict):
        credibility_dimensions_raw = {}

    propagation_raw = news.propagation_data or {}
    if not isinstance(propagation_raw, dict):
        propagation_raw = {}

    timeline_raw = propagation_raw.get("timeline") or []
    if not isinstance(timeline_raw, list):
        timeline_raw = []

    trend = [
        PropagationTrendPoint(
            timestamp=str(item.get("timestamp", "")),
            value=_to_int(item.get("shares", 0)),
        )
        for item in timeline_raw
        if isinstance(item, dict)
    ]

    total_mentions = sum(point.value for point in trend)
    peak_event = max(trend, key=lambda x: x.value, default=PropagationTrendPoint())

    platform_counter: dict[str, int] = {}
    for item in timeline_raw:
        if not isinstance(item, dict):
            continue

        platform_name = str(item.get("platform") or "")
        if not platform_name:
            continue

        platform_counter[platform_name] = platform_counter.get(platform_name, 0) + _to_int(
            item.get("shares", 0)
        )

    platform_distribution: list[PropagationPlatformItem] = []
    for platform_name, count in sorted(platform_counter.items(), key=lambda x: x[1], reverse=True):
        ratio = (count / total_mentions) if total_mentions > 0 else 0.0
        platform_distribution.append(
            PropagationPlatformItem(platform=platform_name, count=count, ratio=round(ratio, 4))
        )

    region_distribution = _collect_region_distribution(timeline_raw)

    relations_raw = news.relations_data or {}
    if not isinstance(relations_raw, dict):
        relations_raw = {}

    related_ids_raw = relations_raw.get("related_rumors") or []
    related_ids = [str(item) for item in related_ids_raw if str(item or "")]
    related_articles_by_id = await get_news_by_ids(db, related_ids)

    relations = _build_relations(news, related_articles_by_id, related_ids)

    return NewsDetailResponse(
        news_id=news.news_id,
        title=news.title or "",
        content=_safe_text(news.content, "暂无内容"),
        url=_safe_text(news.url, "#"),
        pic_url=_safe_text(news.pic_url, ""),
        label=news.label or "未知",
        platform=news.platform or "",
        hashtag=news.hashtag or "",
        summary=_safe_text(news.summary, "暂无摘要"),
        location=news.location or "",
        conclusion=_safe_text(news.conclusion, "暂无结论"),
        publish_time=news.publish_time or "",
        check_time=news.check_time or "",
        iscredit=news.iscredit or False,
        credibility=CredibilityInfo(
            score=_to_float(news.credibility_score, 0.0),
            dimension_scores=CredibilityDimensionScores(**credibility_dimensions_raw)
            if credibility_dimensions_raw
            else CredibilityDimensionScores(),
            verification_progress=_to_int(news.verification_progress, 0),
            verified=news.verified or False,
        ),
        propagation=PropagationInfo(
            total_mentions=total_mentions,
            peak_timestamp=peak_event.timestamp,
            trend=trend,
            platform_distribution=platform_distribution,
            region_distribution=region_distribution,
        ),
        relations=relations,
        ui_fallbacks=NewsDetailUIFallbacks(),
        propagation_data=propagation_raw,
        relations_data=relations_raw,
    )


async def get_news_detail(db: AsyncSession, news_id: str):
    news = await get_news(db, news_id)
    if not news:
        raise ValueError("新闻不存在")
    return news
