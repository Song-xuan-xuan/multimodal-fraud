"""手动输入链接，提取网页正文并直接打印到控制台。"""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup

REQUEST_TIMEOUT = 20
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'zh-CN,zh;q=0.9',
}


def clean_text(text: str) -> str:
    return ' '.join((text or '').split()).strip()


def parse_plain_article(html: str, source_url: str) -> dict[str, str]:
    soup = BeautifulSoup(html, 'html.parser')

    title = ''
    source = ''
    publish_time = ''
    content = ''

    for selector in ('#activity-name', 'h1', 'title'):
        node = soup.select_one(selector)
        if node and clean_text(node.get_text()):
            title = clean_text(node.get_text())
            break

    for selector in ('#js_name', '.profile_meta_value', '.account_nickname'):
        node = soup.select_one(selector)
        if node and clean_text(node.get_text()):
            source = clean_text(node.get_text())
            break

    for selector in ('#publish_time', 'em#publish_time', '.publish_time', '.article-meta time'):
        node = soup.select_one(selector)
        if node and clean_text(node.get_text()):
            publish_time = clean_text(node.get_text())
            break

    content_root = (
        soup.select_one('#js_content')
        or soup.select_one('.rich_media_content')
        or soup.select_one('article')
        or soup.select_one('.article-content')
    )
    if content_root:
        paragraphs: list[str] = []
        for node in content_root.find_all(['p', 'section', 'div']):
            if node.find('img'):
                for image in node.find_all('img'):
                    image.decompose()
            text = clean_text(node.get_text(' ', strip=True))
            if text:
                paragraphs.append(text)
        content = '\n'.join(paragraphs)

    return {
        'title': title,
        'source': source,
        'publish_time': publish_time,
        'source_url': source_url,
        'content': content,
    }


def fetch_article_body(url: str) -> dict[str, str]:
    response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return parse_plain_article(response.text, url)


def format_console_output(article: dict[str, str]) -> str:
    return '\n'.join(
        [
            f"title: {article.get('title', '')}",
            f"source: {article.get('source', '')}",
            f"publish_time: {article.get('publish_time', '')}",
            f"source_url: {article.get('source_url', '')}",
            '',
            'content:',
            article.get('content', ''),
        ]
    )


def main() -> None:
    print('逐条输入链接，回车后开始提取。直接输入 q 或 quit 退出。')
    while True:
        url = input('\n请输入链接: ').strip()
        if not url:
            continue
        if url.lower() in {'q', 'quit', 'exit'}:
            print('已退出。')
            break

        try:
            article = fetch_article_body(url)
        except Exception as exc:
            print(f'提取失败: {exc}')
            continue

        print('\n' + '=' * 80)
        print(format_console_output(article))
        print('=' * 80)


if __name__ == '__main__':
    main()
