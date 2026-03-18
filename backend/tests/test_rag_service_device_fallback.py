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

from model.rag.service import RAGIndexService, has_persisted_rag_index


class FakeCollection:
    def __init__(self, count: int = 0):
        self._count = count

    def count(self):
        return self._count


class FakePersistentClient:
    collections_by_name: dict[str, FakeCollection] = {}
    created_names: list[str] = []
    deleted_names: list[str] = []

    def __init__(self, path):
        self.path = Path(path)

    def get_collection(self, name: str):
        if name not in self.collections_by_name:
            raise ValueError(name)
        return self.collections_by_name[name]

    def get_or_create_collection(self, name: str):
        self.created_names.append(name)
        collection = self.collections_by_name.get(name)
        if collection is None:
            collection = FakeCollection()
            self.collections_by_name[name] = collection
        return collection

    def delete_collection(self, name: str):
        self.deleted_names.append(name)
        self.collections_by_name.pop(name, None)

    def list_collections(self):
        return [SimpleNamespace(name=name) for name in self.collections_by_name]

    @classmethod
    def reset(cls):
        cls.collections_by_name = {}
        cls.created_names = []
        cls.deleted_names = []


class FakeChromaVectorStore:
    def __init__(self, chroma_collection):
        self.chroma_collection = chroma_collection


class FakeIndex:
    def __init__(self):
        self.docstore = SimpleNamespace(docs={})
        self.inserted = []
        self._retriever = SimpleNamespace(retrieve=lambda _question: [])

    def as_retriever(self, similarity_top_k=3):
        self.last_top_k = similarity_top_k
        return self._retriever

    def insert(self, document):
        self.inserted.append(document)


class FakeVectorStoreIndex:
    last_documents = None
    last_vector_store = None
    loaded_vector_store = None
    last_loaded_index = None

    @classmethod
    def from_documents(cls, documents, storage_context=None):
        cls.last_documents = list(documents)
        cls.last_vector_store = getattr(storage_context, 'vector_store', None)
        for document in documents:
            metadata = getattr(document, 'metadata', {}) or {}
            for value in metadata.values():
                if isinstance(value, list):
                    raise ValueError('Value for metadata tags must be one of (str, int, float, None)')
        return FakeIndex()

    @classmethod
    def from_vector_store(cls, vector_store):
        cls.loaded_vector_store = vector_store
        cls.last_loaded_index = FakeIndex()
        return cls.last_loaded_index

    @classmethod
    def reset(cls):
        cls.last_documents = None
        cls.last_vector_store = None
        cls.loaded_vector_store = None
        cls.last_loaded_index = None


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

    return {
        'llama_index': fake_root,
        'llama_index.core': fake_core,
        'llama_index.embeddings': fake_embeddings,
        'llama_index.embeddings.huggingface': fake_hf,
        'llama_index.vector_stores': fake_vector_stores,
        'llama_index.vector_stores.chroma': fake_vs_chroma,
        'chromadb': fake_chromadb,
    }


