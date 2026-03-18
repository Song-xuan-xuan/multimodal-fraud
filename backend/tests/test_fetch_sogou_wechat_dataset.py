import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
for candidate in (PROJECT_ROOT, SCRIPTS_DIR):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from fetch_sogou_wechat_dataset import (
    build_dataset_item,
    download_article_images,
    infer_fraud_type,
    merge_article_data,
    parse_article_detail,
    parse_search_results,
)


class FetchSogouWechatDatasetTests(unittest.TestCase):
    def test_parse_search_results_extracts_entries(self) -> None:
        html = '''
        <html><body>
          <ul class="news-list">
            <li>
              <div class="txt-box">
                <h3><a href="/link?url=abc">警惕冒充班主任收费诈骗</a></h3>
                <p class="txt-info">近日，多地出现家长群收款码骗局。</p>
                <div class="s-p"><a>平安校园</a><span>2026-03-16</span></div>
              </div>
            </li>
          </ul>
        </body></html>
        '''

        results = parse_search_results(html)

        self.assertEqual(1, len(results))
        self.assertEqual('警惕冒充班主任收费诈骗', results[0]['title'])
        self.assertEqual('https://weixin.sogou.com/link?url=abc', results[0]['url'])
        self.assertEqual('平安校园', results[0]['source'])
        self.assertEqual('2026-03-16', results[0]['publish_time'])

    def test_parse_article_detail_extracts_content_and_images(self) -> None:
        html = '''
        <html><body>
          <h1 id="activity-name">警惕冒充公检法诈骗</h1>
          <a id="js_name">反诈中心</a>
          <em id="publish_time">2026-03-15</em>
          <div id="js_content">
            <p>骗子冒充公安机关，诱导受害人转账到安全账户。</p>
            <p>警方提醒不要轻信陌生电话。</p>
            <img data-src="https://img.example.com/a.jpg" />
            <img src="https://img.example.com/b.png" />
          </div>
        </body></html>
        '''

        detail = parse_article_detail(html, 'https://mp.weixin.qq.com/s/demo')

        self.assertEqual('警惕冒充公检法诈骗', detail['title'])
        self.assertEqual('反诈中心', detail['source'])
        self.assertEqual('2026-03-15', detail['publish_time'])
        self.assertIn('骗子冒充公安机关', detail['content'])
        self.assertEqual(
            ['https://img.example.com/a.jpg', 'https://img.example.com/b.png'],
            detail['image_urls'],
        )

    def test_build_dataset_item_maps_fields(self) -> None:
        article = {
            'title': '警惕冒充班主任收费诈骗',
            'content': '骗子冒充班主任在群里发收款码，要求家长今天截止前缴费。',
            'source': '反诈中心',
            'publish_time': '2026-03-16',
            'source_url': 'https://mp.weixin.qq.com/s/demo',
            'image_urls': ['https://img.example.com/a.jpg'],
        }

        item = build_dataset_item(
            case_id='TXT_BLACK_001',
            article=article,
            image_paths=['backend/data/evaluation_assets/images/TXT_BLACK_001/detail_001.jpg'],
        )

        self.assertEqual('TXT_BLACK_001', item['case_id'])
        self.assertEqual('text', item['modality'])
        self.assertEqual(1, item['label'])
        self.assertEqual('冒充班主任收费', item['fraud_type'])
        self.assertEqual('警惕冒充班主任收费诈骗', item['title'])
        self.assertEqual('骗子冒充班主任在群里发收款码，要求家长今天截止前缴费。', item['content'])
        self.assertEqual(['https://img.example.com/a.jpg'], item['image_urls'])
        self.assertEqual(1, len(item['image_paths']))

    def test_infer_fraud_type_returns_best_matching_label(self) -> None:
        fraud_type = infer_fraud_type(
            title='紧急提醒：警惕冒充客服退款骗局',
            content='骗子冒充电商客服，以订单异常、退款赔付为由诱导点击链接并填写信息。',
        )

        self.assertEqual('虚假客服退款', fraud_type)

    def test_infer_fraud_type_falls_back_when_no_match(self) -> None:
        fraud_type = infer_fraud_type(
            title='春季校园安全宣传',
            content='文章主要介绍如何提升学生安全意识，并未涉及具体诈骗套路。',
        )

        self.assertEqual('待标注', fraud_type)

    def test_download_article_images_saves_local_files(self) -> None:
        session = Mock()
        response = Mock()
        response.content = b'fake-image-bytes'
        response.raise_for_status.return_value = None
        response.headers = {'Content-Type': 'image/jpeg'}
        session.get.return_value = response

        temp_dir = Path(PROJECT_ROOT) / '.claude' / 'test_fetch_sogou_wechat_images'
        if temp_dir.exists():
            for item in sorted(temp_dir.rglob('*'), reverse=True):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
        temp_dir.mkdir(parents=True, exist_ok=True)

        paths = download_article_images(
            session=session,
            image_urls=['https://img.example.com/demo'],
            target_dir=temp_dir,
            referer='https://mp.weixin.qq.com/s/demo',
        )

        self.assertEqual(1, len(paths))
        self.assertTrue(Path(paths[0]).exists())
        self.assertEqual(b'fake-image-bytes', Path(paths[0]).read_bytes())

    def test_merge_article_data_preserves_search_fields_when_detail_is_empty(self) -> None:
        search_item = {
            'title': '警惕冒充班主任收费诈骗',
            'url': 'https://weixin.sogou.com/link?url=abc',
            'summary': '家长群收款码骗局近期高发。',
            'source': '平安校园',
            'publish_time': '2026-03-16',
        }
        article = {
            'title': '',
            'source': '',
            'publish_time': '',
            'content': '',
            'image_urls': [],
            'source_url': 'https://weixin.sogou.com/link?url=abc',
        }

        merged = merge_article_data(search_item, article)

        self.assertEqual('警惕冒充班主任收费诈骗', merged['title'])
        self.assertEqual('平安校园', merged['source'])
        self.assertEqual('2026-03-16', merged['publish_time'])
        self.assertEqual('家长群收款码骗局近期高发。', merged['content'])


if __name__ == '__main__':
    unittest.main()
