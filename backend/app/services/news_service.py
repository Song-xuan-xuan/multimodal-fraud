import json
import math
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.news_repo import get_news, get_news_by_ids, list_news
from app.schemas.news import (
    CredibilityDimensionScores,
    CredibilityInfo,
    KnowledgeGraphResponse,
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


def normalize_credibility_dimensions(raw: Any) -> dict[str, float]:
    if not isinstance(raw, dict):
        raw = {}

    keys = ["source", "content", "logic", "propagation", "AI", "content1", "content2"]
    return {key: _to_float(raw.get(key), 0.0) for key in keys}


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

    # 1) Seed node
    nodes = [
        RelationNode(
            node_id=news.news_id,
            name=news.title or "种子新闻",
            category="seed",
            value=20.0,
        )
    ]

    edges: list[RelationEdge] = []

    # 2) Knowledge keyword nodes + edges to seed
    knowledge_nodes = relations_raw.get("knowledge_nodes") or []
    for idx, name in enumerate(knowledge_nodes):
        name_str = str(name or "")
        if not name_str:
            continue
        node_id = f"knowledge:{idx}"
        nodes.append(
            RelationNode(
                node_id=node_id,
                name=name_str,
                category="knowledge",
                value=3.0,
            )
        )
        edges.append(
            RelationEdge(
                source=news.news_id,
                target=node_id,
                relation_type="has_keyword",
                weight=1.0,
            )
        )

    # 3) Related news nodes + edges to seed
    related_news: list[RelatedNewsItem] = []
    for related_id in related_ids:
        article = related_articles_by_id.get(related_id)
        title = article.title or related_id if article else related_id
        platform = article.platform or "" if article else ""

        related_news.append(
            RelatedNewsItem(
                news_id=related_id,
                title=title,
                similarity=0.0,
                platform=platform,
                publish_time=article.publish_time or "" if article else "",
                url=article.url or "" if article else "",
            )
        )
        nodes.append(
            RelationNode(
                node_id=related_id,
                name=title,
                category="related_news",
                value=8.0,
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

    credibility_dimensions_raw = normalize_credibility_dimensions(news.credibility_dimensions or {})

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


async def build_knowledge_graph(
    db: AsyncSession, seed_news_id: str, max_depth: int = 2, max_nodes: int = 60
) -> KnowledgeGraphResponse:
    """Build a multi-hop knowledge graph starting from a seed news article.

    Expands related_rumors and knowledge_nodes for each article up to max_depth layers.
    """
    seed = await get_news(db, seed_news_id)
    if not seed:
        raise ValueError("新闻不存在")

    node_map: dict[str, RelationNode] = {}
    edge_list: list[RelationEdge] = []
    visited: set[str] = set()
    queue: list[tuple[str, int]] = [(seed_news_id, 0)]

    # BFS expansion
    while queue:
        current_id, depth = queue.pop(0)
        if current_id in visited:
            continue
        visited.add(current_id)

        if len(node_map) >= max_nodes:
            break

        # Fetch article
        if current_id == seed_news_id:
            article = seed
        else:
            article = await get_news(db, current_id)
        if not article:
            continue

        # Add news node
        is_seed = current_id == seed_news_id
        if current_id not in node_map:
            node_map[current_id] = RelationNode(
                node_id=current_id,
                name=article.title or current_id,
                category="seed" if is_seed else "news",
                value=20.0 if is_seed else 10.0,
            )

        relations_raw = article.relations_data or {}
        if not isinstance(relations_raw, dict):
            relations_raw = {}

        # Add knowledge keyword nodes + edges
        for idx, kw in enumerate(relations_raw.get("knowledge_nodes") or []):
            kw_str = str(kw or "")
            if not kw_str:
                continue
            # Use keyword text as node_id to merge duplicate keywords across articles
            kw_node_id = f"kw:{kw_str}"
            if kw_node_id not in node_map:
                node_map[kw_node_id] = RelationNode(
                    node_id=kw_node_id,
                    name=kw_str,
                    category="keyword",
                    value=4.0,
                )
            edge_key = (current_id, kw_node_id, "has_keyword")
            edge_list.append(RelationEdge(
                source=current_id, target=kw_node_id,
                relation_type="has_keyword", weight=1.0,
            ))

        # Expand related rumors (if within depth)
        if depth < max_depth:
            related_ids = [
                str(rid) for rid in (relations_raw.get("related_rumors") or []) if str(rid or "")
            ]
            # Pre-fetch related articles
            related_map = await get_news_by_ids(db, related_ids)
            for rid in related_ids:
                rel_article = related_map.get(rid)
                if rid not in node_map and len(node_map) < max_nodes:
                    node_map[rid] = RelationNode(
                        node_id=rid,
                        name=(rel_article.title or rid) if rel_article else rid,
                        category="news",
                        value=8.0,
                    )
                edge_list.append(RelationEdge(
                    source=current_id, target=rid,
                    relation_type="related_rumor", weight=1.0,
                ))
                if rid not in visited:
                    queue.append((rid, depth + 1))

    # Deduplicate edges
    seen_edges: set[tuple[str, str, str]] = set()
    unique_edges: list[RelationEdge] = []
    for e in edge_list:
        key = (e.source, e.target, e.relation_type)
        if key not in seen_edges:
            seen_edges.add(key)
            unique_edges.append(e)

    return KnowledgeGraphResponse(
        seed_news_id=seed_news_id,
        seed_title=seed.title or "",
        nodes=list(node_map.values()),
        edges=unique_edges,
    )