class RagServiceDeviceFallbackTests(unittest.TestCase):
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

    def test_falls_back_to_cpu_when_cuda_is_unavailable(self) -> None:
        service = RAGIndexService()
        temp_root = self._make_temp_root('test_rag_device_fallback_cpu')
        data_path = temp_root / 'output_data.json'
        data_path.write_text(json.dumps([{
            'id': 'item_1',
            'type': 'case',
            'title': '测试标题',
            'content': '测试内容',
            'source': 'test',
        }], ensure_ascii=False), encoding='utf-8')
        storage_path = temp_root / 'storage'

        fake_modules = install_fake_modules()
        with patch.dict(sys.modules, fake_modules), \
             patch('model.rag.service.resolve_device', return_value='cpu') as mock_resolve_device, \
             patch('llama_index.embeddings.huggingface.HuggingFaceEmbedding', side_effect=lambda **kwargs: SimpleNamespace(**kwargs)) as mock_embedding:
            service.build_or_load(
                data_path=data_path,
                storage_path=storage_path,
                api_key='test-key',
                api_base='https://example.com',
                model='gpt-4o-mini',
                embedding_model='BAAI/bge-small-zh-v1.5',
                embedding_device='cuda',
                chunk_size=128,
                collection_name='fraud_knowledge',
            )

        mock_resolve_device.assert_called_once_with('cuda')
        self.assertEqual(mock_embedding.call_args.kwargs['device'], 'cpu')

    def test_builds_new_index_when_collection_is_missing(self) -> None:
        service = RAGIndexService()
        temp_root = self._make_temp_root('test_rag_build_new_chroma')
        data_path = temp_root / 'output_data.json'
        data_path.write_text(json.dumps([{
            'id': 'item_1',
            'type': 'case',
            'title': '测试标题',
            'content': '测试内容',
            'source': 'test',
        }], ensure_ascii=False), encoding='utf-8')
        storage_path = temp_root / 'storage'

        fake_modules = install_fake_modules()
        with patch.dict(sys.modules, fake_modules), \
             patch('model.rag.service.resolve_device', return_value='cpu'), \
             patch('llama_index.embeddings.huggingface.HuggingFaceEmbedding', side_effect=lambda **kwargs: SimpleNamespace(**kwargs)):
            service.build_or_load(
                data_path=data_path,
                storage_path=storage_path,
                api_key='test-key',
                api_base='https://example.com',
                model='gpt-4o-mini',
                embedding_model='BAAI/bge-small-zh-v1.5',
                embedding_device='cpu',
                chunk_size=128,
                collection_name='fraud_knowledge',
            )

        self.assertEqual(FakePersistentClient.created_names, ['fraud_knowledge'])
        self.assertEqual(len(FakeVectorStoreIndex.last_documents), 1)

    def test_loads_existing_index_when_chroma_collection_has_data(self) -> None:
        service = RAGIndexService()
        temp_root = self._make_temp_root('test_rag_load_existing_chroma')
        data_path = temp_root / 'output_data.json'
        data_path.write_text('[]', encoding='utf-8')
        storage_path = temp_root / 'storage'
        chroma_path = storage_path / 'chroma_db'
        chroma_path.mkdir(parents=True, exist_ok=True)
        FakePersistentClient.collections_by_name = {'fraud_knowledge': FakeCollection(count=3)}

        fake_modules = install_fake_modules()
        with patch.dict(sys.modules, fake_modules), \
             patch('model.rag.service.resolve_device', return_value='cpu'), \
             patch('llama_index.embeddings.huggingface.HuggingFaceEmbedding', side_effect=lambda **kwargs: SimpleNamespace(**kwargs)):
            service.build_or_load(
                data_path=data_path,
                storage_path=chroma_path,
                api_key='test-key',
                api_base='https://example.com',
                model='gpt-4o-mini',
                embedding_model='BAAI/bge-small-zh-v1.5',
                embedding_device='cpu',
                chunk_size=128,
                collection_name='fraud_knowledge',
            )

        self.assertIsNotNone(FakeVectorStoreIndex.loaded_vector_store)
        self.assertIs(service._index, FakeVectorStoreIndex.last_loaded_index)

    def test_has_persisted_rag_index_checks_existing_non_empty_collection(self) -> None:
        temp_root = self._make_temp_root('test_rag_has_persisted_index')
        chroma_path = temp_root / 'chroma_db'
        chroma_path.mkdir(parents=True, exist_ok=True)
        FakePersistentClient.collections_by_name = {'fraud_knowledge': FakeCollection(count=2)}
        fake_modules = install_fake_modules()
        with patch.dict(sys.modules, fake_modules):
            self.assertTrue(has_persisted_rag_index(chroma_path, 'fraud_knowledge'))
            self.assertFalse(has_persisted_rag_index(chroma_path, 'missing'))

    def test_build_or_load_serializes_tags_metadata_for_chroma(self) -> None:
        service = RAGIndexService()
        temp_root = self._make_temp_root('test_rag_chroma_metadata_tags')
        data_path = temp_root / 'output_data.json'
        data_path.write_text(json.dumps([{
            'id': 'item_1',
            'type': 'case',
            'title': '测试标题',
            'content': '测试内容',
            'source': 'test',
            'tags': ['反诈', '案例'],
        }], ensure_ascii=False), encoding='utf-8')
        storage_path = temp_root / 'storage'

        fake_modules = install_fake_modules()
        with patch.dict(sys.modules, fake_modules), \
             patch('model.rag.service.resolve_device', return_value='cpu'), \
             patch('llama_index.embeddings.huggingface.HuggingFaceEmbedding', side_effect=lambda **kwargs: SimpleNamespace(**kwargs)):
            service.build_or_load(
                data_path=data_path,
                storage_path=storage_path,
                api_key='test-key',
                api_base='https://example.com',
                model='gpt-4o-mini',
                embedding_model='BAAI/bge-small-zh-v1.5',
                embedding_device='cpu',
                chunk_size=128,
                collection_name='fraud_knowledge',
            )

        stored_metadata = FakeVectorStoreIndex.last_documents[0].metadata
        self.assertIsInstance(stored_metadata['tags'], str)


if __name__ == '__main__':
    unittest.main()
