"""从项目内置新闻爬虫快速生成白样本(txt)。

目标：为测评集准备 label=0 的“正常新闻文本”样本，带可追溯 source_url。

说明：
- 复用 backend/app/services/crawler_service.py 的搜索聚合能力（新华网/百度/央视/中新网/搜狗等）。
- 尝试用 newspaper3k 抽取正文；抽取失败时回退为爬虫的 summary。
- 会过滤掉明显反诈/诈骗相关的内容，避免白样本混入黑样本语料。

用法示例：
  python scripts/generate_white_samples_from_crawler.py --count 20
  python scripts/generate_white_samples_from_crawler.py --count 20 --keyword "科技创新"
  python scripts/generate_white_samples_from_crawler.py --count 20 --platform "all" --min-chars 300
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
TXT_DIR_DEFAULT = PROJECT_ROOT / "test-dataset" / "txt"

# 让脚本能 import 到 backend/app/...
sys.path.insert(0, str(BACKEND_DIR))

try:
    from app.services.crawler_service import search_news_by_keyword  # type: ignore
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"无法导入爬虫服务，请确认在项目根目录运行。原始错误: {exc}") from exc


FRAUD_KEYWORDS = [
    "诈骗",
    "反诈",
    "电信网络诈骗",
    "刷单",
    "返利",
    "冒充",
    "转账",
    "验证码",
    "刷流水",
    "贷款",
    "征信",
    "投资理财",
    "杀猪盘",
]

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
}

# 很多聚合/跳转页无法稳定抽取正文，默认跳过或尝试解析真实落地 URL
SKIP_URL_SUBSTRINGS = [
    "weixin.sogou.com",
    "www.sogou.com/link",
]

REDIRECT_URL_SUBSTRINGS = [
    "www.baidu.com/s?",
    "www.baidu.com/link?",
]


def _clean_text(text: str) -> str:
    value = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _looks_like_fraud(text: str) -> bool:
    value = (text or "").strip()
    if not value:
        return False
    return any(k in value for k in FRAUD_KEYWORDS)


def _should_skip_url(url: str) -> bool:
    return any(s in (url or "") for s in SKIP_URL_SUBSTRINGS)


def _maybe_resolve_redirect_url(url: str, timeout_sec: int = 15) -> str:
    """将部分聚合跳转 URL 尝试解析为真实落地 URL。

    注意：不是所有跳转都能解析成功，失败时返回原 URL。
    """
    raw_url = (url or "").strip()
    if not raw_url:
        return ""

    if not any(s in raw_url for s in REDIRECT_URL_SUBSTRINGS):
        return raw_url

    try:
        resp = requests.get(
            raw_url,
            headers=REQUEST_HEADERS,
            timeout=timeout_sec,
            allow_redirects=True,
        )
        final_url = (resp.url or "").strip()
        # 某些站点会跳回聚合页或进入验证码页，这里不强行替换
        return final_url or raw_url
    except Exception:
        return raw_url


def _try_extract_article_text_bs4(url: str, timeout_sec: int = 20) -> str:
    """用 BeautifulSoup 的兜底抽取：抓取页面后提取较长段落文本。"""
    if not url:
        return ""
    try:
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=timeout_sec)
        if resp.status_code != 200:
            return ""
        resp.encoding = resp.apparent_encoding or resp.encoding
        html = resp.text or ""
    except Exception:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    for tag in soup.find_all(["img", "video", "audio", "iframe"]):
        tag.decompose()

    # 常见正文容器优先
    selectors = [
        "article",
        "#content",
        "#article-content",
        ".article",
        ".article-content",
        ".content",
        ".content-body",
        ".TRS_Editor",
        ".rich_media_content",
    ]
    roots = []
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            roots.append(el)

    # 如果没命中容器，就用整个 body
    if not roots:
        body = soup.body
        if body:
            roots = [body]
        else:
            return ""

    best_text = ""
    for root in roots:
        parts: list[str] = []
        for p in root.find_all(["p", "h1", "h2", "h3", "li", "blockquote"]):
            t = _clean_text(p.get_text(" ", strip=True))
            if t and len(t) >= 10:
                parts.append(t)
        text = _clean_text(" ".join(parts))
        if len(text) > len(best_text):
            best_text = text
    return best_text


def _try_extract_article_text(url: str, timeout_sec: int = 20) -> str:
    """优先 newspaper3k 抽取正文；失败返回空串。"""
    if not url:
        return ""

    try:
        from newspaper import Article  # type: ignore
    except Exception:
        return ""

    try:
        article = Article(url, language="zh")
        article.download()
        article.parse()
        return _clean_text(article.text or "")
    except Exception:
        # 站点反爬/跳转/编码等都可能失败，这里直接回退即可
        return ""


def _next_white_index(txt_dir: Path) -> int:
    """计算下一个 TXT_WHITE_XXX 的起始编号，避免覆盖已有文件。"""
    max_idx = 0
    for p in txt_dir.glob("TXT_WHITE_*.txt"):
        m = re.search(r"TXT_WHITE_(\d+)", p.stem.upper())
        if not m:
            continue
        max_idx = max(max_idx, int(m.group(1)))
    return max_idx + 1


@dataclass(frozen=True)
class Candidate:
    title: str
    url: str
    source: str
    summary: str
    publish_time: str


def _to_candidate(item: dict[str, Any]) -> Candidate:
    return Candidate(
        title=str(item.get("title") or ""),
        url=str(item.get("url") or ""),
        source=str(item.get("source") or ""),
        summary=str(item.get("summary") or ""),
        publish_time=str(item.get("publish_time") or ""),
    )


def _render_txt(case_id: str, cand: Candidate, content: str) -> str:
    header_lines = [
        f"case_id: {case_id}",
        "fraud_type: benign",
        f"title: {cand.title}",
        f"source: {cand.source}",
        f"publish_time: {cand.publish_time}",
        f"source_url: {cand.url}",
        "",
        "summary:",
        _clean_text(cand.summary) or "暂无摘要",
        "",
        "content_candidate:",
        _clean_text(content),
        "",
    ]
    return "\n".join(header_lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从内置新闻爬虫生成白样本(txt)")
    parser.add_argument("--count", type=int, default=20, help="生成白样本数量")
    parser.add_argument("--keyword", type=str, default="", help="搜索关键词（留空则使用默认关键词池）")
    parser.add_argument("--platform", type=str, default="all", help="平台: all/baidu/sogou/cctv/chinanews")
    parser.add_argument("--min-chars", type=int, default=220, help="正文最少字符数（不足则丢弃）")
    parser.add_argument("--sleep", type=float, default=0.5, help="每条之间的延迟，降低被封风险")
    parser.add_argument("--out-dir", type=str, default=str(TXT_DIR_DEFAULT), help="输出目录（txt）")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 默认关键词：尽量远离“诈骗/反诈”等语料
    keyword_pool = [
        "科技创新",
        "数字经济",
        "网络安全",
        "教育",
        "医疗",
        "交通",
        "新能源",
        "人工智能",
    ]

    keyword = (args.keyword or "").strip() or keyword_pool[int(time.time()) % len(keyword_pool)]
    target = max(1, int(args.count))
    # 允许在 demo/测试时将阈值设得很低；默认值在参数里控制即可。
    min_chars = max(0, int(args.min_chars))

    start_index = _next_white_index(out_dir)
    written = 0
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()

    # 为了尽快凑齐，循环尝试多次抓取
    attempts = 0
    max_attempts = max(6, target * 3)

    while written < target and attempts < max_attempts:
        attempts += 1
        result = search_news_by_keyword(keyword, platform=args.platform)
        items = [i for i in (result or {}).get("news", []) if isinstance(i, dict)]

        for raw in items:
            if written >= target:
                break

            cand = _to_candidate(raw)
            if not cand.title or not cand.url:
                continue
            if _should_skip_url(cand.url):
                continue

            resolved_url = _maybe_resolve_redirect_url(cand.url)
            if not resolved_url:
                continue
            cand = Candidate(
                title=cand.title,
                url=resolved_url,
                source=cand.source,
                summary=cand.summary,
                publish_time=cand.publish_time,
            )
            if cand.url in seen_urls or cand.title in seen_titles:
                continue
            seen_urls.add(cand.url)
            seen_titles.add(cand.title)

            # 快速过滤明显的反诈/诈骗语料（避免白样本污染）
            if _looks_like_fraud(cand.title) or _looks_like_fraud(cand.summary):
                continue

            content = _try_extract_article_text(cand.url)
            if not content:
                content = _try_extract_article_text_bs4(cand.url)
            if not content:
                content = _clean_text(cand.summary)

            if _looks_like_fraud(content):
                continue
            if len(content) < min_chars:
                continue

            case_id = f"TXT_WHITE_{start_index + written:03d}"
            txt = _render_txt(case_id, cand, content)
            out_path = out_dir / f"{case_id}.txt"
            out_path.write_text(txt, encoding="utf-8")
            written += 1

            if args.sleep > 0:
                time.sleep(float(args.sleep))

        # 每轮换关键词，减少重复和被封概率
        keyword = keyword_pool[(keyword_pool.index(keyword) + 1) % len(keyword_pool)] if keyword in keyword_pool else keyword_pool[0]

    print(f"[white-samples] written={written} out_dir={out_dir} (start_index={start_index})")
    if written < target:
        print(
            "[white-samples] 警告：未凑齐目标数量。常见原因：站点反爬/正文提取失败/过滤过严。\n"
            "可尝试：降低 --min-chars，或改用 --platform cctv/chinanews，或多运行几次后人工挑选。"
        )
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
