from pydantic import BaseModel


class CrawlerNewsItem(BaseModel):
    title: str
    url: str
    source: str
    summary: str = "暂无摘要"
    publish_time: str = ""


class CrawlerListResponse(BaseModel):
    news: list[CrawlerNewsItem]
    total: int


class CrawlerSearchResponse(BaseModel):
    news: list[CrawlerNewsItem]
    stats: dict
