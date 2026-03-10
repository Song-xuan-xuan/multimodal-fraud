import os
import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
for candidate in (BACKEND_DIR, PROJECT_ROOT):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from app.services.rag_service import append_rag_documents, load_index_manifest, persist_index_manifest


class FakeStorageContext:
    @staticmethod
    def from_defaults(*_args, **_kwargs):
        return SimpleNamespace()


class FakeIndex:
    def __init__(self):
        self.inserted = []
        self.storage_context = SimpleNamespace(persist=lambda **_kwargs: None)
        self.docstore = SimpleNamespace(docs={})

    def insert(self, document):
        self.inserted.append(document)


class FakeVectorStoreIndex:
    @staticmethod
    def from_documents(_documents):
        return FakeIndex()


def install_fake_llama_index_modules(fake_index):
    fake_core = types.ModuleType('llama_index.core')
    fake_core.VectorStoreIndex = FakeVectorStoreIndex
    fake_core.StorageContext = FakeStorageContext
    fake_core.Document = lambda **kwargs: SimpleNamespace(**kwargs)
    fake_core.Settings = SimpleNamespace(llm=None, embed_model=None, chunk_size=None)
    fake_core.load_index_from_storage = lambda _storage_context: fake_index

    fake_hf = types.ModuleType('llama_index.embeddings.huggingface')
    fake_hf.HuggingFaceEmbedding = SimpleNamespace

    fake_embeddings = types.ModuleType('llama_index.embeddings')
    fake_embeddings.huggingface = fake_hf

    fake_root = types.ModuleType('llama_index')
    fake_root.core = fake_core
    fake_root.embeddings = fake_embeddings

    fake_device = types.ModuleType('model.common.device')
    fake_device.resolve_device = lambda device: device

    return {
        'llama_index': fake_root,
        'llama_index.core': fake_core,
        'llama_index.embeddings': fake_embeddings,
        'llama_index.embeddings.huggingface': fake_hf,
        'model.common.device': fake_device,
    }


class RagIncrementalIndexingTests(unittest.TestCase):
    def test_append_updates_manifest_and_inserts_new_documents(self) -> None:
        fake_index = FakeIndex()
        fake_modules = install_fake_llama_index_modules(fake_index)

        temp_root = Path(PROJECT_ROOT) / '.claude' / 'test_rag_incremental'
        if temp_root.exists():
            for item in sorted(temp_root.rglob('*'), reverse=True):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
        temp_root.mkdir(parents=True, exist_ok=True)

        storage_path = temp_root / 'storage'
        storage_path.mkdir(parents=True, exist_ok=True)
        for filename in ('docstore.json', 'index_store.json', 'graph_store.json', 'vector_store.json'):
            (storage_path / filename).write_text('{}', encoding='utf-8')

        persist_index_manifest(storage_path, ['existing_1'])

        payload = [
            {
                'id': 'new_1',
                'type': 'case',
                'title': '标题',
                'content': '内容',
                'conclusion': '',
                'fraud_type': '',
                'risk_level': '',
                'source': 'test',
                'tags': [],
                'target_groups': [],
                'signals': [],
                'advice': [],
            }
        ]

        fake_settings = SimpleNamespace(
            storage_path=storage_path,
            data_path=temp_root,
            OPENAI_API_KEY='test-key',
            OPENAI_BASE_URL='https://example.com',
            OPENAI_MODEL='gpt-4o-mini',
            EMBEDDING_MODEL='BAAI/bge-small-zh-v1.5',
            EMBEDDING_DEVICE='cpu',
            CHUNK_SIZE=128,
        )

        with patch.dict(sys.modules, fake_modules),              patch('app.services.rag_service.get_settings', return_value=fake_settings),              patch('llama_index.embeddings.huggingface.HuggingFaceEmbedding', side_effect=lambda **kwargs: SimpleNamespace(**kwargs)):
            _, appended_count = append_rag_documents(payload)

        self.assertEqual(appended_count, 1)
        self.assertEqual(len(fake_index.inserted), 1)
        manifest = load_index_manifest(storage_path)
        self.assertEqual(set(manifest['indexed_item_ids']), {'existing_1', 'new_1'})

    def test_append_persists_via_temp_directory_before_replacing_live_files(self) -> None:
        fake_index = FakeIndex()
        persist_calls: list[Path] = []

        def fake_persist(**kwargs):
            persist_dir = Path(kwargs['persist_dir'])
            persist_calls.append(persist_dir)
            persist_dir.mkdir(parents=True, exist_ok=True)
            (persist_dir / 'docstore.json').write_text('{"doc":"new"}', encoding='utf-8')
            (persist_dir / 'index_store.json').write_text('{"index":"new"}', encoding='utf-8')
            (persist_dir / 'graph_store.json').write_text('{"graph":"new"}', encoding='utf-8')
            (persist_dir / 'default__vector_store.json').write_text(
                '{"embedding_dict":{"new":"vector"}}',
                encoding='utf-8',
            )

        fake_index.storage_context = SimpleNamespace(persist=fake_persist)
        fake_modules = install_fake_llama_index_modules(fake_index)

        temp_root = Path(PROJECT_ROOT) / '.claude' / 'test_rag_atomic_persist'
        if temp_root.exists():
            for item in sorted(temp_root.rglob('*'), reverse=True):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
        temp_root.mkdir(parents=True, exist_ok=True)

        storage_path = temp_root / 'storage'
        storage_path.mkdir(parents=True, exist_ok=True)
        (storage_path / 'docstore.json').write_text('{"doc":"old"}', encoding='utf-8')
        (storage_path / 'index_store.json').write_text('{"index":"old"}', encoding='utf-8')
        (storage_path / 'graph_store.json').write_text('{"graph":"old"}', encoding='utf-8')
        (storage_path / 'default__vector_store.json').write_text(
            '{"embedding_dict":{"old":"vector"}}',
            encoding='utf-8',
        )

        persist_index_manifest(storage_path, ['existing_1'])

        payload = [
            {
                'id': 'new_1',
                'type': 'case',
                'title': '标题',
                'content': '内容',
                'conclusion': '',
                'fraud_type': '',
                'risk_level': '',
                'source': 'test',
                'tags': [],
                'target_groups': [],
                'signals': [],
                'advice': [],
            }
        ]

        fake_settings = SimpleNamespace(
            storage_path=storage_path,
            data_path=temp_root,
            OPENAI_API_KEY='test-key',
            OPENAI_BASE_URL='https://example.com',
            OPENAI_MODEL='gpt-4o-mini',
            EMBEDDING_MODEL='BAAI/bge-small-zh-v1.5',
            EMBEDDING_DEVICE='cpu',
            CHUNK_SIZE=128,
        )

        with patch.dict(sys.modules, fake_modules),              patch('app.services.rag_service.get_settings', return_value=fake_settings),              patch('llama_index.embeddings.huggingface.HuggingFaceEmbedding', side_effect=lambda **kwargs: SimpleNamespace(**kwargs)):
            append_rag_documents(payload)

        self.assertEqual(len(persist_calls), 1)
        self.assertNotEqual(persist_calls[0], storage_path)
        self.assertFalse(persist_calls[0].exists())
        self.assertEqual(
            (storage_path / 'default__vector_store.json').read_text(encoding='utf-8'),
            '{"embedding_dict":{"new":"vector"}}',
        )


if __name__ == '__main__':
    unittest.main()
