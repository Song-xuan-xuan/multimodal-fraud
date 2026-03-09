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

import app.api.v1.alerts as alerts_api
from app.api.v1.alerts import router as alerts_router


class AlertsApiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = FastAPI()
        self.app.include_router(alerts_router, prefix='/api/v1/alerts')
        self.app.dependency_overrides[alerts_api.get_current_user] = lambda: SimpleNamespace(username='tester')
        self.app.dependency_overrides[alerts_api.get_db] = lambda: AsyncMock(name='db')
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()

    def _alert_item_payload(self, status: str = 'pending') -> dict:
        return {
            'alert_id': 'alt_abc123456789',
            'alert_type': 'feedback_review',
            'title': '有新反馈待审核',
            'message': 'news-1 出现新的用户反馈',
            'recipient_username': 'reviewer',
            'created_by': 'tester',
            'metadata': {'news_id': 'news-1'},
            'status': status,
            'review_feedback': '',
            'reviewed_by': '',
            'reviewed_at': '',
            'created_at': '2026-03-01T10:00:00+00:00',
            'updated_at': '2026-03-01T10:00:00+00:00',
        }

    def _event_payload(self, event: str, status: str = 'pending') -> dict:
        return {
            'event': event,
            'contract_version': 'v1',
            'occurred_at': '2026-03-01T10:00:00+00:00',
            'recipient_username': 'reviewer',
            'triggered_by': 'tester',
            'alert': self._alert_item_payload(status),
        }

    def test_create_alert_returns_contract_and_pushes_ws_event(self) -> None:
        item = SimpleNamespace(alert_id='alt_abc123456789')
        event = self._event_payload('alert_created')

        with patch.object(alerts_api, 'create_alert', AsyncMock(return_value=(item, event))) as create_mock, patch.object(
            alerts_api,
            'serialize_alert_item',
            return_value=self._alert_item_payload(),
        ), patch.object(
            alerts_api,
            'push_alert_created_event',
            AsyncMock(),
        ) as push_mock:
            resp = self.client.post(
                '/api/v1/alerts',
                json={
                    'alert_type': 'feedback_review',
                    'title': '有新反馈待审核',
                    'message': 'news-1 出现新的用户反馈',
                    'recipient_username': 'reviewer',
                    'metadata': {'news_id': 'news-1'},
                },
            )

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['message'], '警报创建成功')
        self.assertEqual(data['item']['alert_id'], 'alt_abc123456789')
        self.assertEqual(data['event']['event'], 'alert_created')
        create_mock.assert_awaited_once()
        push_mock.assert_awaited_once_with(event)

    def test_review_alert_returns_contract_and_pushes_review_event(self) -> None:
        item = SimpleNamespace(alert_id='alt_abc123456789')
        reviewed_item = self._alert_item_payload(status='approved')
        reviewed_item.update({'reviewed_by': 'tester', 'reviewed_at': '2026-03-01T11:00:00+00:00'})
        event = self._event_payload('review_updated', status='approved')

        with patch.object(alerts_api, 'review_alert', AsyncMock(return_value=(item, event))) as review_mock, patch.object(
            alerts_api,
            'serialize_alert_item',
            return_value=reviewed_item,
        ), patch.object(
            alerts_api,
            'push_review_updated_event',
            AsyncMock(),
        ) as push_mock:
            resp = self.client.post(
                '/api/v1/alerts/alt_abc123456789/review',
                json={'status': 'approved', 'feedback': '内容清晰，予以通过'},
            )

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['message'], '警报审核成功')
        self.assertEqual(data['item']['status'], 'approved')
        self.assertEqual(data['event']['event'], 'review_updated')
        review_mock.assert_awaited_once_with(
            unittest.mock.ANY,
            alert_id='alt_abc123456789',
            target_status='approved',
            reviewer_username='tester',
            feedback='内容清晰，予以通过',
        )
        push_mock.assert_awaited_once_with(event)

    def test_list_my_alerts_returns_paging_contract(self) -> None:
        payload = {
            'items': [self._alert_item_payload()],
            'total': 1,
            'page': 1,
            'page_size': 20,
            'total_pages': 1,
        }
        with patch.object(alerts_api, 'list_my_alerts', AsyncMock(return_value=payload)) as list_mock:
            resp = self.client.get('/api/v1/alerts/my?page=1&page_size=20&status=pending')

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['items'][0]['status'], 'pending')
        list_mock.assert_awaited_once_with(
            unittest.mock.ANY,
            'tester',
            page=1,
            page_size=20,
            status='pending',
        )


class AlertsApiExceptionTests(unittest.TestCase):
    def test_review_alert_invalid_status_returns_422(self) -> None:
        app = FastAPI()
        app.include_router(alerts_router, prefix='/api/v1/alerts')
        app.dependency_overrides[alerts_api.get_current_user] = lambda: SimpleNamespace(username='tester')
        app.dependency_overrides[alerts_api.get_db] = lambda: AsyncMock(name='db')
        client = TestClient(app)

        resp = client.post('/api/v1/alerts/alt_x/review', json={'status': 'pending', 'feedback': 'x'})

        self.assertEqual(resp.status_code, 422)

    def test_create_alert_requires_auth_header_when_not_overridden(self) -> None:
        app = FastAPI()
        app.include_router(alerts_router, prefix='/api/v1/alerts')
        app.dependency_overrides[alerts_api.get_db] = lambda: AsyncMock(name='db')
        client = TestClient(app)

        resp = client.post(
            '/api/v1/alerts',
            json={'title': 't', 'message': 'm', 'alert_type': 'feedback_review', 'metadata': {}},
        )

        self.assertEqual(resp.status_code, 403)


if __name__ == '__main__':
    unittest.main()
