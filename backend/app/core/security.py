import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.responses import Response

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_EXPIRY_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def hash_token(token: str) -> str:
    """Hash a refresh token using SHA-256 hex digest."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token(token: str, token_hash: str) -> bool:
    """Verify a refresh token against its SHA-256 hash."""
    return hash_token(token) == token_hash


def generate_csrf_token() -> str:
    """Generate a cryptographically random 32-char hex CSRF token."""
    return secrets.token_hex(16)


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    csrf_token: str,
    environment: str,
) -> None:
    """Set httponly auth cookies on the response."""
    secure = environment == "production"

    response.set_cookie(
        "access_token", access_token,
        max_age=1800, httponly=True, samesite="lax", secure=secure, path="/",
    )
    response.set_cookie(
        "refresh_token", refresh_token,
        max_age=604800, httponly=True, samesite="strict", secure=secure, path="/",
    )
    response.set_cookie(
        "csrf_token", csrf_token,
        max_age=604800, httponly=False, samesite="lax", secure=secure, path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    """Clear all auth cookies by setting Max-Age=0."""
    for name in ("access_token", "refresh_token", "csrf_token"):
        response.set_cookie(name, "", max_age=0, path="/")
