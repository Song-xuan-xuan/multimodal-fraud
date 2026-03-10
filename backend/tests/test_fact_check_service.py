import asyncio
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
for candidate in (BACKEND_DIR, PROJECT_ROOT):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from app.services.fact_check_service import check_fact


class FactCheckServiceTests(unittest.TestCase):
    def test_check_fact_prefers_serpapi_when_key_present(self) -> None:
        fake_response = Mock()
        fake_response.status_code = 200
        fake_response.json.return_value = {
            'organic_results': [
                {
                    'title': '警方提醒：冒充客服退款诈骗高发',
                    'link': 'https://example.com/news-1',
                    'snippet': '多地警方确认此类退款骗局近期高发，要求不要共享屏幕。',
                    'source': '警方通报',
                }
            ]
        }

        with patch('app.services.fact_check_service.get_settings', return_value=SimpleNamespace(
            SERPAPI_API_KEY='serp-key',
            SEARCH_API_KEY='',
            SEARCH_ENGINE_ID='',
        )), patch('app.services.fact_check_service.requests.get', return_value=fake_response) as request_mock:
            result = asyncio.run(check_fact('客服说要我开启屏幕共享来退款', use_advanced=True))

        request_mock.assert_called_once()
        self.assertEqual(result['query'], '客服说要我开启屏幕共享来退款')
        self.assertTrue(result['sources'])
        self.assertFalse(result['evidence_unavailable'])

    def test_check_fact_falls_back_to_google_search_when_serpapi_missing(self) -> None:
        fake_response = Mock()
        fake_response.status_code = 200
        fake_response.json.return_value = {
            'items': [
                {
                    'title': '案例提醒',
                    'link': 'https://example.com/fallback',
                    'snippet': '这是一种常见骗局，警方已辟谣并提醒提高警惕。',
                }
            ]
        }

        with patch('app.services.fact_check_service.get_settings', return_value=SimpleNamespace(
            SERPAPI_API_KEY='',
            SEARCH_API_KEY='google-key',
            SEARCH_ENGINE_ID='engine-id',
        )), patch('app.services.fact_check_service.requests.get', return_value=fake_response) as request_mock:
            result = asyncio.run(check_fact('有人让我先转账后解冻账户'))

        request_mock.assert_called_once()
        self.assertEqual(result['sources'][0]['url'], 'https://example.com/fallback')
        self.assertFalse(result['evidence_unavailable'])

    def test_check_fact_reports_provider_missing(self) -> None:
        with patch('app.services.fact_check_service.get_settings', return_value=SimpleNamespace(
            SERPAPI_API_KEY='',
            SEARCH_API_KEY='',
            SEARCH_ENGINE_ID='',
        )):
            result = asyncio.run(check_fact('这条承诺是真的吗'))

        self.assertTrue(result['evidence_unavailable'])
        self.assertIn('SERPAPI_API_KEY', result['explanation'])


if __name__ == '__main__':
    unittest.main()
