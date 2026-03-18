import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
for candidate in (BACKEND_DIR, PROJECT_ROOT):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from app.services.knowledge_service import rebuild_knowledge_index


class FakeScalarResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return self

    def all(self):
        return list(self._items)


class KnowledgeServiceRagIndexingTests(unittest.IsolatedAsyncioTestCase):
    async def test_rebuilds_full_index_when_chroma_is_missing_even_if_manifest_exists(self) -> None:
        items = [
            SimpleNamespace(
                item_id='existing_1',
                item_type='case',
                title='标题1',
                content='内容1',
                conclusion='',
                fraud_type='',
                risk_level='',
                source='test',
                tags=[],
                target_groups=[],
                signals=[],
                advice=[],
            ),
            SimpleNamespace(
                item_id='new_2',
                item_type='case',
                title='标题2',
                content='内容2',
                conclusion='',
                fraud_type='',
                risk_level='',
                source='test',
                tags=[],
                target_groups=[],
                signals=[],
                advice=[],
            ),
        ]
        db = AsyncMock()
        db.execute = AsyncMock(return_value=FakeScalarResult(items))
        settings = SimpleNamespace(
            storage_path=Path(PROJECT_ROOT) / '.claude' / 'manifest-storage',
            chroma_path=Path(PROJECT_ROOT) / '.claude' / 'chroma-storage',
            CHROMA_COLLECTION_NAME='fraud_knowledge',
        )

        with patch('app.services.knowledge_service.get_settings', return_value=settings), \
             patch('app.services.knowledge_service.export_approved_knowledge', AsyncMock(return_value=(Path('backend/data/fraud_knowledge.json'), 2))), \
             patch('app.services.knowledge_service.load_index_manifest', return_value={'indexed_item_ids': ['existing_1']}), \
             patch('app.services.knowledge_service.has_persisted_rag_index', return_value=False), \
             patch('app.services.knowledge_service.rebuild_rag_index', return_value=settings.chroma_path) as rebuild_mock, \
             patch('app.services.knowledge_service.persist_index_manifest') as persist_mock, \
             patch('app.services.knowledge_service.append_rag_documents') as append_mock:
            result = await rebuild_knowledge_index(db)

        rebuild_mock.assert_called_once()
        append_mock.assert_not_called()
        persist_mock.assert_called_once_with(settings.storage_path, ['existing_1', 'new_2'])
        self.assertEqual(str(settings.chroma_path), result['storage_path'])

    async def test_appends_only_new_items_when_chroma_is_ready(self) -> None:
        items = [
            SimpleNamespace(
                item_id='existing_1',
                item_type='case',
                title='标题1',
                content='内容1',
                conclusion='',
                fraud_type='',
                risk_level='',
                source='test',
                tags=[],
                target_groups=[],
                signals=[],
                advice=[],
            ),
            SimpleNamespace(
                item_id='new_2',
                item_type='case',
                title='标题2',
                content='内容2',
                conclusion='',
                fraud_type='诈骗',
                risk_level='medium',
                source='test',
                tags=['tag'],
                target_groups=['学生'],
                signals=['转账'],
                advice=['报警'],
            ),
        ]
        db = AsyncMock()
        db.execute = AsyncMock(return_value=FakeScalarResult(items))
        settings = SimpleNamespace(
            storage_path=Path(PROJECT_ROOT) / '.claude' / 'manifest-storage',
            chroma_path=Path(PROJECT_ROOT) / '.claude' / 'chroma-storage',
            CHROMA_COLLECTION_NAME='fraud_knowledge',
        )

        with patch('app.services.knowledge_service.get_settings', return_value=settings), \
             patch('app.services.knowledge_service.export_approved_knowledge', AsyncMock(return_value=(Path('backend/data/fraud_knowledge.json'), 2))), \
             patch('app.services.knowledge_service.load_index_manifest', return_value={'indexed_item_ids': ['existing_1']}), \
             patch('app.services.knowledge_service.has_persisted_rag_index', return_value=True), \
             patch('app.services.knowledge_service.rebuild_rag_index') as rebuild_mock, \
             patch('app.services.knowledge_service.append_rag_documents', return_value=(settings.chroma_path, 1)) as append_mock:
            result = await rebuild_knowledge_index(db)

        rebuild_mock.assert_not_called()
        append_mock.assert_called_once()
        new_payload = append_mock.call_args.args[0]
        self.assertEqual(1, len(new_payload))
        self.assertEqual('new_2', new_payload[0]['id'])
        self.assertEqual('诈骗', new_payload[0]['fraud_type'])
        self.assertEqual(str(settings.chroma_path), result['storage_path'])


if __name__ == '__main__':
    unittest.main()
