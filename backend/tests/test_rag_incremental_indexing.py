import json
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


class FakeCollection:
    def __init__(self, count: int = 0):
        self._count = count

    def count(self):
        return self._count


class FakePersistentClient:
    collections_by_name: dict[str, FakeCollection] = {}

    def __init__(self, path):
        self.path = Path(path)

    def get_collection(self, name: str):
        if name not in self.collections_by_name:
            raise ValueError(name)
        return self.collections_by_name[name]

    def get_or_create_collection(self, name: str):
        collection = self.collections_by_name.get(name)
        if collection is None:
            collection = FakeCollection()
            self.collections_by_name[name] = collection
        return collection

    def delete_collection(self, name: str):
        self.collections_by_name.pop(name, None)

    @classmethod
    def reset(cls):
        cls.collections_by_name = {}


class FakeChromaVectorStore:
    def __init__(self, chroma_collection):
        self.chroma_collection = chroma_collection


class FakeIndex:
    def __init__(self):
        self.inserted = []
        self.docstore = SimpleNamespace(docs={})

    def insert(self, document):
        self.inserted.append(document)


class FakeVectorStoreIndex:
    created_documents = None
    created_index = None
    loaded_index = None

    @classmethod
    def from_documents(cls, documents, storage_context=None):
        cls.created_documents = list(documents)
        cls.created_index = FakeIndex()
        return cls.created_index

    @classmethod
    def from_vector_store(cls, vector_store):
        cls.loaded_index = FakeIndex()
        return cls.loaded_index

    @classmethod
    def reset(cls):
        cls.created_documents = None
        cls.created_index = None
        cls.loaded_index = None


def install_fake_modules():
    fake_core = types.ModuleType('llama_index.core')
    fake_core.VectorStoreIndex = FakeVectorStoreIndex
    fake_core.StorageContext = SimpleNamespace(from_defaults=lambda **kwargs: SimpleNamespace(**kwargs))
    fake_core.Document = lambda **kwargs: SimpleNamespace(**kwargs)
    fake_core.Settings = SimpleNamespace(llm=None, embed_model=None, chunk_size=None)

    fake_hf = types.ModuleType('llama_index.embeddings.huggingface')
    fake_hf.HuggingFaceEmbedding = SimpleNamespace

    fake_embeddings = types.ModuleType('llama_index.embeddings')
    fake_embeddings.huggingface = fake_hf

    fake_vs_chroma = types.ModuleType('llama_index.vector_stores.chroma')
    fake_vs_chroma.ChromaVectorStore = FakeChromaVectorStore

    fake_vector_stores = types.ModuleType('llama_index.vector_stores')
    fake_vector_stores.chroma = fake_vs_chroma

    fake_root = types.ModuleType('llama_index')
    fake_root.core = fake_core
    fake_root.embeddings = fake_embeddings
    fake_root.vector_stores = fake_vector_stores

    fake_chromadb = types.ModuleType('chromadb')
    fake_chromadb.PersistentClient = FakePersistentClient

    fake_device = types.ModuleType('model.common.device')
    fake_device.resolve_device = lambda device: device

    return {
        'llama_index': fake_root,
        'llama_index.core': fake_core,
        'llama_index.embeddings': fake_embeddings,
        'llama_index.embeddings.huggingface': fake_hf,
        'llama_index.vector_stores': fake_vector_stores,
        'llama_index.vector_stores.chroma': fake_vs_chroma,
        'chromadb': fake_chromadb,
        'model.common.device': fake_device,
    }


class RagIncrementalIndexingTests(unittest.TestCase):
    def setUp(self) -> None:
        FakePersistentClient.reset()
        FakeVectorStoreIndex.reset()

    def _make_temp_root(self, name: str) -> Path:
        temp_root = Path(PROJECT_ROOT) / '.claude' / name
        if temp_root.exists():
            for item in sorted(temp_root.rglob('*'), reverse=True):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
        temp_root.mkdir(parents=True, exist_ok=True)
        return temp_root

    def test_append_initializes_new_chroma_index_and_manifest(self) -> None:
        fake_modules = install_fake_modules()

        temp_root = self._make_temp_root('test_rag_append_initial')
        storage_path = temp_root / 'storage'
        storage_path.mkdir(parents=True, exist_ok=True)
        chroma_path = storage_path / 'chroma_db'
        chroma_path.mkdir(parents=True, exist_ok=True)

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
            chroma_path=chroma_path,
            CHROMA_COLLECTION_NAME='fraud_knowledge',
            data_path=temp_root,
            OPENAI_API_KEY='test-key',
            OPENAI_BASE_URL='https://example.com',
            OPENAI_MODEL='gpt-4o-mini',
            EMBEDDING_MODEL='BAAI/bge-small-zh-v1.5',
            EMBEDDING_DEVICE='cpu',
            CHUNK_SIZE=128,
        )

        with patch.dict(sys.modules, fake_modules), \
             patch('app.services.rag_service.get_settings', return_value=fake_settings), \
             patch('llama_index.embeddings.huggingface.HuggingFaceEmbedding', side_effect=lambda **kwargs: SimpleNamespace(**kwargs)):
            result_path, appended_count = append_rag_documents(payload)

        self.assertEqual(appended_count, 1)
        self.assertEqual(result_path, chroma_path)
        self.assertEqual(len(FakeVectorStoreIndex.created_documents), 1)
        manifest = load_index_manifest(storage_path)
        self.assertEqual(set(manifest['indexed_item_ids']), {'new_1'})

    def test_append_uses_existing_loaded_index_and_updates_manifest(self) -> None:
        fake_modules = install_fake_modules()

        temp_root = self._make_temp_root('test_rag_append_existing')
        storage_path = temp_root / 'storage'
        storage_path.mkdir(parents=True, exist_ok=True)
        chroma_path = storage_path / 'chroma_db'
        chroma_path.mkdir(parents=True, exist_ok=True)
        FakePersistentClient.collections_by_name = {'fraud_knowledge': FakeCollection(count=2)}

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
            chroma_path=chroma_path,
            CHROMA_COLLECTION_NAME='fraud_knowledge',
            data_path=temp_root,
            OPENAI_API_KEY='test-key',
            OPENAI_BASE_URL='https://example.com',
            OPENAI_MODEL='gpt-4o-mini',
            EMBEDDING_MODEL='BAAI/bge-small-zh-v1.5',
            EMBEDDING_DEVICE='cpu',
            CHUNK_SIZE=128,
        )

        with patch.dict(sys.modules, fake_modules), \
             patch('app.services.rag_service.get_settings', return_value=fake_settings), \
             patch('llama_index.embeddings.huggingface.HuggingFaceEmbedding', side_effect=lambda **kwargs: SimpleNamespace(**kwargs)):
            append_rag_documents(payload)

        self.assertIsNotNone(FakeVectorStoreIndex.loaded_index)
        self.assertEqual(len(FakeVectorStoreIndex.loaded_index.inserted), 1)
        manifest = load_index_manifest(storage_path)
        self.assertEqual(set(manifest['indexed_item_ids']), {'existing_1', 'new_1'})


if __name__ == '__main__':
    unittest.main()
