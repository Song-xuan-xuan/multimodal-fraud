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

import app.api.v1.community as community_api
from app.api.v1.community import router as community_router


class CommunityEvidenceApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = FastAPI()
        self.app.include_router(community_router, prefix='/api/v1/community')
        self.app.dependency_overrides[community_api.get_current_user] = lambda: SimpleNamespace(username='tester')
        self.app.dependency_overrides[community_api.get_db] = lambda: AsyncMock(name='db')
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def test_my_evidence_route_uses_submission_list_handler(self) -> None:
        fake_items = [SimpleNamespace(id=1)]
        fake_result = SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: fake_items))
        fake_db = AsyncMock()
        fake_db.execute = AsyncMock(return_value=fake_result)
        self.app.dependency_overrides[community_api.get_db] = lambda: fake_db

        with patch.object(
            community_api,
            'serialize_evidence_item',
            return_value={
                'id': 1,
                'news_id': 'news-1',
                'content': '证据内容',
                'source': 'https://example.com',
                'submitted_by': 'tester',
                'submitted_at': '2026-03-18T10:00:00+08:00',
                'status': 'pending',
                'reason': '',
                'reviewed_by': '',
                'reviewed_at': '',
            },
        ):
            resp = self.client.get('/api/v1/community/evidence/my')

        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(payload['total'], 1)
        self.assertEqual(payload['items'][0]['submitted_by'], 'tester')


if __name__ == '__main__':
    unittest.main()