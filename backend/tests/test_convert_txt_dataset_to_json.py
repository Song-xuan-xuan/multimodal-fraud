import json
import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
for candidate in (PROJECT_ROOT, SCRIPTS_DIR):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from convert_txt_dataset_to_json import (
    convert_directory_to_dataset,
    normalize_content,
    parse_txt_sample,
)


class ConvertTxtDatasetToJsonTests(unittest.TestCase):
    def test_normalize_content_flattens_text_to_single_paragraph(self) -> None:
        raw = '第一段第一句。\n\n\n第一段第二句。\n\n第二段。\n\n\n'
        normalized = normalize_content(raw)
        self.assertEqual('第一段第一句。 第一段第二句。 第二段。', normalized)

    def test_parse_txt_sample_extracts_fields_and_uses_content_candidate(self) -> None:
        text = '''case_id: TXT_BLACK_001
fraud_type: 冒充公检法
title: 假冒警方办案
source: 平安发布
publish_time: 2026-03-16
source_url: https://example.com/article

summary:
这是摘要。

content_candidate:
第一段。


第二段。
'''
        sample = parse_txt_sample(text)

        self.assertEqual('TXT_BLACK_001', sample['case_id'])
        self.assertEqual('冒充公检法', sample['fraud_type'])
        self.assertEqual('假冒警方办案', sample['title'])
        self.assertEqual('平安发布', sample['source'])
        self.assertEqual('2026-03-16', sample['publish_time'])
        self.assertEqual('https://example.com/article', sample['source_url'])
        self.assertEqual('第一段。 第二段。', sample['content'])

    def test_convert_directory_to_dataset_writes_json_array(self) -> None:
        temp_dir = Path(PROJECT_ROOT) / '.claude' / 'test_convert_txt_dataset'
        if temp_dir.exists():
            for item in sorted(temp_dir.rglob('*'), reverse=True):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
        txt_dir = temp_dir / 'txt'
        txt_dir.mkdir(parents=True, exist_ok=True)
        output_path = temp_dir / 'dataset.json'

        (txt_dir / 'TXT_BLACK_001.txt').write_text(
            '''case_id: TXT_BLACK_001
fraud_type: 刷单返利
title: 兼职刷单
source: 平安东胜
publish_time: 2026-03-16
source_url: https://example.com/1

summary:
摘要一

content_candidate:
正文一
''',
            encoding='utf-8',
        )

        (txt_dir / 'TXT_WHITE_001.txt').write_text(
            '''case_id: TXT_WHITE_001
fraud_type: benign
title: 正常通知
source: 官方平台
publish_time: 2026-03-17
source_url: https://example.com/2

summary:
摘要二

content_candidate:
正文二
''',
            encoding='utf-8',
        )

        dataset = convert_directory_to_dataset(txt_dir, output_path)

        self.assertEqual(2, len(dataset))
        self.assertEqual('text', dataset[0]['modality'])
        self.assertEqual(1, dataset[0]['label'])
        self.assertEqual(0, dataset[1]['label'])
        self.assertTrue(output_path.exists())

        saved = json.loads(output_path.read_text(encoding='utf-8'))
        self.assertEqual(2, len(saved))

    def test_convert_directory_applies_manual_fraud_type_override_and_omits_source_notes(self) -> None:
        temp_dir = Path(PROJECT_ROOT) / '.claude' / 'test_convert_txt_dataset_override'
        if temp_dir.exists():
            for item in sorted(temp_dir.rglob('*'), reverse=True):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
        txt_dir = temp_dir / 'txt'
        txt_dir.mkdir(parents=True, exist_ok=True)
        output_path = temp_dir / 'dataset.json'

        (txt_dir / 'TXT_BLACK_002.txt').write_text(
            '''case_id: TXT_BLACK_002
fraud_type: 冒充公检法
title: 男子连续2次被骗 骗子教他把黄金藏投影仪邮寄
source: 公安部刑侦局
publish_time: 2026-03-16
source_url: https://example.com/black-002

summary:
摘要

content_candidate:
正文
''',
            encoding='utf-8',
        )

        dataset = convert_directory_to_dataset(txt_dir, output_path)

        self.assertEqual('邮寄黄金投资诈骗', dataset[0]['fraud_type'])
        self.assertNotIn('notes', dataset[0])
        self.assertNotIn('source', dataset[0])


if __name__ == '__main__':
    unittest.main()
