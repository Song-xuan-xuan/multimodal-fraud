import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import app.api.v1.news as news_api
from app.api.v1.news import router as news_router
from app.schemas.news import NewsDetailResponse
from app.services.news_service import get_news_aggregated_detail


class NewsDetailApiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        app = FastAPI()
        app.include_router(news_router, prefix='/api/v1/news')
        self.client = TestClient(app)

    def test_detail_endpoint_returns_full_contract_fields(self) -> None:
        payload = {
            'news_id': 'news-1',
            'title': '测试新闻',
            'content': '正文',
            'url': 'https://example.com/n1',
            'pic_url': 'https://example.com/n1.png',
            'label': '谣言',
            'platform': '微博',
            'hashtag': '#测试',
            'summary': '摘要',
            'location': '北京',
            'conclusion': '结论',
            'publish_time': '2026-01-01 10:00:00',
            'check_time': '2026-01-01 11:00:00',
            'iscredit': False,
            'credibility': {
                'score': 0.36,
                'dimension_scores': {
                    'source': 0.2,
                    'content': 0.4,
                    'logic': 0.3,
                    'propagation': 0.5,
                    'AI': 0.4,
                    'content1': 'x',
                    'content2': 'y',
                },
                'verification_progress': 78,
                'verified': False,
            },
            'propagation': {
                'total_mentions': 330,
                'peak_timestamp': '2026-01-01 12:00:00',
                'trend': [{'timestamp': '2026-01-01 10:00:00', 'value': 120}],
                'platform_distribution': [{'platform': '微博', 'count': 210, 'ratio': 0.6364}],
                'region_distribution': [{'region': '北京', 'count': 80}],
            },
            'relations': {
                'related_news': [
                    {
                        'news_id': 'news-2',
                        'title': '关联新闻',
                        'similarity': 0.0,
                        'platform': '微博',
                        'publish_time': '2026-01-01 10:30:00',
                        'url': 'https://example.com/n2',
                    }
                ],
                'nodes': [{'node_id': 'knowledge:0', 'name': '关键词', 'category': 'knowledge', 'value': 1.0}],
                'edges': [{'source': 'news-1', 'target': 'news-2', 'relation_type': 'related_rumor', 'weight': 1.0}],
            },
            'ui_fallbacks': {
                'summary': '暂无摘要',
                'conclusion': '暂无结论',
                'propagation_empty_reason': '暂无传播数据',
                'relations_empty_reason': '暂无关联关系数据',
            },
            'propagation_data': {'timeline': [{'platform': '微博', 'shares': 120}]},
            'relations_data': {'related_rumors': ['news-2']},
        }

        with patch.object(
            news_api,
            'get_news_aggregated_detail',
            AsyncMock(return_value=NewsDetailResponse(**payload)),
        ):
            resp = self.client.get('/api/v1/news/news-1/detail')

        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        expected_top_fields = {
            'news_id',
            'title',
            'content',
            'url',
            'pic_url',
            'label',
            'platform',
            'hashtag',
            'summary',
            'location',
            'conclusion',
            'publish_time',
            'check_time',
            'iscredit',
            'credibility',
            'propagation',
            'relations',
            'ui_fallbacks',
            'propagation_data',
            'relations_data',
        }
        self.assertTrue(expected_top_fields.issubset(data.keys()))
        self.assertIn('dimension_scores', data['credibility'])
        self.assertIn('trend', data['propagation'])
        self.assertIn('platform_distribution', data['propagation'])
        self.assertIn('region_distribution', data['propagation'])
        self.assertIn('related_news', data['relations'])
        self.assertIn('nodes', data['relations'])
        self.assertIn('edges', data['relations'])

    def test_legacy_news_endpoint_shape_is_unchanged(self) -> None:
        legacy_news = SimpleNamespace(
            news_id='news-legacy',
            title='旧接口新闻',
            content='old-content',
            url='https://example.com/legacy',
            pic_url='',
            label='未知',
            platform='微博',
            hashtag='',
            summary='',
            location='',
            conclusion='',
            publish_time='2026-01-01',
            check_time='2026-01-02',
            iscredit=None,
            credibility_score=0.0,
            credibility_dimensions=None,
            verification_progress=None,
            verified=None,
            propagation_data=None,
            relations_data=None,
        )

        with patch.object(news_api, 'get_news_detail', AsyncMock(return_value=legacy_news)):
            resp = self.client.get('/api/v1/news/news-legacy')

        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # 旧接口应继续返回 NewsResponse，不包含聚合后的 propagation/relations/ui_fallbacks
        self.assertIn('news_id', data)
        self.assertIn('credibility', data)
        self.assertIn('propagation_data', data)
        self.assertIn('relations_data', data)
        self.assertNotIn('propagation', data)
        self.assertNotIn('relations', data)
        self.assertNotIn('ui_fallbacks', data)


class NewsDetailAggregationNullSampleTests(unittest.IsolatedAsyncioTestCase):
    async def test_aggregation_fills_defaults_for_null_and_empty_samples(self) -> None:
        news_row = SimpleNamespace(
            news_id='news-null',
            title=None,
            content=None,
            url=None,
            pic_url=None,
            label=None,
            platform=None,
            hashtag=None,
            summary=None,
            location=None,
            conclusion=None,
            publish_time=None,
            check_time=None,
            iscredit=None,
            credibility_score=None,
            credibility_dimensions='invalid',
            verification_progress=None,
            verified=None,
            propagation_data='invalid',
            relations_data='invalid',
        )

        fake_db = AsyncMock()

        with patch('app.services.news_service.get_news', AsyncMock(return_value=news_row)), patch(
            'app.services.news_service.get_news_by_ids', AsyncMock(return_value={})
        ):
            detail = await get_news_aggregated_detail(fake_db, 'news-null')

        self.assertEqual(detail.news_id, 'news-null')
        self.assertEqual(detail.title, '')
        self.assertEqual(detail.content, '暂无内容')
        self.assertEqual(detail.url, '#')
        self.assertEqual(detail.summary, '暂无摘要')
        self.assertEqual(detail.conclusion, '暂无结论')
        self.assertEqual(detail.label, '未知')
        self.assertFalse(detail.iscredit)

        self.assertEqual(detail.credibility.score, 0.0)
        self.assertEqual(detail.credibility.verification_progress, 0)
        self.assertFalse(detail.credibility.verified)
        self.assertEqual(detail.credibility.dimension_scores.source, 0.0)

        self.assertEqual(detail.propagation.total_mentions, 0)
        self.assertEqual(detail.propagation.peak_timestamp, '')
        self.assertEqual(detail.propagation.trend, [])
        self.assertEqual(detail.propagation.platform_distribution, [])
        self.assertEqual(detail.propagation.region_distribution, [])

        self.assertEqual(detail.relations.related_news, [])
        self.assertEqual(detail.relations.nodes, [])
        self.assertEqual(detail.relations.edges, [])

        self.assertEqual(detail.ui_fallbacks.summary, '暂无摘要')
        self.assertEqual(detail.ui_fallbacks.propagation_empty_reason, '暂无传播数据')
        self.assertEqual(detail.propagation_data, {})
        self.assertEqual(detail.relations_data, {})


if __name__ == '__main__':
    unittest.main()
