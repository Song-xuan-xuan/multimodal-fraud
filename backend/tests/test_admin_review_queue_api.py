import asyncio
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import app.api.v1.admin as admin_api
from app.core import deps as core_deps
from app.api.v1.admin import router as admin_router
from app.db.base import Base
from app.db.models.report import Report


class AdminReviewQueueApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._temp_db.close()
        self._db_url = f"sqlite+aiosqlite:///{self._temp_db.name.replace(os.sep, '/')}"
        self._engine = create_async_engine(self._db_url, future=True)
        self._session_maker = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)
        asyncio.run(self._prepare_database())

        self.app = FastAPI()
        self.app.include_router(admin_router, prefix="/api/v1/admin")
        self.app.dependency_overrides[admin_api.get_current_admin_user] = lambda: SimpleNamespace(username="admin")
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
            session.add_all(
                [
                    Report(
                        report_id="rpt_pending_001",
                        type="举报",
                        url="https://example.com/pending",
                        description="待审核举报",
                        reported_by="alice",
                        status="pending",
                        created_at=datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc),
                    ),
                    Report(
                        report_id="rpt_approved_001",
                        type="举报",
                        url="https://example.com/approved",
                        description="已通过举报",
                        reported_by="bob",
                        status="approved",
                        review_reason="证据充分",
                        reviewed_by="admin",
                        reviewed_at=datetime(2026, 3, 10, 9, 5, tzinfo=timezone.utc),
                        created_at=datetime(2026, 3, 10, 8, 0, tzinfo=timezone.utc),
                    ),
                    Report(
                        report_id="rpt_rejected_001",
                        type="举报",
                        url="https://example.com/rejected",
                        description="已驳回举报",
                        reported_by="carol",
                        status="rejected",
                        review_reason="信息不足",
                        reviewed_by="admin",
                        reviewed_at=datetime(2026, 3, 10, 9, 10, tzinfo=timezone.utc),
                        created_at=datetime(2026, 3, 10, 7, 0, tzinfo=timezone.utc),
                    ),
                ]
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

    def test_submissions_includes_pending_and_reviewed_items(self) -> None:
        resp = self.client.get("/api/v1/admin/submissions")

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total"], 3)
        self.assertEqual([item["status"] for item in data["items"]], ["pending", "approved", "rejected"])
        self.assertEqual(data["items"][1]["reviewed_by"], "admin")
        self.assertEqual(data["items"][2]["review_reason"], "信息不足")

    def test_submissions_forbidden_for_non_admin_user(self) -> None:
        self.app.dependency_overrides.pop(admin_api.get_current_admin_user, None)
        self.app.dependency_overrides[core_deps.get_current_user] = lambda: SimpleNamespace(username="alice")

        resp = self.client.get("/api/v1/admin/submissions")

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()["detail"], "无权限访问")

    def test_submissions_forbidden_for_legacy_admin_alias(self) -> None:
        self.app.dependency_overrides.pop(admin_api.get_current_admin_user, None)
        self.app.dependency_overrides[core_deps.get_current_user] = lambda: SimpleNamespace(username="administrator")

        resp = self.client.get("/api/v1/admin/submissions")

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()["detail"], "无权限访问")


if __name__ == "__main__":
    unittest.main()
