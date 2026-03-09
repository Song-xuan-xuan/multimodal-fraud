import os
import sys
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.api.v1.router import api_router


class FavoritesApiRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        app = FastAPI()
        app.include_router(api_router)
        self.client = TestClient(app)

    def test_api_router_does_not_expose_server_side_favorites_endpoints(self) -> None:
        paths = {route.path for route in api_router.routes}

        self.assertNotIn('/api/v1/favorites', paths)
        self.assertNotIn('/api/v1/favorites/{news_id}', paths)
        self.assertTrue(any(path.startswith('/api/v1/feedback') for path in paths))

    def test_requesting_favorites_endpoint_returns_404(self) -> None:
        resp = self.client.get('/api/v1/favorites')

        self.assertEqual(resp.status_code, 404)

    def test_news_detail_contract_has_no_favorite_fields(self) -> None:
        resp = self.client.get('/api/v1/news/non-existent-id/detail')

        self.assertEqual(resp.status_code, 404)
        if isinstance(resp.json(), dict):
            self.assertNotIn('favorited', resp.json())
            self.assertNotIn('favorite_count', resp.json())


if __name__ == '__main__':
    unittest.main()
