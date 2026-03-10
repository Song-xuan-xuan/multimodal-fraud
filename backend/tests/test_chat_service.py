import asyncio
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
for candidate in (BACKEND_DIR, PROJECT_ROOT):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from app.services.chat_service import (
    build_chat_message_payload,
    decode_assistant_content,
    encode_assistant_content,
    remove_chat,
    rename_chat,
    send_message,
)


class ChatServiceTests(unittest.TestCase):
    def test_assistant_content_round_trip_preserves_sources(self) -> None:
        sources = [
            {
                'text': '类型: case\n标题: 诈骗案例A\n正文: 这是一个案例',
                'score': 0.91,
                'metadata': {
                    'item_id': 'case_a',
                    'item_type': 'case',
                    'fraud_type': '刷单返利',
                    'source': '公安通报',
                },
            }
        ]
        encoded = encode_assistant_content('这是回答正文', sources, 'knowledge_enhanced')

        content, decoded_sources, retrieval_mode = decode_assistant_content(encoded)

        self.assertEqual(content, '这是回答正文')
        self.assertEqual(decoded_sources, sources)
        self.assertEqual(retrieval_mode, 'knowledge_enhanced')

        payload = build_chat_message_payload(SimpleNamespace(
            id=2,
            role='assistant',
            content=encoded,
            created_at='2026-03-10T10:00:00+00:00',
        ))
        self.assertEqual(payload['content'], '这是回答正文')
        self.assertEqual(payload['sources'], sources)
        self.assertEqual(payload['retrieval_mode'], 'knowledge_enhanced')

    def test_send_message_uses_recent_context_and_attaches_rag_sources(self) -> None:
        history = [
            SimpleNamespace(id=index, role='user' if index % 2 == 0 else 'assistant', content=f'历史消息{index}', created_at='')
            for index in range(12)
        ]
        history.append(SimpleNamespace(id=100, role='user', content='用户当前问题', created_at=''))

        captured_assistant_content: list[str] = []

        async def fake_add_message(_db, _chat_id, role, content):
            if role == 'assistant':
                captured_assistant_content.append(content)
                return SimpleNamespace(id=102, role=role, content=content, created_at='')
            return SimpleNamespace(id=101, role=role, content=content, created_at='')

        rag_sources = [
            {
                'text': '类型: case\n标题: 骗局样本\n诈骗类型: 冒充客服\n正文: 退款前要求共享屏幕',
                'score': 0.88,
                'metadata': {
                    'item_id': 'case_1',
                    'item_type': 'case',
                    'fraud_type': '冒充客服',
                    'source': '知识库案例',
                },
            }
        ]
        llm_mock = AsyncMock(return_value='请勿共享屏幕，并通过官方渠道核验。')

        with patch('app.services.chat_service.get_chat', AsyncMock(return_value=SimpleNamespace(id='chat-1', user_id=1))), \
             patch('app.services.chat_service.add_message', side_effect=fake_add_message), \
             patch('app.services.chat_service.get_messages', AsyncMock(return_value=history)), \
             patch('app.services.chat_service.retrieve_relevant_sources', return_value=rag_sources), \
             patch('app.services.chat_service._call_llm', llm_mock):
            user_msg, assistant_msg = asyncio.run(send_message(None, 'chat-1', 1, '用户当前问题'))

        self.assertEqual(user_msg.role, 'user')
        self.assertEqual(assistant_msg.role, 'assistant')
        self.assertEqual(len(captured_assistant_content), 1)
        self.assertIn('[[RAG_SOURCES_JSON]]', captured_assistant_content[0])

        llm_messages = llm_mock.await_args.args[0]
        llm_text = '\n'.join(message['content'] for message in llm_messages)
        self.assertIn('骗局样本', llm_text)
        self.assertNotIn('历史消息0', llm_text)
        self.assertIn('历史消息11', llm_text)

        assistant_payload = build_chat_message_payload(assistant_msg)
        self.assertEqual(assistant_payload['sources'], rag_sources)
        self.assertEqual(assistant_payload['retrieval_mode'], 'knowledge_enhanced')

    def test_send_message_falls_back_to_plain_llm_when_rag_fails(self) -> None:
        history = [SimpleNamespace(id=1, role='user', content='帮我判断这个链接是否可疑', created_at='')]

        async def fake_add_message(_db, _chat_id, role, content):
            return SimpleNamespace(id=1 if role == 'user' else 2, role=role, content=content, created_at='')

        llm_mock = AsyncMock(return_value='仅根据你提供的信息，建议先不要点击链接。')

        with patch('app.services.chat_service.get_chat', AsyncMock(return_value=SimpleNamespace(id='chat-1', user_id=1))), \
             patch('app.services.chat_service.add_message', side_effect=fake_add_message), \
             patch('app.services.chat_service.get_messages', AsyncMock(return_value=history)), \
             patch('app.services.chat_service.retrieve_relevant_sources', side_effect=RuntimeError('rag down')), \
             patch('app.services.chat_service._call_llm', llm_mock):
            _user_msg, assistant_msg = asyncio.run(send_message(None, 'chat-1', 1, '帮我判断这个链接是否可疑'))

        assistant_payload = build_chat_message_payload(assistant_msg)
        self.assertEqual(assistant_payload['sources'], [])
        self.assertEqual(assistant_payload['retrieval_mode'], 'retrieval_failed')
        llm_mock.assert_awaited_once()

    def test_send_message_marks_empty_retrieval_without_sources(self) -> None:
        history = [SimpleNamespace(id=1, role='user', content='请帮我分析一个新型骗局', created_at='')]

        async def fake_add_message(_db, _chat_id, role, content):
            return SimpleNamespace(id=1 if role == 'user' else 2, role=role, content=content, created_at='')

        llm_mock = AsyncMock(return_value='目前没有直接命中的资料，我先根据常见诈骗套路给你建议。')

        with patch('app.services.chat_service.get_chat', AsyncMock(return_value=SimpleNamespace(id='chat-1', user_id=1))), \
             patch('app.services.chat_service.add_message', side_effect=fake_add_message), \
             patch('app.services.chat_service.get_messages', AsyncMock(return_value=history)), \
             patch('app.services.chat_service.retrieve_relevant_sources', return_value=[]), \
             patch('app.services.chat_service._call_llm', llm_mock):
            _user_msg, assistant_msg = asyncio.run(send_message(None, 'chat-1', 1, '请帮我分析一个新型骗局'))

        assistant_payload = build_chat_message_payload(assistant_msg)
        self.assertEqual(assistant_payload['sources'], [])
        self.assertEqual(assistant_payload['retrieval_mode'], 'retrieval_empty')

    def test_decode_assistant_content_defaults_to_llm_only_without_marker(self) -> None:
        content, decoded_sources, retrieval_mode = decode_assistant_content('普通助手回复')

        self.assertEqual(content, '普通助手回复')
        self.assertEqual(decoded_sources, [])
        self.assertEqual(retrieval_mode, 'llm_only')

    def test_send_message_retries_with_context_when_current_question_has_no_sources(self) -> None:
        history = [
            SimpleNamespace(id=1, role='user', content='最近总有人冒充客服让我退款', created_at=''),
            SimpleNamespace(id=2, role='assistant', content='你先不要转账，也不要共享屏幕。', created_at=''),
            SimpleNamespace(id=3, role='user', content='我想了解一下电子诈骗的最近骗局，帮我理解一下', created_at=''),
        ]

        async def fake_add_message(_db, _chat_id, role, content):
            return SimpleNamespace(id=1 if role == 'user' else 2, role=role, content=content, created_at='')

        rag_sources = [
            {
                'text': '类型: case\n标题: 电子诈骗近期骗局\n正文: 冒充客服退款、虚假投资和共享屏幕诱导仍然高发',
                'score': 0.79,
                'metadata': {
                    'item_id': 'case_recent',
                    'item_type': 'case',
                    'fraud_type': '电子诈骗',
                    'source': '近期汇总',
                },
            }
        ]
        llm_mock = AsyncMock(return_value='近期高发的仍然是冒充客服退款、共享屏幕和虚假投资骗局。')

        with patch('app.services.chat_service.get_chat', AsyncMock(return_value=SimpleNamespace(id='chat-1', user_id=1))), \
             patch('app.services.chat_service.add_message', side_effect=fake_add_message), \
             patch('app.services.chat_service.get_messages', AsyncMock(return_value=history)), \
             patch('app.services.chat_service.retrieve_relevant_sources', side_effect=[[], rag_sources]) as retrieve_mock, \
             patch('app.services.chat_service._call_llm', llm_mock):
            _user_msg, assistant_msg = asyncio.run(send_message(None, 'chat-1', 1, '我想了解一下电子诈骗的最近骗局，帮我理解一下'))

        self.assertEqual(retrieve_mock.call_count, 2)
        first_query = retrieve_mock.call_args_list[0].args[0]
        second_query = retrieve_mock.call_args_list[1].args[0]
        self.assertEqual(first_query, '我想了解一下电子诈骗的最近骗局，帮我理解一下')
        self.assertIn('最近总有人冒充客服让我退款', second_query)

        assistant_payload = build_chat_message_payload(assistant_msg)
        self.assertEqual(assistant_payload['sources'], rag_sources)
        self.assertEqual(assistant_payload['retrieval_mode'], 'knowledge_enhanced')

    def test_rename_chat_updates_title_for_owner(self) -> None:
        renamed_chat = SimpleNamespace(
            id='chat-1',
            user_id=1,
            title='新的标题',
            created_at='',
            updated_at='',
            is_shared=False,
        )

        with patch('app.services.chat_service.get_chat', AsyncMock(return_value=SimpleNamespace(id='chat-1', user_id=1))), \
             patch('app.services.chat_service.repo_rename_chat', AsyncMock(return_value=renamed_chat)) as rename_repo:
            result = asyncio.run(rename_chat(None, 'chat-1', 1, '   新的标题   '))

        rename_repo.assert_awaited_once_with(None, 'chat-1', '新的标题')
        self.assertEqual(result.title, '新的标题')

    def test_rename_chat_rejects_blank_title(self) -> None:
        with patch('app.services.chat_service.get_chat', AsyncMock(return_value=SimpleNamespace(id='chat-1', user_id=1))):
            with self.assertRaisesRegex(ValueError, '对话标题不能为空'):
                asyncio.run(rename_chat(None, 'chat-1', 1, '   '))

    def test_remove_chat_requires_owner(self) -> None:
        with patch('app.services.chat_service.get_chat', AsyncMock(return_value=SimpleNamespace(id='chat-1', user_id=2))):
            with self.assertRaisesRegex(ValueError, '对话不存在或无权访问'):
                asyncio.run(remove_chat(None, 'chat-1', 1))


if __name__ == '__main__':
    unittest.main()
