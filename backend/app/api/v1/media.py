import ipaddress
import os
from urllib.parse import urljoin, urlparse

import httpx
from fastapi import APIRouter, HTTPException, Query, Response

router = APIRouter()

_IMAGE_PROXY_TIMEOUT_SECONDS = 8.0
_IMAGE_PROXY_MAX_BYTES = 5 * 1024 * 1024
_IMAGE_PROXY_ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/avif",
}
_DEFAULT_ALLOWED_HOSTS = {
    "images.unsplash.com",
    "pbs.twimg.com",
    "i.imgur.com",
    "imgur.com",
    "mmbiz.qpic.cn",
    "wx.qlogo.cn",
}


def _allowed_hosts() -> set[str]:
    configured = os.getenv("MEDIA_PROXY_ALLOWED_HOSTS", "")
    if not configured.strip():
        return _DEFAULT_ALLOWED_HOSTS
    return {host.strip().lower().strip(".") for host in configured.split(",") if host.strip()}


def _is_private_or_local_ip(hostname: str) -> bool:
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return False
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _validate_image_url(candidate: str, allowed_hosts: set[str]) -> str:
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="仅支持 http/https 图片地址")

    if parsed.username or parsed.password:
        raise HTTPException(status_code=400, detail="图片地址不支持用户信息")

    hostname = (parsed.hostname or "").lower().strip(".")
    if not hostname:
        raise HTTPException(status_code=400, detail="图片地址缺少域名")

    if hostname == "localhost" or _is_private_or_local_ip(hostname):
        raise HTTPException(status_code=403, detail="不允许访问该地址")

    is_allowed = hostname in allowed_hosts or any(hostname.endswith(f".{domain}") for domain in allowed_hosts)
    if not is_allowed:
        raise HTTPException(status_code=403, detail="图片域名不在白名单中")

    return candidate


def _validate_image_payload(content_type: str, content: bytes) -> str:
    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type not in _IMAGE_PROXY_ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="仅允许代理常见图片类型")

    if len(content) > _IMAGE_PROXY_MAX_BYTES:
        raise HTTPException(status_code=413, detail="图片体积超过限制")

    return media_type


@router.get("/proxy")
async def proxy_image(url: str = Query(..., max_length=2048)):
    allowed_hosts = _allowed_hosts()
    request_url = _validate_image_url(url, allowed_hosts)

    try:
        async with httpx.AsyncClient(timeout=_IMAGE_PROXY_TIMEOUT_SECONDS, follow_redirects=False) as client:
            response = await client.get(request_url, headers={"Accept": "image/*"})

            if 300 <= response.status_code < 400:
                redirect = response.headers.get("location")
                if not redirect:
                    raise HTTPException(status_code=502, detail="上游返回了无效重定向")
                redirected_url = _validate_image_url(urljoin(request_url, redirect), allowed_hosts)
                response = await client.get(redirected_url, headers={"Accept": "image/*"})

        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="图片源站访问失败")

        content_type = response.headers.get("content-type", "")
        media_type = _validate_image_payload(content_type, response.content)
        return Response(
            content=response.content,
            media_type=media_type,
            headers={"Cache-Control": "public, max-age=300"},
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="图片代理请求超时")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="图片代理请求失败")
