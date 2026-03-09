import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import app.api.v1.admin as admin_api
from app.api.v1.admin import router as admin_router


class EvidenceReviewFlowApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = FastAPI()
        self.app.include_router(admin_router, prefix='/api/v1/admin')
        self.app.dependency_overrides[admin_api.get_current_user] = lambda: SimpleNamespace(username='admin')
        self.app.dependency_overrides[admin_api.get_db] = lambda: AsyncMock(name='db')
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def _evidence_payload(self, status: str = 'pending') -> dict:
        return {
            'id': 11,
            'news_id': 'news-1',
            'content': '提供了原视频来源链接',
            'source': 'https://example.com/source',
            'submitted_by': 'alice',
            'submitted_at': '2026-03-01T10:00:00+00:00',
            'status': status,
            'reason': '',
            'reviewed_by': '',
            'reviewed_at': '',
        }

    def test_list_pending_submissions_returns_contract(self) -> None:
        fake_items = [SimpleNamespace(id=11), SimpleNamespace(id=12)]
        fake_result = SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: fake_items))
        fake_db = AsyncMock()
        fake_db.execute = AsyncMock(return_value=fake_result)

        self.app.dependency_overrides[admin_api.get_db] = lambda: fake_db

        with patch.object(
            admin_api,
            'serialize_evidence_item',
            side_effect=[
                self._evidence_payload('pending'),
                {**self._evidence_payload('pending'), 'id': 12, 'news_id': 'news-2'},
            ],
        ):
            resp = self.client.get('/api/v1/admin/submissions')

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['total'], 2)
        self.assertEqual(len(data['items']), 2)
        self.assertEqual(data['items'][0]['status'], 'pending')

    def test_review_submission_approved_returns_reviewed_contract(self) -> None:
        reviewed = self._evidence_payload('approved')
        reviewed.update({'reviewed_by': 'admin', 'reviewed_at': '2026-03-01T11:00:00+00:00'})

        with patch.object(
            admin_api,
            'review_evidence',
            AsyncMock(return_value=SimpleNamespace(id=11)),
        ) as review_mock, patch.object(
            admin_api,
            'serialize_evidence_item',
            return_value=reviewed,
        ):
            resp = self.client.post(
                '/api/v1/admin/submissions/11/review',
                json={'status': 'approved', 'reason': '证据链完整'},
            )

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['message'], '审核完成')
        self.assertEqual(data['item']['status'], 'approved')
        self.assertEqual(data['item']['reviewed_by'], 'admin')
        review_mock.assert_awaited_once_with(
            db=unittest.mock.ANY,
            submission_id=11,
            target_status='approved',
            reviewer_username='admin',
            reason='证据链完整',
        )

    def test_review_submission_404_is_propagated(self) -> None:
        with patch.object(
            admin_api,
            'review_evidence',
            AsyncMock(side_effect=HTTPException(status_code=404, detail='提交不存在')),
        ):
            resp = self.client.post('/api/v1/admin/submissions/999/review', json={'status': 'approved'})

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()['detail'], '提交不存在')


class EvidenceReviewFlowExceptionTests(unittest.TestCase):
    def test_review_submission_invalid_status_returns_422(self) -> None:
        app = FastAPI()
        app.include_router(admin_router, prefix='/api/v1/admin')
        app.dependency_overrides[admin_api.get_current_user] = lambda: SimpleNamespace(username='admin')
        app.dependency_overrides[admin_api.get_db] = lambda: AsyncMock(name='db')
        client = TestClient(app)

        resp = client.post('/api/v1/admin/submissions/11/review', json={'status': 'pending'})

        self.assertEqual(resp.status_code, 422)

    def test_submissions_requires_auth_without_override(self) -> None:
        app = FastAPI()
        app.include_router(admin_router, prefix='/api/v1/admin')
        app.dependency_overrides[admin_api.get_db] = lambda: AsyncMock(name='db')
        client = TestClient(app)

        resp = client.get('/api/v1/admin/submissions')

        self.assertEqual(resp.status_code, 403)


if __name__ == '__main__':
    unittest.main()
