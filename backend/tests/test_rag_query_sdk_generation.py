import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
for candidate in (BACKEND_DIR, PROJECT_ROOT):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from model.rag.service import RAGIndexService


class RagQuerySdkGenerationTests(unittest.TestCase):
    def test_query_uses_retriever_and_openai_sdk_instead_of_query_engine(self) -> None:
        service = RAGIndexService()
        service._index = MagicMock()
        service._api_key = 'test-key'
        service._api_base = 'https://example.com/v1'
        service._model = 'gpt-5.4'
        service._temperature = 0.2

        fake_node = SimpleNamespace(
            node=SimpleNamespace(text='第一条检索内容', metadata={'news_id': 'n1'}),
            score=0.87,
        )
        fake_retriever = MagicMock()
        fake_retriever.retrieve.return_value = [fake_node]
        service._index.as_retriever.return_value = fake_retriever
        service._index.as_query_engine.side_effect = AssertionError('query_engine should not be used')

        fake_completion = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='基于检索内容生成的回答'))]
        )
        fake_create = MagicMock(return_value=fake_completion)
        fake_client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=fake_create)
            )
        )

        with patch('model.rag.service.OpenAI', return_value=fake_client) as mock_openai:
            result = service.query('测试问题', similarity_top_k=2)

        service._index.as_retriever.assert_called_once_with(similarity_top_k=2)
        fake_retriever.retrieve.assert_called_once_with('测试问题')
        mock_openai.assert_called_once_with(api_key='test-key', base_url='https://example.com/v1')
        fake_create.assert_called_once()
        kwargs = fake_create.call_args.kwargs
        self.assertEqual(kwargs['model'], 'gpt-5.4')
        self.assertEqual(kwargs['temperature'], 0.2)
        self.assertEqual(kwargs['messages'][0]['role'], 'system')
        self.assertIn('测试问题', kwargs['messages'][1]['content'])
        self.assertIn('第一条检索内容', kwargs['messages'][1]['content'])
        self.assertEqual(result['answer'], '基于检索内容生成的回答')
        self.assertEqual(result['sources'], [
            {
                'text': '第一条检索内容',
                'score': 0.87,
                'metadata': {'news_id': 'n1'},
            }
        ])

    def test_query_uses_full_retrieved_text_for_generation_context(self) -> None:
        service = RAGIndexService()
        service._index = MagicMock()
        service._api_key = 'test-key'
        service._api_base = 'https://example.com/v1'
        service._model = 'gpt-5.4'
        service._temperature = 0.2

        long_text = 'A' * 520 + '关键结尾信息'
        fake_node = SimpleNamespace(
            node=SimpleNamespace(text=long_text, metadata={'news_id': 'n2'}),
            score=0.66,
        )
        fake_retriever = MagicMock()
        fake_retriever.retrieve.return_value = [fake_node]
        service._index.as_retriever.return_value = fake_retriever
        service._index.as_query_engine.side_effect = AssertionError('query_engine should not be used')

        fake_completion = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='回答'))]
        )
        fake_create = MagicMock(return_value=fake_completion)
        fake_client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=fake_create)
            )
        )

        with patch('model.rag.service.OpenAI', return_value=fake_client):
            result = service.query('测试长文本问题', similarity_top_k=1)

        kwargs = fake_create.call_args.kwargs
        self.assertIn('关键结尾信息', kwargs['messages'][1]['content'])
        self.assertEqual(result['sources'][0]['text'], long_text[:500])


if __name__ == '__main__':
    unittest.main()
