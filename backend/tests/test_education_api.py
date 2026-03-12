import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import app.api.v1.education as education_api
from app.api.v1.education import router as education_router


class EducationApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = FastAPI()
        self.app.include_router(education_router, prefix="/api/v1/education")
        self.app.dependency_overrides[education_api.get_current_user] = lambda: SimpleNamespace(username="alice")
        self.client = TestClient(self.app)

    def test_questions_endpoint_returns_requested_count(self) -> None:
        with patch.object(
            education_api,
            "get_question_batch",
            AsyncMock(
                return_value=[
                    {
                        "question_id": "q_1",
                        "question": "测试题",
                        "options": ["A", "B", "C", "D"],
                        "category": "测试",
                        "difficulty": "beginner",
                        "fraud_type": "通用诈骗",
                        "source_type": "generated",
                    }
                ]
            ),
        ):
            resp = self.client.get("/api/v1/education/questions?count=1&stage_id=advanced&refresh=true")

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["source_type"], "generated")

    def test_submit_test_uses_question_ids_and_answers(self) -> None:
        with patch.object(
            education_api,
            "submit_test_answers",
            AsyncMock(
                return_value={
                "total": 1,
                "correct": 1,
                "score": 100.0,
                "passed": True,
                "risk_profile": "low",
                "weaknesses": [],
                "recommended_stage": "advanced",
                "next_actions": ["继续综合训练"],
                "summary": "表现稳定",
                "recent_trend": [
                    {"timestamp": "2026-03-11T11:00:00", "score": 80.0, "passed": True},
                    {"timestamp": "2026-03-11T11:10:00", "score": 100.0, "passed": True},
                ],
                "trend_delta": 20.0,
                "learning_objective": "强化核验动作",
                "knowledge_gaps": ["虚假客服退款（正确率 50%）"],
                "micro_lessons": ["退款必须走官方渠道"],
                "common_mistakes": ["在紧急话术下直接操作"],
                "coach_feedback": "先核验再操作",
                "next_plan": ["每天复盘1次"],
                "details": [
                    {
                        "question_id": "q_1",
                        "question": "测试题",
                        "options": ["A", "B", "C", "D"],
                        "selected": 1,
                        "correct_answer": 1,
                        "is_correct": True,
                        "explanation": "解析",
                        "category": "测试",
                        "difficulty": "beginner",
                        "fraud_type": "通用诈骗",
                        "source_type": "generated",
                    }
                ],
            }
            ),
        ) as submit_mock:
            resp = self.client.post(
                "/api/v1/education/submit-test",
                json={"question_ids": ["q_1"], "answers": {"q_1": 1}},
            )

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["passed"])
        self.assertEqual(resp.json()["risk_profile"], "low")
        self.assertIn("recommended_stage", resp.json())
        self.assertIn("next_actions", resp.json())
        self.assertIn("recent_trend", resp.json())
        self.assertEqual(resp.json()["trend_delta"], 20.0)
        self.assertIn("learning_objective", resp.json())
        self.assertIn("coach_feedback", resp.json())
        submit_mock.assert_called_once_with(["q_1"], {"q_1": 1}, username="alice")

    def test_coach_endpoint_returns_reply(self) -> None:
        with patch.object(
            education_api,
            "coach_reply",
            AsyncMock(return_value={"reply": "复盘错题后再练3题", "actions": ["先核验来源", "记录触发词"]}),
        ) as coach_mock:
            resp = self.client.post(
                "/api/v1/education/coach",
                json={"question": "我该怎么提升？", "stage_id": "intermediate", "score": 70, "wrong_topics": ["兼职刷单"]},
            )

        self.assertEqual(resp.status_code, 200)
        self.assertIn("reply", resp.json())
        self.assertIn("actions", resp.json())
        coach_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
