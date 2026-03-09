import importlib
import os
import sys
import unittest


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


class NewsSchemaImportTests(unittest.TestCase):
    def test_news_schema_module_is_importable(self) -> None:
        module = importlib.import_module('app.schemas.news')
        self.assertTrue(hasattr(module, 'NewsDetailResponse'))
        self.assertTrue(hasattr(module, 'NewsResponse'))


if __name__ == '__main__':
    unittest.main()
