import asyncio
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import app.api.v1.admin as admin_api
from app.api.v1.admin import router as admin_router
from app.db.base import Base
from app.db.models.report import Report


class EvidenceReviewFlowApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self._temp_db.close()
        self._db_url = f"sqlite+aiosqlite:///{self._temp_db.name.replace(os.sep, '/')}"
        self._engine = create_async_engine(self._db_url, future=True)
        self._session_maker = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)
        asyncio.run(self._prepare_database())

        self.app = FastAPI()
        self.app.include_router(admin_router, prefix='/api/v1/admin')
        self.app.dependency_overrides[admin_api.get_current_admin_user] = lambda: SimpleNamespace(username='admin')
        self.app.dependency_overrides[admin_api.get_db] = self._override_get_db
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()
        asyncio.run(self._dispose_database())
        if os.path.exists(self._temp_db.name):
            os.unlink(self._temp_db.name)

    async def _prepare_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with self._session_maker() as session:
            session.add(
                Report(
                    report_id='rpt_test_001',
                    type='举报',
                    url='https://example.com/report',
                    description='提供了新的线索材料',
                    reported_by='alice',
                    status='pending',
                )
            )
            await session.commit()

    async def _dispose_database(self) -> None:
        await self._engine.dispose()

    async def _override_get_db(self):
        async with self._session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def _get_report(self, report_id: int) -> Report | None:
        async with self._session_maker() as session:
            result = await session.execute(select(Report).where(Report.id == report_id))
            return result.scalar_one_or_none()

    def test_review_submission_approved_returns_reviewed_contract(self) -> None:
        report = asyncio.run(self._get_report(1))
        self.assertIsNotNone(report)

        resp = self.client.post(
            '/api/v1/admin/submissions/1/review',
            json={'status': 'approved', 'reason': '证据链完整'},
        )

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['message'], '审核完成')
        self.assertEqual(data['item']['status'], 'approved')
        self.assertEqual(data['item']['review_reason'], '证据链完整')
        self.assertEqual(data['item']['reviewed_by'], 'admin')
        self.assertTrue(data['item']['reviewed_at'])

        updated = asyncio.run(self._get_report(1))
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, 'approved')
        self.assertEqual(updated.review_reason, '证据链完整')
        self.assertEqual(updated.reviewed_by, 'admin')
        self.assertIsNotNone(updated.reviewed_at)

    def test_review_submission_404_is_propagated(self) -> None:
        resp = self.client.post('/api/v1/admin/submissions/999/review', json={'status': 'approved'})

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()['detail'], '举报记录不存在')


if __name__ == '__main__':
    unittest.main()
