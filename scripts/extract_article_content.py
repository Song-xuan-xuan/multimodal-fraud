"""从微信公众号文章提取纯文本正文，跳过图片。

问题：搜狗链接(weixin.sogou.com)有反爬验证，无法直接抓取。
方案：在浏览器中打开搜狗链接，跳转到 mp.weixin.qq.com 后，复制地址栏URL给脚本。

用法:
  # 模式1: 输入微信文章URL，输出正文到终端
  python scripts/extract_article_content.py "https://mp.weixin.qq.com/s?..."

  # 模式2: 交互模式 - 逐个处理内容不足的TXT文件
  python scripts/extract_article_content.py -i test-dataset/txt/

  # 模式3: 指定文件 + 微信URL，直接回填
  python scripts/extract_article_content.py --update test-dataset/txt/TXT_BLACK_010.txt --url "https://mp.weixin.qq.com/s?..."
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/131.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
}

REQUEST_TIMEOUT = 20


def clean_text(text: str) -> str:
    if not text:
        return ''
    return re.sub(r'\s+', ' ', text).strip()


def is_sogou_blocked(html: str) -> bool:
    """检测是否被搜狗反爬拦截。"""
    markers = ['VerifyCode', '返回首页', '验证码', 'antispider', 'IP:']
    return any(m in html for m in markers)


def extract_text_from_html(html: str) -> str:
    """从HTML中提取微信文章纯文本正文。"""
    soup = BeautifulSoup(html, 'html.parser')

    # 微信公众号文章正文容器
    content_root = (
        soup.select_one('#js_content')
        or soup.select_one('.rich_media_content')
    )

    if content_root:
        # 移除图片、SVG、视频等非文字元素
        for tag in content_root.find_all(['img', 'svg', 'video', 'audio', 'iframe']):
            tag.decompose()
        # 移除空的 span/section（常见于微信排版装饰）
        for tag in content_root.find_all(['span', 'section']):
            if not tag.get_text(strip=True):
                tag.decompose()

        # 收集段落文本，去重
        paragraphs: list[str] = []
        seen: set[str] = set()
        for el in content_root.find_all(['p', 'section', 'h1', 'h2', 'h3', 'h4', 'li', 'blockquote']):
            text = clean_text(el.get_text(' ', strip=True))
            if text and text not in seen and len(text) > 1:
                paragraphs.append(text)
                seen.add(text)

        if paragraphs:
            return '\n'.join(paragraphs)

        # 段落提取为空时，回退到整个容器文字
        full_text = clean_text(content_root.get_text(' ', strip=True))
        if full_text:
            return full_text

    # 回退：尝试其他常见正文容器
    for selector in ['article', 'main', '.content', '#content']:
        fallback = soup.select_one(selector)
        if fallback:
            for tag in fallback.find_all(['img', 'svg', 'video', 'script', 'style']):
                tag.decompose()
            text = clean_text(fallback.get_text(' ', strip=True))
            if text and len(text) > 50:
                return text

    return ''


def fetch_article_text(url: str, session: requests.Session) -> str:
    """抓取文章URL，提取纯文本。检测搜狗反爬并提示。"""
    # 搜狗链接需要特殊处理
    if 'weixin.sogou.com' in url:
        raise ValueError(
            '搜狗链接有反爬验证，无法直接抓取。\n'
            '请在浏览器中打开此链接，等待跳转到 mp.weixin.qq.com 后，\n'
            '复制浏览器地址栏中的URL使用。'
        )

    resp = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or 'utf-8'

    if is_sogou_blocked(resp.text):
        raise ValueError('被搜狗反爬拦截，请使用 mp.weixin.qq.com 的URL')

    return extract_text_from_html(resp.text)


# ---------- TXT 文件读写 ----------

def read_txt_file(path: Path) -> dict[str, str]:
    """解析 TXT_BLACK_xxx.txt 格式文件。"""
    raw = path.read_text(encoding='utf-8')
    fields: dict[str, str] = {}
    current_key = ''
    current_lines: list[str] = []

    for line in raw.split('\n'):
        m = re.match(r'^([\w]+):\s?(.*)', line)
        if m:
            if current_key:
                fields[current_key] = '\n'.join(current_lines).strip()
            current_key = m.group(1)
            current_lines = [m.group(2)]
        else:
            current_lines.append(line)

    if current_key:
        fields[current_key] = '\n'.join(current_lines).strip()

    return fields


def write_txt_file(path: Path, fields: dict[str, str]) -> None:
    """写回 TXT_BLACK_xxx.txt 格式。"""
    key_order = [
        'case_id', 'fraud_type', 'title', 'source',
        'publish_time', 'source_url', 'summary', 'content_candidate',
    ]
    lines: list[str] = []
    written: set[str] = set()

    for key in key_order:
        if key in fields:
            lines.append(f'{key}: {fields[key]}')
            if key == 'source_url':
                lines.append('')
            written.add(key)

    for key, value in fields.items():
        if key not in written:
            lines.append(f'{key}: {value}')

    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def update_file_with_text(path: Path, text: str) -> None:
    """将提取到的正文回填到文件的 content_candidate。"""
    fields = read_txt_file(path)
    fields['content_candidate'] = text
    write_txt_file(path, fields)


# ---------- 主流程 ----------

def cmd_fetch_url(url: str, session: requests.Session) -> None:
    """模式1: 抓取URL打印正文。"""
    text = fetch_article_text(url, session)
    if text:
        print(text)
    else:
        print('未能提取到正文（可能是纯图片文章）', file=sys.stderr)
        sys.exit(1)


def cmd_update_file(file_path: Path, url: str, session: requests.Session) -> None:
    """模式3: 指定文件 + URL，抓取并回填。"""
    text = fetch_article_text(url, session)
    if not text or len(text) < 10:
        print(f'提取失败或正文太短（{len(text)}字）', file=sys.stderr)
        sys.exit(1)
    update_file_with_text(file_path, text)
    print(f'已更新 {file_path.name}: {len(text)}字')


def cmd_interactive(batch_dir: Path, min_len: int, session: requests.Session) -> None:
    """模式2: 交互模式，逐个处理。"""
    txt_files = sorted(batch_dir.glob('TXT_BLACK_*.txt'))
    if not txt_files:
        print(f'目录下没有 TXT_BLACK_*.txt 文件', file=sys.stderr)
        sys.exit(1)

    # 筛选出需要更新的文件
    need_update: list[tuple[Path, dict[str, str]]] = []
    for f in txt_files:
        fields = read_txt_file(f)
        content = fields.get('content_candidate', '').strip()
        if len(content) < min_len:
            need_update.append((f, fields))

    if not need_update:
        print(f'所有 {len(txt_files)} 个文件的 content_candidate 都已超过 {min_len} 字，无需更新。')
        return

    print(f'共 {len(txt_files)} 个文件，其中 {len(need_update)} 个需要补充正文（content < {min_len}字）')
    print('='*60)
    print('操作方法:')
    print('  1. 在浏览器打开文件中的搜狗链接')
    print('  2. 等待跳转到 mp.weixin.qq.com')
    print('  3. 复制地址栏URL粘贴到这里')
    print('  输入 s 跳过当前文件，输入 q 退出')
    print('='*60)

    updated = 0
    for i, (path, fields) in enumerate(need_update, 1):
        title = fields.get('title', '无标题')
        sogou_url = fields.get('source_url', '')
        old_content = fields.get('content_candidate', '').strip()

        print(f'\n[{i}/{len(need_update)}] {path.name}')
        print(f'  标题: {title}')
        print(f'  现有内容: {old_content[:80]}{"..." if len(old_content) > 80 else ""}')
        print(f'  搜狗链接: {sogou_url[:80]}...' if len(sogou_url) > 80 else f'  搜狗链接: {sogou_url}')

        while True:
            user_input = input('\n  粘贴微信URL (s=跳过, q=退出): ').strip()

            if user_input.lower() == 'q':
                print(f'\n退出。已更新 {updated} 个文件。')
                return
            if user_input.lower() == 's':
                print('  已跳过')
                break

            if not user_input.startswith('http'):
                print('  请输入有效的URL（以 http 开头）')
                continue

            try:
                text = fetch_article_text(user_input, session)
            except Exception as e:
                print(f'  抓取失败: {e}')
                print('  请重试或输入 s 跳过')
                continue

            if not text or len(text) < 10:
                print(f'  提取到的正文太短（{len(text)}字），可能是纯图片页面')
                print('  请重试或输入 s 跳过')
                continue

            # 显示提取结果预览
            preview = text[:200] + ('...' if len(text) > 200 else '')
            print(f'\n  提取到 {len(text)} 字:')
            print(f'  ---')
            print(f'  {preview}')
            print(f'  ---')

            confirm = input('  确认写入? (y/n): ').strip().lower()
            if confirm in ('y', 'yes', ''):
                update_file_with_text(path, text)
                updated += 1
                print(f'  已写入 {path.name}')
                break
            else:
                print('  已取消，请重新输入URL或跳过')

    print(f'\n全部完成。共更新 {updated}/{len(need_update)} 个文件。')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='从微信公众号文章提取纯文本正文（跳过图片）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('url', nargs='?', help='微信文章URL (mp.weixin.qq.com)，直接输出正文')
    parser.add_argument('-i', '--interactive', metavar='DIR',
                        help='交互模式: 逐个处理目录下内容不足的TXT文件')
    parser.add_argument('--update', metavar='FILE',
                        help='指定TXT文件，配合 --url 回填 content_candidate')
    parser.add_argument('--url', metavar='URL',
                        help='配合 --update 使用，指定微信文章URL')
    parser.add_argument('--min-len', type=int, default=50,
                        help='交互模式下，content_candidate 少于此字数才处理（默认50）')
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update(HEADERS)

    if args.url and not args.update:
        # 模式1: 直接输入URL，打印正文
        cmd_fetch_url(args.url, session)

    elif args.update:
        # 模式3: 更新单个文件
        path = Path(args.update)
        if not path.exists():
            print(f'文件不存在: {path}', file=sys.stderr)
            sys.exit(1)
        if not args.url:
            # 没给 --url，进入单文件交互
            fields = read_txt_file(path)
            print(f'文件: {path.name}')
            print(f'标题: {fields.get("title", "")}')
            print(f'搜狗链接: {fields.get("source_url", "")}')
            url = input('\n请粘贴微信文章URL: ').strip()
            if not url.startswith('http'):
                print('无效URL', file=sys.stderr)
                sys.exit(1)
            cmd_update_file(path, url, session)
        else:
            cmd_update_file(path, args.url, session)

    elif args.interactive:
        # 模式2: 交互模式
        batch_dir = Path(args.interactive)
        if not batch_dir.is_dir():
            print(f'目录不存在: {batch_dir}', file=sys.stderr)
            sys.exit(1)
        cmd_interactive(batch_dir, args.min_len, session)

    else:
        parser.print_help()
        print('\n提示: 搜狗链接有反爬验证，请先在浏览器打开搜狗链接，')
        print('等跳转到 mp.weixin.qq.com 后复制地址栏URL使用。')


if __name__ == '__main__':
    main()
