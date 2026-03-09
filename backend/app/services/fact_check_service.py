"""Fact-checking service.

Provides fact verification by searching for corroborating/contradicting
evidence and computing a credibility verdict.
"""

import json
import logging
import os
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)


# ---------- Search ----------

def _google_search(query: str, api_key: str, engine_id: str) -> List[Dict[str, Any]]:
    """Search using Google Custom Search API."""
    try:
        resp = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key": api_key, "cx": engine_id, "q": query, "num": 10},
            timeout=10,
        )
        if resp.status_code == 200:
            return [
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "Google Search",
                }
                for item in resp.json().get("items", [])
            ]
    except Exception as e:
        logger.error("Google search error: %s", e)
    return []


def _get_search_results(query: str) -> List[Dict[str, Any]]:
    api_key = os.environ.get("SEARCH_API_KEY", "")
    engine_id = os.environ.get("SEARCH_ENGINE_ID", "")
    if api_key and engine_id:
        return _google_search(query, api_key, engine_id)
    return []


def _has_search_provider() -> bool:
    api_key = os.environ.get("SEARCH_API_KEY", "")
    engine_id = os.environ.get("SEARCH_ENGINE_ID", "")
    return bool(api_key and engine_id)


# ---------- Analysis helpers ----------

def _extract_main_claim(text: str) -> str:
    text = " ".join(text.split())
    if len(text) <= 100:
        return text
    for i in range(80, min(150, len(text))):
        if text[i] in ".。!！?？":
            return text[: i + 1]
    return text[:100]


def _calc_relevance(snippet: str, query: str) -> float:
    if not snippet or not query:
        return 0.0
    s_words = set(snippet.lower().split())
    q_words = set(query.lower().split())
    common = s_words & q_words
    if not s_words or not q_words:
        return 0.0
    jaccard = len(common) / (len(s_words) + len(q_words) - len(common))
    return min(1.0, 0.5 + jaccard * 0.5)


def _calc_support(snippet: str) -> float:
    support_words = ["证实", "确认", "证明", "支持", "表明", "显示", "的确", "确实", "正确"]
    oppose_words = ["否认", "反驳", "质疑", "不实", "虚假", "错误", "谣言", "不正确", "假的"]
    s = sum(1 for w in support_words if w in snippet)
    o = sum(1 for w in oppose_words if w in snippet)
    if s == 0 and o == 0:
        return 0.5
    if o == 0:
        return min(0.8, 0.5 + 0.1 * s)
    if s == 0:
        return max(0.2, 0.5 - 0.1 * o)
    return 0.3 + s / (s + o) * 0.4


# ---------- Public API ----------

async def check_fact(text: str, use_advanced: bool = False) -> dict:
    """
    Fact-check a news text.

    Args:
        text: The news text to verify.
        use_advanced: Reserved for advanced fact-checking (Perplexica/SearxNG).

    Returns:
        dict with verdict, confidence, explanation, sources, query.
    """
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
                "explanation": "风险核验服务不可用：未配置检索提供商（SEARCH_API_KEY/SEARCH_ENGINE_ID）。",
                "sources": [],
                "evidence_unavailable": True,
            }

        search_results = _get_search_results(text)
        main_claim = _extract_main_claim(text)

        evidence = []
        support_scores = []
        for r in search_results[:5]:
            snippet = r.get("snippet", "")
            relevance = _calc_relevance(snippet, text)
            support = _calc_support(snippet)
            support_scores.append(support)
            evidence.append({
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "snippet": snippet,
                "relevance": relevance,
            })

        # Compute verdict
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

        # Generate explanation
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

    except Exception as e:
        logger.error("Fact check error: %s", e)
        return {
            "query": text,
            "verdict": "不可用",
            "confidence": 0.0,
            "explanation": f"风险核验过程出错: {e}",
            "sources": [],
            "evidence_unavailable": True,
        }
