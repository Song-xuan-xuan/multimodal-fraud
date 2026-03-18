import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
import sys


class GenerateWhiteSamplesFromCrawlerSmokeTests(TestCase):
    def test_script_generates_txt_files_with_expected_headers(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        script_path = project_root / "scripts" / "generate_white_samples_from_crawler.py"
        self.assertTrue(script_path.exists(), str(script_path))

        out_dir = project_root / ".claude" / "white_samples_smoke"
        out_dir.mkdir(parents=True, exist_ok=True)

        # Dynamic import (script lives outside backend package)
        spec = importlib.util.spec_from_file_location("generate_white_samples_from_crawler", script_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        # Ensure module is visible for dataclass string-annotations resolution.
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)  # type: ignore[union-attr]

        fake_results = {
            "news": [
                {
                    "title": "城市公共交通迎来新线路优化",
                    "url": "https://example.com/news1",
                    "source": "示例来源",
                    "summary": "这是一个正常新闻摘要，介绍城市交通线路优化与便民措施。",
                    "publish_time": "2026-03-01",
                },
                {
                    "title": "新能源产业链持续扩张带动就业",
                    "url": "https://example.com/news2",
                    "source": "示例来源",
                    "summary": "产业链升级与创新驱动，带动就业增长与投资热度。",
                    "publish_time": "2026-03-02",
                },
            ]
        }

        # Avoid real network/extraction; return summary as content.
        with patch.object(module, "search_news_by_keyword", return_value=fake_results), patch.object(
            module, "_try_extract_article_text", return_value=""
        ):
            args = SimpleNamespace(
                count=2,
                keyword="科技创新",
                platform="all",
                min_chars=10,
                sleep=0.0,
                out_dir=str(out_dir),
            )
            with patch.object(module, "parse_args", return_value=args):
                rc = module.main()

        self.assertEqual(rc, 0)
        files = sorted(out_dir.glob("TXT_WHITE_*.txt"))
        self.assertEqual(len(files), 2)
        text0 = files[0].read_text(encoding="utf-8")
        self.assertIn("fraud_type: benign", text0)
        self.assertIn("content_candidate:", text0)
