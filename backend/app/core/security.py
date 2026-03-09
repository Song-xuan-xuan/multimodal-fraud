from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BCRYPT_MAX_SECRET_BYTES = 72


def _normalize_bcrypt_secret(secret: str | bytes) -> bytes:
    """Normalize secret for bcrypt/passlib compatibility.

    bcrypt only uses first 72 bytes. bcrypt>=4 no longer truncates silently,
    so we enforce truncation before hashing/verifying.
    """
    if isinstance(secret, str):
        secret_bytes = secret.encode("utf-8")
    else:
        secret_bytes = secret
    return secret_bytes[:BCRYPT_MAX_SECRET_BYTES]


def hash_password(password: str) -> str:
    return pwd_context.hash(_normalize_bcrypt_secret(password))


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(_normalize_bcrypt_secret(plain), hashed)


def create_access_token(data: dict) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {**data, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {**data, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        settings = get_settings()
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
