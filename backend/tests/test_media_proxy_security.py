import os
import sys
import unittest

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.api.v1.media import (
    _IMAGE_PROXY_MAX_BYTES,
    _validate_image_payload,
    _validate_image_url,
    router as media_router,
)


class MediaProxyValidationTests(unittest.TestCase):
    def test_validate_image_url_accepts_allowed_host(self) -> None:
        url = _validate_image_url('https://images.unsplash.com/photo-1', {'images.unsplash.com'})
        self.assertEqual(url, 'https://images.unsplash.com/photo-1')

    def test_validate_image_url_rejects_non_http_scheme(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            _validate_image_url('file:///etc/passwd', {'images.unsplash.com'})
        self.assertEqual(ctx.exception.status_code, 400)

    def test_validate_image_url_rejects_userinfo(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            _validate_image_url('https://user:pass@images.unsplash.com/pic.jpg', {'images.unsplash.com'})
        self.assertEqual(ctx.exception.status_code, 400)

    def test_validate_image_url_rejects_localhost_and_private_ip(self) -> None:
        with self.assertRaises(HTTPException) as localhost_ctx:
            _validate_image_url('http://localhost/x.jpg', {'localhost'})
        self.assertEqual(localhost_ctx.exception.status_code, 403)

        with self.assertRaises(HTTPException) as private_ip_ctx:
            _validate_image_url('http://127.0.0.1/x.jpg', {'127.0.0.1'})
        self.assertEqual(private_ip_ctx.exception.status_code, 403)

    def test_validate_image_url_rejects_non_whitelisted_domain(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            _validate_image_url('https://evil.example.com/x.jpg', {'images.unsplash.com'})
        self.assertEqual(ctx.exception.status_code, 403)

    def test_validate_image_payload_allows_supported_types(self) -> None:
        media_type = _validate_image_payload('image/png; charset=utf-8', b'abc')
        self.assertEqual(media_type, 'image/png')

    def test_validate_image_payload_rejects_unsupported_type(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            _validate_image_payload('text/html', b'<html></html>')
        self.assertEqual(ctx.exception.status_code, 415)

    def test_validate_image_payload_rejects_oversized_body(self) -> None:
        content = b'a' * (_IMAGE_PROXY_MAX_BYTES + 1)
        with self.assertRaises(HTTPException) as ctx:
            _validate_image_payload('image/jpeg', content)
        self.assertEqual(ctx.exception.status_code, 413)


class MediaProxyEndpointFastFailTests(unittest.TestCase):
    def setUp(self) -> None:
        app = FastAPI()
        app.include_router(media_router, prefix='/api/v1/media')
        self.client = TestClient(app)

    def test_proxy_rejects_non_http_url_before_network_request(self) -> None:
        resp = self.client.get('/api/v1/media/proxy', params={'url': 'ftp://images.unsplash.com/a.jpg'})
        self.assertEqual(resp.status_code, 400)

    def test_proxy_rejects_non_whitelisted_url_before_network_request(self) -> None:
        resp = self.client.get('/api/v1/media/proxy', params={'url': 'https://not-whitelisted.example/a.jpg'})
        self.assertEqual(resp.status_code, 403)


if __name__ == '__main__':
    unittest.main()
