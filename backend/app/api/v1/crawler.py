import asyncio
import logging

from fastapi import APIRouter, HTTPException, Query

from app.schemas.crawler import CrawlerListResponse, CrawlerNewsItem, CrawlerSearchResponse
from app.services.crawler_service import crawl_all_news, search_news_by_keyword

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/latest", response_model=CrawlerListResponse)
async def get_latest_news():
    """获取首页实时新闻（多平台爬取）"""
    try:
        news_list = await asyncio.to_thread(crawl_all_news)
        return CrawlerListResponse(
            news=[CrawlerNewsItem(**item) for item in news_list],
            total=len(news_list),
        )
    except Exception as e:
        logger.error("爬取实时新闻失败: %s", e)
        raise HTTPException(status_code=500, detail="获取实时新闻失败")


@router.get("/search", response_model=CrawlerSearchResponse)
async def search_crawler_news(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    platform: str = Query("all", description="平台: all/baidu/sogou/cctv/chinanews"),
):
    """按关键词搜索多平台新闻"""
    try:
        result = await asyncio.to_thread(search_news_by_keyword, keyword, platform)
        return CrawlerSearchResponse(
            news=[CrawlerNewsItem(**item) for item in result["news"]],
            stats=result["stats"],
        )
    except Exception as e:
        logger.error("搜索新闻失败: %s", e)
        raise HTTPException(status_code=500, detail="搜索新闻失败")
