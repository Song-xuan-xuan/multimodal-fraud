from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.news import NewsArticle


async def get_news_by_ids(db: AsyncSession, news_ids: list[str]) -> dict[str, NewsArticle]:
    if not news_ids:
        return {}

    unique_ids = list(dict.fromkeys([news_id for news_id in news_ids if news_id]))
    if not unique_ids:
        return {}

    result = await db.execute(select(NewsArticle).where(NewsArticle.news_id.in_(unique_ids)))
    items = result.scalars().all()
    return {item.news_id: item for item in items}

async def list_news(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 10,
    keyword: str | None = None,
    province: str | None = None,
    label: str | None = None,
    platform: str | None = None,
):
    query = select(NewsArticle)
    count_query = select(func.count()).select_from(NewsArticle)

    if keyword:
        filter_cond = or_(
            NewsArticle.title.contains(keyword),
            NewsArticle.content.contains(keyword),
        )
        query = query.where(filter_cond)
        count_query = count_query.where(filter_cond)

    if province:
        query = query.where(NewsArticle.location.contains(province))
        count_query = count_query.where(NewsArticle.location.contains(province))

    if label:
        query = query.where(NewsArticle.label == label)
        count_query = count_query.where(NewsArticle.label == label)

    if platform:
        query = query.where(NewsArticle.platform.contains(platform))
        count_query = count_query.where(NewsArticle.platform.contains(platform))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    items = result.scalars().all()

    return items, total

async def get_news(db: AsyncSession, news_id: str) -> NewsArticle | None:
    result = await db.execute(select(NewsArticle).where(NewsArticle.news_id == news_id))
    return result.scalar_one_or_none()