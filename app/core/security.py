import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

ACCESS_MINUTES = 30
REFRESH_DAYS = 14


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(*, sub: str, role: str) -> str:
    now = _now_utc()
    exp = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MIN)
    payload = {
        "sub": sub,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": exp,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def create_refresh_token(*, sub: str, jti: str) -> str:
    now = _now_utc()
    exp = now + timedelta(days=REFRESH_DAYS)
    payload = {
        "sub": sub,
        "type": "refresh",
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": exp,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def new_refresh_jti() -> str:
    return str(uuid.uuid4())


def hash_jti(jti: str) -> str:
    return hashlib.sha256(jti.encode("utf-8")).hexdigest()


def refresh_expires_at() -> datetime:
    return _now_utc() + timedelta(days=REFRESH_DAYS)
