import os
import sys
import tempfile
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

from model.rag.service import RAGIndexService


class FakeStorageContext:
    @staticmethod
    def from_defaults(*_args, **_kwargs):
        return SimpleNamespace()


class FakeVectorStoreIndex:
    @staticmethod
    def from_documents(_documents):
        return SimpleNamespace(
            storage_context=SimpleNamespace(persist=lambda **_kwargs: None),
            docstore=SimpleNamespace(docs={}),
        )


def install_fake_llama_index_modules():
    fake_core = types.ModuleType('llama_index.core')
    fake_core.VectorStoreIndex = FakeVectorStoreIndex
    fake_core.StorageContext = FakeStorageContext
    fake_core.Document = lambda **kwargs: SimpleNamespace(**kwargs)
    fake_core.Settings = SimpleNamespace(llm=None, embed_model=None, chunk_size=None)
    fake_core.load_index_from_storage = lambda _storage_context: SimpleNamespace(docstore=SimpleNamespace(docs={}))

    fake_hf = types.ModuleType('llama_index.embeddings.huggingface')
    fake_hf.HuggingFaceEmbedding = SimpleNamespace

    fake_openai = types.ModuleType('llama_index.llms.openai')
    fake_openai.OpenAI = lambda **kwargs: SimpleNamespace(**kwargs)

    fake_embeddings = types.ModuleType('llama_index.embeddings')
    fake_embeddings.huggingface = fake_hf

    fake_llms = types.ModuleType('llama_index.llms')
    fake_llms.openai = fake_openai

    fake_root = types.ModuleType('llama_index')
    fake_root.core = fake_core
    fake_root.embeddings = fake_embeddings
    fake_root.llms = fake_llms

    return {
        'llama_index': fake_root,
        'llama_index.core': fake_core,
        'llama_index.embeddings': fake_embeddings,
        'llama_index.embeddings.huggingface': fake_hf,
        'llama_index.llms': fake_llms,
        'llama_index.llms.openai': fake_openai,
    }


class RagServiceDeviceFallbackTests(unittest.TestCase):
    def test_falls_back_to_cpu_when_cuda_is_unavailable(self) -> None:
        service = RAGIndexService()
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / 'output_data.json'
            data_path.write_text('[]', encoding='utf-8')
            storage_path = Path(temp_dir) / 'storage'

            fake_modules = install_fake_llama_index_modules()
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
                )

        mock_resolve_device.assert_called_once_with('cuda')
        self.assertEqual(mock_embedding.call_args.kwargs['device'], 'cpu')

    def test_builds_new_index_when_storage_is_non_empty_but_missing_llamaindex_files(self) -> None:
        service = RAGIndexService()
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / 'output_data.json'
            data_path.write_text('[]', encoding='utf-8')
            storage_path = Path(temp_dir) / 'storage'
            storage_path.mkdir(parents=True, exist_ok=True)
            (storage_path / 'legacy_data').mkdir(parents=True, exist_ok=True)

            fake_modules = install_fake_llama_index_modules()
            with patch.dict(sys.modules, fake_modules), \
                 patch('model.rag.service.resolve_device', return_value='cpu'), \
                 patch('llama_index.embeddings.huggingface.HuggingFaceEmbedding', side_effect=lambda **kwargs: SimpleNamespace(**kwargs)), \
                 patch('llama_index.core.load_index_from_storage') as mock_load_index_from_storage:
                service.build_or_load(
                    data_path=data_path,
                    storage_path=storage_path,
                    api_key='test-key',
                    api_base='https://example.com',
                    model='gpt-4o-mini',
                    embedding_model='BAAI/bge-small-zh-v1.5',
                    embedding_device='cuda',
                    chunk_size=128,
                )

        mock_load_index_from_storage.assert_not_called()


if __name__ == '__main__':
    unittest.main()
