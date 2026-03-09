"""
多平台新闻爬虫服务 — 从各大新闻平台抓取实时新闻
"""

import logging
import random
import re
import time
import urllib.parse
from datetime import datetime
from typing import Any

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;"
        "q=0.8,application/signed-exchange;v=b3;q=0.7"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
}

# ---------------------------------------------------------------------------
# 各平台爬取
# ---------------------------------------------------------------------------


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text.strip())


def _random_delay() -> None:
    time.sleep(random.uniform(0.3, 1.0))


def _make_item(
    title: str,
    url: str,
    source: str,
    summary: str = "",
    publish_time: str = "",
) -> dict[str, Any]:
    title = _clean_text(title)
    if len(title) > 100:
        title = title[:97] + "..."
    return {
        "title": title,
        "url": url,
        "source": source,
        "summary": _clean_text(summary) or "暂无摘要",
        "publish_time": publish_time or datetime.now().strftime("%Y-%m-%d"),
    }


# ---- 百度新闻 ----
def _crawl_baidu(keyword: str) -> list[dict[str, Any]]:
    try:
        encoded = urllib.parse.quote(keyword)
        url = f"https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&word={encoded}"
        headers = {
            **_HEADERS,
            "Referer": "https://www.baidu.com",
            "Host": "www.baidu.com",
            "Cookie": "BAIDUID=" + "".join(random.choices("0123456789ABCDEF", k=32)),
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        items = soup.select(".result") or soup.select(".c-container")
        results: list[dict[str, Any]] = []
        for item in items[:10]:
            title_el = item.select_one("h3 a")
            if not title_el or not title_el.text.strip():
                continue
            summary_el = item.select_one(".c-summary")
            time_el = item.select_one(".c-author")
            results.append(
                _make_item(
                    title=title_el.text,
                    url=title_el.get("href", ""),
                    source="百度新闻",
                    summary=summary_el.text if summary_el else "",
                    publish_time=time_el.text.strip() if time_el else "",
                )
            )
        return results
    except Exception as e:
        logger.warning("百度新闻搜索出错: %s", e)
        return []


# ---- 搜狗新闻 ----
def _crawl_sogou(keyword: str) -> list[dict[str, Any]]:
    try:
        encoded = urllib.parse.quote(keyword)
        url = f"https://www.sogou.com/web?query={encoded}&ie=utf8"
        headers = {
            **_HEADERS,
            "Referer": "https://www.sogou.com",
            "Host": "www.sogou.com",
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        results: list[dict[str, Any]] = []
        for item in soup.select(".vrwrap"):
            title_el = item.select_one("h3 a")
            if not title_el:
                continue
            href = title_el.get("href", "")
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                href = "https://www.sogou.com" + href
            summary_el = item.select_one(".text-layout")
            info_el = item.select_one(".news-info")
            results.append(
                _make_item(
                    title=title_el.text,
                    url=href,
                    source="搜狗新闻",
                    summary=summary_el.text if summary_el else "",
                    publish_time=info_el.text.strip() if info_el else "",
                )
            )
        return results[:10]
    except Exception as e:
        logger.warning("搜狗新闻搜索出错: %s", e)
        return []


# ---- 央视网 ----
def _crawl_cctv(keyword: str) -> list[dict[str, Any]]:
    try:
        params = {"qtext": keyword, "sort": "date", "type": "web", "page": 1}
        headers = {**_HEADERS, "Referer": "https://search.cctv.com", "Host": "search.cctv.com"}
        resp = requests.get(
            "https://search.cctv.com/search.php", params=params, headers=headers, timeout=10
        )
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.find_all("li", class_="image")

        results: list[dict[str, Any]] = []
        for item in items[:10]:
            title_tag = item.find("a", id=lambda x: x and x.startswith("web_content_"))
            if not title_tag:
                continue
            encoded_link = title_tag["href"]
            match = re.search(r"targetpage=([^&]+)", encoded_link)
            if not match:
                continue
            real_url = urllib.parse.unquote(match.group(1))
            summary_tag = item.find("p", class_="bre")
            source_tag = item.find("span", class_="src")
            time_tag = item.find("span", class_="tim")
            results.append(
                _make_item(
                    title=title_tag.get_text(strip=True),
                    url=real_url,
                    source=source_tag.get_text(strip=True) if source_tag else "央视网",
                    summary=summary_tag.get_text(strip=True) if summary_tag else "",
                    publish_time=time_tag.get_text(strip=True) if time_tag else "",
                )
            )
        return results
    except Exception as e:
        logger.warning("央视网搜索出错: %s", e)
        return []


# ---- 中新网 ----
def _crawl_chinanews(keyword: str) -> list[dict[str, Any]]:
    try:
        import json as _json

        encoded = urllib.parse.quote(keyword)
        url = f"https://sou.chinanews.com.cn/search.do?q={encoded}"
        headers = {
            **_HEADERS,
            "Referer": "https://sou.chinanews.com.cn",
            "Host": "sou.chinanews.com.cn",
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        script_text = soup.find("script", text=re.compile("var docArr"))

        results: list[dict[str, Any]] = []
        if script_text and script_text.string:
            m = re.search(r"var docArr = (\[.*?\]);", script_text.string)
            if m:
                data = _json.loads(m.group(1))
                for item in data[:10]:
                    title = item.get("title", "")
                    if isinstance(title, list):
                        title = " ".join(str(t) for t in title)
                    title = str(title).replace("<em>", "").replace("</em>", "")
                    content = item.get("content_without_tag", "")
                    if isinstance(content, list):
                        content = " ".join(str(c) for c in content)
                    content = str(content).replace("<em>", "").replace("</em>", "")
                    item_url = item.get("url", "")
                    if title and item_url:
                        results.append(
                            _make_item(
                                title=title,
                                url=item_url,
                                source="中新网",
                                summary=content,
                                publish_time=item.get("pubtime", ""),
                            )
                        )
        return results
    except Exception as e:
        logger.warning("中新网搜索出错: %s", e)
        return []


# ---- 新华网 ----
def _crawl_xinhua() -> list[dict[str, Any]]:
    try:
        url = "http://www.news.cn/tech/index.htm"
        headers = {**_HEADERS, "Referer": "http://www.news.cn", "Host": "www.news.cn"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        selectors = [".news-list li a", ".content-list li a", "h3 a", ".title a", "a[title]"]
        items: list[Any] = []
        for sel in selectors:
            items = soup.select(sel)
            if items:
                break

        results: list[dict[str, Any]] = []
        for item in items[:10]:
            title = _clean_text(item.get_text())
            href = item.get("href", "")
            if not title or len(title) < 8:
                continue
            if href and not href.startswith("http"):
                if href.startswith("//"):
                    href = "https:" + href
                elif href.startswith("/"):
                    href = "http://www.news.cn" + href
            results.append(
                _make_item(
                    title=title,
                    url=href,
                    source="新华网",
                )
            )
        return results
    except Exception as e:
        logger.warning("新华网搜索出错: %s", e)
        return []


# ---------------------------------------------------------------------------
# 公共接口
# ---------------------------------------------------------------------------

_SAMPLE_NEWS = [
    {
        "title": "我国成功发射新一代人工智能卫星，开启太空智能时代",
        "source": "科技日报",
        "url": "https://www.stdaily.com/",
    },
    {
        "title": "量子计算机在药物研发领域实现重大突破，效率提升千倍",
        "source": "科学网",
        "url": "https://www.sciencenet.cn/",
    },
    {
        "title": "5G网络覆盖率达98%，推动数字经济高质量发展",
        "source": "通信世界",
        "url": "https://www.cww.net.cn/",
    },
    {
        "title": "新型芯片技术问世，功耗降低70%性能提升300%",
        "source": "电子工程世界",
        "url": "https://www.eeworld.com.cn/",
    },
    {
        "title": "虚拟现实技术在教育领域应用普及，学习效果显著提升",
        "source": "教育科技",
        "url": "https://www.jyb.cn/",
    },
    {
        "title": "区块链赋能供应链管理，透明度和效率双重提升",
        "source": "区块链资讯",
        "url": "https://www.8btc.com/",
    },
]


def crawl_all_news() -> list[dict[str, Any]]:
    """爬取所有新闻源（首页实时新闻卡片用）"""
    all_news: list[dict[str, Any]] = []

    # 每次随机选取关键词，让刷新有不同内容
    keywords_pool = ["人工智能", "科技创新", "科技发展", "数字经济", "网络安全", "大数据", "新能源", "量子计算"]
    kw_baidu, kw_cctv, kw_china = random.sample(keywords_pool, 3)

    crawlers: list[tuple[str, Any]] = [
        ("新华网", lambda: _crawl_xinhua()),
        ("百度新闻", lambda: _crawl_baidu(kw_baidu)),
        ("央视网", lambda: _crawl_cctv(kw_cctv)),
        ("中新网", lambda: _crawl_chinanews(kw_china)),
    ]

    for name, fn in crawlers:
        try:
            items = fn()
            all_news.extend(items)
            _random_delay()
        except Exception as e:
            logger.warning("爬取 %s 出错: %s", name, e)

    # 去重
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for news in all_news:
        key = news["title"].strip()
        if key not in seen:
            seen.add(key)
            unique.append(news)

    # 如果全部为空则使用备用数据
    if not unique:
        now_str = datetime.now().strftime("%Y-%m-%d")
        for sample in _SAMPLE_NEWS:
            unique.append(
                _make_item(
                    title=sample["title"],
                    url=sample["url"],
                    source=sample["source"],
                    publish_time=now_str,
                )
            )

    # 随机打乱顺序，让每次刷新呈现不同排列
    random.shuffle(unique)

    return unique


def search_news_by_keyword(keyword: str, platform: str = "all") -> dict[str, Any]:
    """按关键词搜索新闻（聚合搜索页用）"""
    if platform != "all":
        dispatch = {
            "baidu": lambda: _crawl_baidu(keyword),
            "百度新闻": lambda: _crawl_baidu(keyword),
            "sogou": lambda: _crawl_sogou(keyword),
            "搜狗新闻": lambda: _crawl_sogou(keyword),
            "cctv": lambda: _crawl_cctv(keyword),
            "央视网": lambda: _crawl_cctv(keyword),
            "chinanews": lambda: _crawl_chinanews(keyword),
            "中新网": lambda: _crawl_chinanews(keyword),
        }
        fn = dispatch.get(platform)
        news_list = fn() if fn else []
    else:
        news_list = []
        for fn in [
            lambda: _crawl_sogou(keyword),
            lambda: _crawl_baidu(keyword),
            lambda: _crawl_cctv(keyword),
            lambda: _crawl_chinanews(keyword),
        ]:
            try:
                news_list.extend(fn())
                _random_delay()
            except Exception:
                continue

    # 去重
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for n in news_list:
        if n["title"] not in seen:
            seen.add(n["title"])
            unique.append(n)

    # 来源统计
    source_stats: dict[str, int] = {}
    for n in unique:
        source_stats[n["source"]] = source_stats.get(n["source"], 0) + 1

    return {
        "news": unique,
        "stats": {"sources": source_stats, "total": len(unique)},
    }
