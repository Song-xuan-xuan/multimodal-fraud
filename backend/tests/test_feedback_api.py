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

import app.api.v1.feedback as feedback_api
from app.api.v1.feedback import router as feedback_router


class FeedbackApiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = FastAPI()
        self.app.include_router(feedback_router, prefix='/api/v1/feedback')
        self.app.dependency_overrides[feedback_api.get_current_user] = lambda: SimpleNamespace(username='tester')
        self.app.dependency_overrides[feedback_api.get_db] = lambda: AsyncMock(name='db')
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def _feedback_item_payload(self, content: str = 'agree', status: str = 'pending') -> dict:
        return {
            'id': 101,
            'news_id': 'news-1',
            'type': 'vote' if content in {'agree', 'disagree'} else 'feedback',
            'content': content,
            'submitted_by': 'tester',
            'submitted_at': '2026-03-01T10:00:00+00:00',
            'updated_at': '2026-03-01T10:00:00+00:00',
            'status': status,
            'reason': '',
            'reviewed_by': '',
            'reviewed_at': '',
        }

    def test_submit_vote_returns_contract_fields(self) -> None:
        with patch.object(
            feedback_api,
            'submit_vote',
            AsyncMock(return_value=(SimpleNamespace(id=101), False)),
        ) as submit_vote_mock, patch.object(
            feedback_api,
            'serialize_feedback_item',
            return_value=self._feedback_item_payload('agree'),
        ):
            resp = self.client.post('/api/v1/feedback/submit-vote', json={'news_id': 'news-1', 'vote': 'agree'})

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['message'], '投票提交成功')
        self.assertTrue(data['idempotent'])
        self.assertIn('item', data)
        self.assertEqual(data['item']['type'], 'vote')
        submit_vote_mock.assert_awaited_once_with(unittest.mock.ANY, 'news-1', 'tester', 'agree')

    def test_submit_feedback_update_returns_non_idempotent(self) -> None:
        with patch.object(
            feedback_api,
            'submit_feedback',
            AsyncMock(return_value=(SimpleNamespace(id=202), True)),
        ) as submit_feedback_mock, patch.object(
            feedback_api,
            'serialize_feedback_item',
            return_value=self._feedback_item_payload('补充证据：原视频被剪辑'),
        ):
            resp = self.client.post(
                '/api/v1/feedback/submit-feedback',
                json={'news_id': 'news-1', 'feedback': '补充证据：原视频被剪辑'},
            )

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['message'], '反馈已更新')
        self.assertFalse(data['idempotent'])
        self.assertEqual(data['item']['type'], 'feedback')
        submit_feedback_mock.assert_awaited_once_with(
            unittest.mock.ANY,
            'news-1',
            'tester',
            '补充证据：原视频被剪辑',
        )

    def test_review_feedback_returns_review_contract(self) -> None:
        reviewed_payload = self._feedback_item_payload('agree', status='approved')
        reviewed_payload.update({'reviewed_by': 'tester', 'reviewed_at': '2026-03-01T11:00:00+00:00'})

        with patch.object(
            feedback_api,
            'review_feedback',
            AsyncMock(return_value=SimpleNamespace(id=101)),
        ) as review_feedback_mock, patch.object(
            feedback_api,
            'serialize_feedback_item',
            return_value=reviewed_payload,
        ):
            resp = self.client.post(
                '/api/v1/feedback/101/review',
                json={'status': 'approved', 'reason': '证据充分'},
            )

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['message'], '审核成功')
        self.assertEqual(data['item']['status'], 'approved')
        self.assertEqual(data['item']['reviewed_by'], 'tester')
        review_feedback_mock.assert_awaited_once_with(
            unittest.mock.ANY,
            submission_id=101,
            target_status='approved',
            reviewer_username='tester',
            reason='证据充分',
        )

    def test_list_my_feedback_forwards_filters_and_returns_page_contract(self) -> None:
        expected = {
            'items': [self._feedback_item_payload('agree')],
            'total': 1,
            'page': 2,
            'page_size': 10,
            'total_pages': 3,
        }
        with patch.object(feedback_api, 'list_my_feedback', AsyncMock(return_value=expected)) as list_mock:
            resp = self.client.get('/api/v1/feedback/my?page=2&page_size=10&type=vote&status=pending&news_id=news-1')

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['page'], 2)
        self.assertEqual(data['page_size'], 10)
        self.assertEqual(data['total_pages'], 3)
        self.assertEqual(len(data['items']), 1)
        list_mock.assert_awaited_once_with(
            unittest.mock.ANY,
            'tester',
            page=2,
            page_size=10,
            feedback_type='vote',
            status='pending',
            news_id='news-1',
        )

    def test_stats_returns_full_contract(self) -> None:
        stats_payload = {
            'news_id': 'news-1',
            'total': 5,
            'vote_total': 3,
            'vote_agree': 2,
            'vote_disagree': 1,
            'feedback_total': 2,
            'pending': 2,
            'approved': 2,
            'rejected': 1,
        }
        with patch.object(feedback_api, 'get_news_feedback_stats', AsyncMock(return_value=stats_payload)):
            resp = self.client.get('/api/v1/feedback/stats/news-1')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), stats_payload)


class FeedbackApiExceptionTests(unittest.TestCase):
    def test_submit_vote_invalid_vote_value_returns_422(self) -> None:
        app = FastAPI()
        app.include_router(feedback_router, prefix='/api/v1/feedback')
        app.dependency_overrides[feedback_api.get_current_user] = lambda: SimpleNamespace(username='tester')
        app.dependency_overrides[feedback_api.get_db] = lambda: AsyncMock(name='db')
        client = TestClient(app)

        resp = client.post('/api/v1/feedback/submit-vote', json={'news_id': 'news-1', 'vote': 'neutral'})

        self.assertEqual(resp.status_code, 422)

    def test_submit_feedback_requires_auth_header_when_not_overridden(self) -> None:
        app = FastAPI()
        app.include_router(feedback_router, prefix='/api/v1/feedback')
        app.dependency_overrides[feedback_api.get_db] = lambda: AsyncMock(name='db')
        client = TestClient(app)

        resp = client.post('/api/v1/feedback/submit-feedback', json={'news_id': 'news-1', 'feedback': 'x'})

        self.assertEqual(resp.status_code, 403)


if __name__ == '__main__':
    unittest.main()
