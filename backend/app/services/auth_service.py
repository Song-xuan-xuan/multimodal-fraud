import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.repositories.user_repo import create_user, get_by_username

_RESET_CODE_TTL_MINUTES = 10
_reset_verification_codes: dict[str, dict[str, datetime | str]] = {}


async def register(db: AsyncSession, username: str, password: str) -> dict:
    existing = await get_by_username(db, username)
    if existing:
        raise ValueError("用户名已存在")
    hashed = hash_password(password)
    user = await create_user(db, username, hashed)
    return {"id": user.id, "username": user.username}


async def authenticate(db: AsyncSession, username: str, password: str) -> dict:
    user = await get_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("用户名或密码错误")
    access = create_access_token({"sub": user.username, "user_id": user.id})
    refresh = create_refresh_token({"sub": user.username, "user_id": user.id})
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


def create_password_reset_code(username: str) -> str:
    code = secrets.token_hex(3).upper()
    _reset_verification_codes[username] = {
        "code_hash": hashlib.sha256(code.encode("utf-8")).hexdigest(),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=_RESET_CODE_TTL_MINUTES),
    }
    return code


def validate_password_reset_code(username: str, code: str) -> None:
    stored = _reset_verification_codes.get(username)
    if not stored:
        raise ValueError("未发送验证码或验证码已过期")

    expires_at = stored["expires_at"]
    if datetime.now(timezone.utc) > expires_at:
        _reset_verification_codes.pop(username, None)
        raise ValueError("验证码已过期")

    input_hash = hashlib.sha256(code.upper().encode("utf-8")).hexdigest()
    if input_hash != stored["code_hash"]:
        raise ValueError("验证码不正确")


def clear_password_reset_code(username: str) -> None:
    _reset_verification_codes.pop(username, None)
