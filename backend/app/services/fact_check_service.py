"""Fact-checking service.

Provides fact verification by searching for corroborating or contradicting
evidence and computing a credibility verdict.
"""

import logging
from typing import Any, Dict, List

import requests

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _serpapi_search(query: str, api_key: str, use_advanced: bool = False) -> List[Dict[str, Any]]:
    """Search using SerpAPI."""
    try:
        response = requests.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google",
                "api_key": api_key,
                "q": query,
                "hl": "zh-cn",
                "gl": "cn",
                "num": 10 if use_advanced else 6,
            },
            timeout=12,
        )
        if response.status_code != 200:
            logger.warning("SerpAPI search returned %s", response.status_code)
            return []

        payload = response.json()
        return [
            {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": item.get("source", "SerpAPI"),
            }
            for item in payload.get("organic_results", [])
            if item.get("title") or item.get("snippet")
        ]
    except Exception as exc:
        logger.error("SerpAPI search error: %s", exc)
        return []


def _google_search(query: str, api_key: str, engine_id: str) -> List[Dict[str, Any]]:
    """Compatibility fallback using Google Custom Search API."""
    try:
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key": api_key, "cx": engine_id, "q": query, "num": 10},
            timeout=10,
        )
        if response.status_code == 200:
            return [
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "Google Search",
                }
                for item in response.json().get("items", [])
            ]
    except Exception as exc:
        logger.error("Google search error: %s", exc)
    return []


def _get_search_results(query: str, use_advanced: bool = False) -> List[Dict[str, Any]]:
    settings = get_settings()
    if settings.SERPAPI_API_KEY:
        return _serpapi_search(query, settings.SERPAPI_API_KEY, use_advanced=use_advanced)
    if settings.SEARCH_API_KEY and settings.SEARCH_ENGINE_ID:
        return _google_search(query, settings.SEARCH_API_KEY, settings.SEARCH_ENGINE_ID)
    return []


def _has_search_provider() -> bool:
    settings = get_settings()
    return bool(settings.SERPAPI_API_KEY or (settings.SEARCH_API_KEY and settings.SEARCH_ENGINE_ID))


def _extract_main_claim(text: str) -> str:
    text = " ".join(text.split())
    if len(text) <= 100:
        return text
    for index in range(80, min(150, len(text))):
        if text[index] in ".。!！?？":
            return text[: index + 1]
    return text[:100]


def _calc_relevance(snippet: str, query: str) -> float:
    if not snippet or not query:
        return 0.0
    snippet_words = set(snippet.lower().split())
    query_words = set(query.lower().split())
    common = snippet_words & query_words
    if not snippet_words or not query_words:
        return 0.0
    jaccard = len(common) / (len(snippet_words) + len(query_words) - len(common))
    return min(1.0, 0.5 + jaccard * 0.5)


def _calc_support(snippet: str) -> float:
    support_words = ["证实", "确认", "证明", "支持", "表明", "显示", "的确", "确实", "正确"]
    oppose_words = ["否认", "反驳", "质疑", "不实", "虚假", "错误", "谣言", "不正确", "假的"]
    support_count = sum(1 for word in support_words if word in snippet)
    oppose_count = sum(1 for word in oppose_words if word in snippet)
    if support_count == 0 and oppose_count == 0:
        return 0.5
    if oppose_count == 0:
        return min(0.8, 0.5 + 0.1 * support_count)
    if support_count == 0:
        return max(0.2, 0.5 - 0.1 * oppose_count)
    return 0.3 + support_count / (support_count + oppose_count) * 0.4


async def check_fact(text: str, use_advanced: bool = False) -> dict:
    """Fact-check a suspicious claim or promise."""
    if not text or not text.strip():
        return {
            "query": text,
            "verdict": "未知",
            "confidence": 0.0,
            "explanation": "输入内容为空，无法进行风险话术核验。",
            "sources": [],
        }

    try:
        if not _has_search_provider():
            return {
                "query": text,
                "verdict": "不可用",
                "confidence": 0.0,
                "explanation": "风险核验服务不可用：未配置检索提供商（SERPAPI_API_KEY 或 SEARCH_API_KEY/SEARCH_ENGINE_ID）。",
                "sources": [],
                "evidence_unavailable": True,
            }

        search_results = _get_search_results(text, use_advanced=use_advanced)
        main_claim = _extract_main_claim(text)

        evidence = []
        support_scores = []
        for result in search_results[:5]:
            snippet = result.get("snippet", "")
            relevance = _calc_relevance(snippet, text)
            support = _calc_support(snippet)
            support_scores.append(support)
            evidence.append({
                "title": result.get("title", ""),
                "url": result.get("link", ""),
                "snippet": snippet,
                "relevance": relevance,
            })

        if not evidence:
            verdict = "待复核"
            confidence = 0.3
        else:
            supporting = sum(1 for score in support_scores if score > 0.5)
            ratio = supporting / len(support_scores)
            if ratio > 0.7:
                verdict = "低风险"
                confidence = 0.7 + (ratio - 0.7) * 0.3
            elif ratio < 0.3:
                verdict = "高风险"
                confidence = 0.7 + (0.3 - ratio) * 0.3
            else:
                verdict = "存在风险"
                confidence = 0.5 + (ratio - 0.5) * 0.4

        if verdict == "低风险":
            explanation = f"声明\"{main_claim}\"暂未发现明显诈骗风险信号，但仍建议继续核验对方身份和资金诉求。"
        elif verdict == "高风险":
            explanation = f"声明\"{main_claim}\"存在明显风险信号，多个来源或规则提示需提高警惕。"
        else:
            explanation = f"声明\"{main_claim}\"存在一定风险或争议信息，建议继续复核后再做决策。"

        return {
            "query": text,
            "verdict": verdict,
            "confidence": float(confidence),
            "explanation": explanation,
            "sources": evidence,
            "evidence_unavailable": False,
        }

    except Exception as exc:
        logger.error("Fact check error: %s", exc)
        return {
            "query": text,
            "verdict": "不可用",
            "confidence": 0.0,
            "explanation": f"风险核验过程出错: {exc}",
            "sources": [],
            "evidence_unavailable": True,
        }
