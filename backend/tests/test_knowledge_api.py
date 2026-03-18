import asyncio
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import app.api.v1.knowledge as knowledge_api
from app.core import deps as core_deps
from app.api.v1.knowledge import router as knowledge_router
from app.db.base import Base
from app.db.models.knowledge_item import KnowledgeItem


class KnowledgeApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._temp_db.close()
        self._db_url = f"sqlite+aiosqlite:///{self._temp_db.name.replace(os.sep, '/')}"
        self._engine = create_async_engine(self._db_url, future=True)
        self._session_maker = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)
        asyncio.run(self._prepare_database())

        self.app = FastAPI()
        self.app.include_router(knowledge_router, prefix="/api/v1/knowledge")
        self.app.dependency_overrides[knowledge_api.get_current_admin_user] = lambda: SimpleNamespace(username="admin")
        self.app.dependency_overrides[knowledge_api.get_db] = self._override_get_db
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
                    KnowledgeItem(
                        item_id="case_001",
                        item_type="case",
                        title="测试案例",
                        content="需要被删除的知识条目",
                        fraud_type="fake_news",
                        source="unit-test",
                        status="pending",
                        submitted_by="admin",
                        created_at=datetime(2026, 3, 18, 9, 0, tzinfo=timezone.utc),
                        updated_at=datetime(2026, 3, 18, 9, 0, tzinfo=timezone.utc),
                    ),
                    KnowledgeItem(
                        item_id="case_002",
                        item_type="case",
                        title="保留案例",
                        content="保留的知识条目",
                        fraud_type="fake_news",
                        source="unit-test",
                        status="approved",
                        submitted_by="admin",
                        created_at=datetime(2026, 3, 18, 9, 5, tzinfo=timezone.utc),
                        updated_at=datetime(2026, 3, 18, 9, 5, tzinfo=timezone.utc),
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

    async def _knowledge_ids(self) -> list[int]:
        async with self._session_maker() as session:
            result = await session.execute(select(KnowledgeItem.id).order_by(KnowledgeItem.id.asc()))
            return list(result.scalars().all())

    async def _item_exists(self, item_id: int) -> bool:
        async with self._session_maker() as session:
            result = await session.execute(select(KnowledgeItem).where(KnowledgeItem.id == item_id))
            return result.scalar_one_or_none() is not None

    def test_delete_knowledge_item_removes_row_from_database(self) -> None:
        before_ids = asyncio.run(self._knowledge_ids())
        target_id = before_ids[0]

        resp = self.client.delete(f"/api/v1/knowledge/items/{target_id}")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["message"], "知识条目已删除")
        self.assertFalse(asyncio.run(self._item_exists(target_id)))
        self.assertEqual(len(before_ids) - 1, len(asyncio.run(self._knowledge_ids())))

    def test_delete_knowledge_item_returns_not_found_for_missing_id(self) -> None:
        resp = self.client.delete("/api/v1/knowledge/items/9999")

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["detail"], "知识条目不存在")

    def test_list_knowledge_forbidden_for_non_admin_user(self) -> None:
        self.app.dependency_overrides.pop(knowledge_api.get_current_admin_user, None)
        self.app.dependency_overrides[core_deps.get_current_user] = lambda: SimpleNamespace(username="alice")

        resp = self.client.get("/api/v1/knowledge/items")

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()["detail"], "无权限访问")

    def test_delete_knowledge_item_forbidden_for_non_admin_user(self) -> None:
        self.app.dependency_overrides.pop(knowledge_api.get_current_admin_user, None)
        self.app.dependency_overrides[core_deps.get_current_user] = lambda: SimpleNamespace(username="alice")
        target_id = asyncio.run(self._knowledge_ids())[0]

        resp = self.client.delete(f"/api/v1/knowledge/items/{target_id}")

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.json()["detail"], "无权限访问")


if __name__ == "__main__":
    unittest.main()
