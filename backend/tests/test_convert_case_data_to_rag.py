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

from convert_case_data_to_rag import convert_file


class ConvertCaseDataToRagTests(unittest.TestCase):
    def test_convert_file_skips_empty_records_and_deduplicates_identical_title_content(self) -> None:
        temp_dir = Path(PROJECT_ROOT) / '.claude' / 'test_convert_case_data_to_rag'
        if temp_dir.exists():
            for item in sorted(temp_dir.rglob('*'), reverse=True):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
        temp_dir.mkdir(parents=True, exist_ok=True)

        source_path = temp_dir / 'source.json'
        payload = {
            'website_name': '测试来源',
            'source_url': 'https://example.com/source',
            'source_data': [
                {'title': '案例A', 'content': '正文A'},
                {'title': '案例A', 'content': '正文A'},
                {'title': '案例B', 'content': '正文B'},
                {'title': '案例C', 'content': ''},
                {'title': '', 'content': '正文D'},
            ],
        }
        source_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

        records, stats = convert_file(source_path, 'demo')

        self.assertEqual(2, len(records))
        self.assertEqual(['demo_0', 'demo_1'], [record['id'] for record in records])
        self.assertEqual('案例A', records[0]['title'])
        self.assertEqual('案例B', records[1]['title'])
        self.assertEqual(5, stats['source_total'])
        self.assertEqual(2, stats['converted'])
        self.assertEqual(3, stats['skipped'])
        self.assertEqual(1, stats['deduplicated'])


if __name__ == '__main__':
    unittest.main()
