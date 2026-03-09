import asyncio
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.services.detection_service import detect_ai_text


class DetectAITextCompatibilityTests(unittest.TestCase):
    def test_zero_probability_is_jittered_like_legacy_route(self) -> None:
        fake_random = SimpleNamespace(randint=lambda *_args, **_kwargs: 5)
        with patch('model.ai_text.service.detect', return_value={
            'is_ai_generated': False,
            'confidence': 0.0,
            'details': {'method': 'Fast-DetectGPT'},
        }), patch('app.services.detection_service.random', new=fake_random, create=True):
            result = asyncio.run(detect_ai_text('legacy zero probability case'))

        self.assertAlmostEqual(result['probability'], 0.05)
        self.assertAlmostEqual(result['confidence'], 0.05)
        self.assertEqual(result['label'], '人工撰写')

    def test_full_probability_is_jittered_like_legacy_route(self) -> None:
        fake_random = SimpleNamespace(randint=lambda *_args, **_kwargs: 3)
        with patch('model.ai_text.service.detect', return_value={
            'is_ai_generated': True,
            'confidence': 1.0,
            'details': {'method': 'Fast-DetectGPT'},
        }), patch('app.services.detection_service.random', new=fake_random, create=True):
            result = asyncio.run(detect_ai_text('legacy full probability case'))

        self.assertAlmostEqual(result['probability'], 0.97)
        self.assertAlmostEqual(result['confidence'], 0.97)
        self.assertEqual(result['label'], 'AI生成')


if __name__ == '__main__':
    unittest.main()
