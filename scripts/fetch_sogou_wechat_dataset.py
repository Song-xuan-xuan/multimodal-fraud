"""抓取搜狗微信搜索结果并导出评测候选 JSON。"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SEARCH_BASE_URL = 'https://weixin.sogou.com/weixin'
DEFAULT_QUERY = '反诈'
DEFAULT_OUTPUT = Path('backend/data/evaluation_candidates.json')
DEFAULT_RAW_OUTPUT = Path('backend/data/evaluation_candidates_raw.json')
DEFAULT_IMAGE_ROOT = Path('backend/data/evaluation_assets/images')
REQUEST_TIMEOUT = 15

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': (
        'text/html,application/xhtml+xml,application/xml;'
        'q=0.9,image/avif,image/webp,image/apng,*/*;'
        'q=0.8,application/signed-exchange;v=b3;q=0.7'
    ),
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://weixin.sogou.com/',
}

IMAGE_EXTENSION_BY_CONTENT_TYPE = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
    'image/gif': '.gif',
}

FRAUD_TYPE_RULES = [
    {
        'label': '冒充班主任收费',
        'keywords': ['班主任', '家长群', '收款码', '资料费', '缴费', '今天截止'],
        'patterns': [('班主任', '收款码'), ('家长群', '缴费')],
    },
    {
        'label': '冒充公检法',
        'keywords': ['公安', '警察', '法院', '检察院', '安全账户', '涉嫌洗钱'],
        'patterns': [('公安', '安全账户'), ('法院', '资金核查')],
    },
    {
        'label': '虚假客服退款',
        'keywords': ['客服', '退款', '赔付', '订单异常', '售后', '退费'],
        'patterns': [('客服', '退款'), ('订单异常', '赔付')],
    },
    {
        'label': '虚假征信修复',
        'keywords': ['征信', '修复', '洗白', '信用记录', '消除记录'],
        'patterns': [('征信', '修复')],
    },
    {
        'label': '刷单返利',
        'keywords': ['刷单', '返利', '垫付', '做任务', '佣金'],
        'patterns': [('刷单', '返利'), ('垫付', '佣金')],
    },
    {
        'label': '投资理财诈骗',
        'keywords': ['投资', '理财', '高收益', '稳赚不赔', '内幕消息', '带单'],
        'patterns': [('投资', '高收益'), ('理财', '内幕消息')],
    },
    {
        'label': '兼职招聘诈骗',
        'keywords': ['兼职', '招聘', '日结', '高薪', '在家办公', '押金'],
        'patterns': [('兼职', '日结'), ('招聘', '押金')],
    },
    {
        'label': '快递理赔诈骗',
        'keywords': ['快递', '丢件', '理赔', '包裹异常', '赔偿'],
        'patterns': [('快递', '理赔'), ('包裹异常', '赔偿')],
    },
    {
        'label': '熟人借钱冒用',
        'keywords': ['熟人', '借钱', '周转', '账号被盗', '先转我', '临时急用'],
        'patterns': [('借钱', '周转'), ('账号被盗', '转账')],
    },
    {
        'label': '虚假中奖诈骗',
        'keywords': ['中奖', '领奖', '手续费', '保证金', '幸运用户'],
        'patterns': [('中奖', '手续费'), ('领奖', '保证金')],
    },
    {
        'label': '钓鱼链接控号',
        'keywords': ['链接', '验证码', '验证', '账号异常', '共享屏幕', '登录'],
        'patterns': [('验证码', '链接'), ('共享屏幕', '登录')],
    },
    {
        'label': 'AI合成语音诈骗',
        'keywords': ['语音', '录音', '合成', '冒充亲友', '冒充领导', '来电'],
        'patterns': [('合成', '语音'), ('冒充领导', '来电')],
    },
]


def clean_text(text: str) -> str:
    if not text:
        return ''
    compact = re.sub(r'\s+', ' ', text)
    return compact.strip()


def infer_fraud_type(title: str, content: str) -> str:
    corpus = clean_text(f'{title} {content}')
    if not corpus:
        return '待标注'

    best_label = '待标注'
    best_score = 0

    for rule in FRAUD_TYPE_RULES:
        score = 0
        for keyword in rule['keywords']:
            if keyword in corpus:
                score += 2
        for pattern in rule.get('patterns', []):
            if all(token in corpus for token in pattern):
                score += 3

        if score > best_score:
            best_score = score
            best_label = rule['label']

    return best_label if best_score > 0 else '待标注'


def build_search_url(query: str, page: int) -> str:
    page_param = max(page, 1)
    return f'{SEARCH_BASE_URL}?query={quote(query)}&type=2&page={page_param}'


def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def parse_search_results(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    results: list[dict[str, str]] = []
    seen_urls: set[str] = set()

    for item in soup.select('li'):
        title_link = item.select_one('h3 a')
        if not title_link:
            continue

        title = clean_text(title_link.get_text())
        href = clean_text(title_link.get('href', ''))
        if not title or not href:
            continue

        url = urljoin('https://weixin.sogou.com', href)
        if url in seen_urls:
            continue
        seen_urls.add(url)

        summary_el = item.select_one('.txt-info') or item.select_one('.s-p3')
        source_el = item.select_one('.s-p a') or item.select_one('.account')
        time_el = item.select_one('.s-p span') or item.select_one('.s2')

        results.append(
            {
                'title': title,
                'url': url,
                'summary': clean_text(summary_el.get_text()) if summary_el else '',
                'source': clean_text(source_el.get_text()) if source_el else '',
                'publish_time': clean_text(time_el.get_text()) if time_el else '',
            }
        )
    return results


def fetch_search_results(
    session: requests.Session,
    query: str,
    page: int = 1,
) -> list[dict[str, str]]:
    url = build_search_url(query, page)
    response = session.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return parse_search_results(response.text)


def parse_article_detail(html: str, source_url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, 'html.parser')
    title = ''
    source = ''
    publish_time = ''
    content = ''
    image_urls: list[str] = []

    title_selectors = ['#activity-name', 'h1']
    for selector in title_selectors:
        title_el = soup.select_one(selector)
        if title_el and clean_text(title_el.get_text()):
            title = clean_text(title_el.get_text())
            break

    source_selectors = ['#js_name', '.profile_meta_value']
    for selector in source_selectors:
        source_el = soup.select_one(selector)
        if source_el and clean_text(source_el.get_text()):
            source = clean_text(source_el.get_text())
            break

    time_selectors = ['#publish_time', 'em#publish_time', '.publish_time']
    for selector in time_selectors:
        time_el = soup.select_one(selector)
        if time_el and clean_text(time_el.get_text()):
            publish_time = clean_text(time_el.get_text())
            break

    content_root = soup.select_one('#js_content') or soup.select_one('.rich_media_content')
    if content_root:
        paragraphs = []
        for element in content_root.find_all(['p', 'section']):
            text = clean_text(element.get_text(' ', strip=True))
            if text:
                paragraphs.append(text)
        content = '\n'.join(paragraphs)

        for img in content_root.find_all('img'):
            raw_url = (
                img.get('data-src')
                or img.get('src')
                or img.get('data-backsrc')
                or ''
            )
            image_url = clean_text(raw_url)
            if not image_url:
                continue
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            elif image_url.startswith('/'):
                image_url = urljoin(source_url, image_url)
            if image_url not in image_urls:
                image_urls.append(image_url)

    return {
        'title': title,
        'source': source,
        'publish_time': publish_time,
        'content': content,
        'image_urls': image_urls,
        'source_url': source_url,
    }


def fetch_article_detail(session: requests.Session, url: str) -> dict[str, Any]:
    response = session.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return parse_article_detail(response.text, url)


def merge_article_data(search_item: dict[str, Any], article: dict[str, Any]) -> dict[str, Any]:
    title = article.get('title') or search_item.get('title', '')
    source = article.get('source') or search_item.get('source', '')
    publish_time = article.get('publish_time') or search_item.get('publish_time', '')
    content = article.get('content') or search_item.get('summary', '')
    image_urls = article.get('image_urls') or []

    return {
        **search_item,
        **article,
        'title': title,
        'source': source,
        'publish_time': publish_time,
        'content': content,
        'image_urls': image_urls,
        'source_url': article.get('source_url') or search_item.get('url', ''),
    }


def infer_image_extension(image_url: str, content_type: str) -> str:
    if content_type in IMAGE_EXTENSION_BY_CONTENT_TYPE:
        return IMAGE_EXTENSION_BY_CONTENT_TYPE[content_type]
    suffix = Path(urlparse(image_url).path).suffix.lower()
    if suffix:
        return suffix
    return '.jpg'


def download_article_images(
    session: requests.Session,
    image_urls: list[str],
    target_dir: Path,
    referer: str,
) -> list[str]:
    target_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[str] = []

    for index, image_url in enumerate(image_urls, start=1):
        response = session.get(
            image_url,
            timeout=REQUEST_TIMEOUT,
            headers={'Referer': referer, 'User-Agent': HEADERS['User-Agent']},
        )
        response.raise_for_status()
        content_type = clean_text(response.headers.get('Content-Type', '')).split(';')[0]
        extension = infer_image_extension(image_url, content_type)
        filename = f'detail_{index:03d}{extension}'
        file_path = target_dir / filename
        file_path.write_bytes(response.content)
        saved_paths.append(file_path.as_posix())
    return saved_paths


def build_dataset_item(
    case_id: str,
    article: dict[str, Any],
    image_paths: list[str],
) -> dict[str, Any]:
    title = article.get('title', '')
    content = article.get('content', '')
    return {
        'case_id': case_id,
        'modality': 'text',
        'label': 1,
        'fraud_type': infer_fraud_type(title, content),
        'title': title,
        'content': content,
        'file_path': '',
        'image_urls': article.get('image_urls', []),
        'image_paths': image_paths,
        'source_type': 'real_public_case',
        'source_url': article.get('source_url', ''),
        'difficulty': 'medium',
        'expected_risk_level': 'high',
        'notes': '来源于搜狗微信搜索结果，待人工复核标注',
        'source': article.get('source', ''),
        'publish_time': article.get('publish_time', ''),
    }


def fetch_dataset_candidates(
    query: str,
    pages: int,
    limit: int,
    output_path: Path,
    raw_output_path: Path,
    image_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    session = create_session()
    search_results: list[dict[str, Any]] = []

    for page in range(1, pages + 1):
        try:
            page_results = fetch_search_results(session, query, page=page)
        except requests.RequestException as exc:
            logger.warning('抓取搜索结果失败 page=%s error=%s', page, exc)
            continue
        search_results.extend(page_results)
        if len(search_results) >= limit:
            break

    raw_articles: list[dict[str, Any]] = []
    dataset_items: list[dict[str, Any]] = []

    for index, search_item in enumerate(search_results[:limit], start=1):
        detail_url = search_item['url']
        try:
            article = fetch_article_detail(session, detail_url)
        except requests.RequestException as exc:
            logger.warning('抓取文章详情失败 url=%s error=%s', detail_url, exc)
            continue

        merged_article = merge_article_data(search_item, article)

        case_id = f'TXT_BLACK_{index:03d}'
        image_dir = image_root / case_id
        try:
            image_paths = download_article_images(
                session=session,
                image_urls=merged_article.get('image_urls', []),
                target_dir=image_dir,
                referer=detail_url,
            )
        except requests.RequestException as exc:
            logger.warning('下载图片失败 case_id=%s error=%s', case_id, exc)
            image_paths = []

        raw_articles.append(merged_article)
        dataset_items.append(build_dataset_item(case_id, merged_article, image_paths))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dataset_items, ensure_ascii=False, indent=2), encoding='utf-8')
    raw_output_path.write_text(json.dumps(raw_articles, ensure_ascii=False, indent=2), encoding='utf-8')
    return dataset_items, raw_articles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='抓取搜狗微信搜索结果并导出评测候选 JSON')
    parser.add_argument('--query', default=DEFAULT_QUERY, help='搜索关键词，默认：反诈')
    parser.add_argument('--pages', type=int, default=1, help='抓取页数，默认：1')
    parser.add_argument('--limit', type=int, default=10, help='最多导出文章数，默认：10')
    parser.add_argument(
        '--output',
        default=str(DEFAULT_OUTPUT),
        help='评测候选 JSON 输出路径',
    )
    parser.add_argument(
        '--raw-output',
        default=str(DEFAULT_RAW_OUTPUT),
        help='原始文章 JSON 输出路径',
    )
    parser.add_argument(
        '--image-root',
        default=str(DEFAULT_IMAGE_ROOT),
        help='文章图片下载目录',
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    args = parse_args()
    dataset_items, raw_articles = fetch_dataset_candidates(
        query=args.query,
        pages=max(args.pages, 1),
        limit=max(args.limit, 1),
        output_path=Path(args.output),
        raw_output_path=Path(args.raw_output),
        image_root=Path(args.image_root),
    )
    logger.info('完成抓取，候选案例 %d 条，原始文章 %d 条', len(dataset_items), len(raw_articles))


if __name__ == '__main__':
    main()
