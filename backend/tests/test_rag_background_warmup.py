import os
import sys
import unittest
from unittest.mock import patch

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
for candidate in (BACKEND_DIR, PROJECT_ROOT):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from app.services import rag_service


class RagBackgroundWarmupTests(unittest.TestCase):
    def test_get_rag_init_state_reports_warming_up(self) -> None:
        with patch.object(rag_service, '_initialized', False),              patch.object(rag_service, '_initializing', True),              patch.object(rag_service, '_init_error', None):
            self.assertEqual(rag_service.get_rag_init_state(), 'warming_up')

    def test_get_rag_init_state_reports_ready(self) -> None:
        with patch.object(rag_service, '_initialized', True),              patch.object(rag_service, '_initializing', False),              patch.object(rag_service, '_init_error', None):
            self.assertEqual(rag_service.get_rag_init_state(), 'ready')


if __name__ == '__main__':
    unittest.main()
