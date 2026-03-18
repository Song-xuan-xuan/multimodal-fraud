import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
for candidate in (PROJECT_ROOT, SCRIPTS_DIR):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from extract_plain_article_body import format_console_output, parse_plain_article


class ExtractPlainArticleBodyTests(unittest.TestCase):
    def test_parse_plain_article_extracts_text_and_ignores_images(self) -> None:
        html = '''
        <html><body>
          <h1 id="activity-name">警惕冒充客服退款诈骗</h1>
          <a id="js_name">平安发布</a>
          <em id="publish_time">2026-03-16</em>
          <div id="js_content">
            <p>骗子冒充客服，以订单异常为由要求点击链接。</p>
            <img data-src="https://img.example.com/demo.jpg" />
            <p>对方还会诱导填写银行卡和验证码。</p>
          </div>
        </body></html>
        '''

        article = parse_plain_article(html, 'https://mp.weixin.qq.com/s/demo')

        self.assertEqual('警惕冒充客服退款诈骗', article['title'])
        self.assertEqual('平安发布', article['source'])
        self.assertEqual('2026-03-16', article['publish_time'])
        self.assertEqual(
            '骗子冒充客服，以订单异常为由要求点击链接。\n对方还会诱导填写银行卡和验证码。',
            article['content'],
        )

    def test_format_console_output_contains_required_fields(self) -> None:
        article = {
            'title': '标题示例',
            'source': '来源示例',
            'publish_time': '2026-03-16',
            'source_url': 'https://example.com/demo',
            'content': '正文第一段\n正文第二段',
        }

        output = format_console_output(article)

        self.assertIn('title: 标题示例', output)
        self.assertIn('source: 来源示例', output)
        self.assertIn('publish_time: 2026-03-16', output)
        self.assertIn('source_url: https://example.com/demo', output)
        self.assertIn('正文第一段', output)


if __name__ == '__main__':
    unittest.main()
