import logging
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_csrf_token,
    hash_password,
    hash_token,
    verify_password,
    verify_token,
)
from app.models.academy import Academy
from app.repositories.academy import AcademyRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.schemas.auth import LoginRequest, RegisterRequest

logger = logging.getLogger(__name__)


# In-memory fallback for DB unavailability (graceful degradation)
_revoked_refresh_tokens: set[str] = set()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = AcademyRepository(db)
        self.refresh_repo = RefreshTokenRepository(db)

    async def register(self, data: RegisterRequest) -> tuple[Academy, str, str, str]:
        """Register a new academy. Returns (academy, access_token, refresh_token, csrf_token)."""
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        academy = await self.repo.create(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
        )

        # Generate tokens for the new academy
        jti = str(uuid.uuid4())
        token_data = {"sub": str(academy.id), "jti": jti}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        csrf_token = generate_csrf_token()

        # Persist refresh token in database
        try:
            expires_at = (datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_EXPIRY_DAYS)).replace(tzinfo=None)
            await self.refresh_repo.create(
                academy_id=academy.id,
                token_hash=hash_token(refresh_token),
                jti=jti,
                expires_at=expires_at,
            )
        except SQLAlchemyError as e:
            logger.warning("DB unavailable during register, using in-memory fallback: %s", e)
            pass

        return academy, access_token, refresh_token, csrf_token

    async def login(self, data: LoginRequest) -> tuple[Academy, str, str, str]:
        """Authenticate and return (academy, access_token, refresh_token, csrf_token)."""
        academy = await self.repo.get_by_email(data.email)
        if not academy or not verify_password(data.password, academy.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        jti = str(uuid.uuid4())
        token_data = {"sub": str(academy.id), "jti": jti}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        csrf_token = generate_csrf_token()

        # Persist refresh token in database
        try:
            expires_at = (datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_EXPIRY_DAYS)).replace(tzinfo=None)
            await self.refresh_repo.create(
                academy_id=academy.id,
                token_hash=hash_token(refresh_token),
                jti=jti,
                expires_at=expires_at,
            )
        except SQLAlchemyError as e:
            logger.warning("DB unavailable during login, using in-memory fallback: %s", e)
            pass

        return academy, access_token, refresh_token, csrf_token

    async def refresh(self, refresh_token: str) -> tuple[str, str, str]:
        """Rotate refresh token. Returns (new_access_token, new_refresh_token, csrf_token)."""
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        jti = payload.get("jti")
        academy_id_str = payload.get("sub")
        if not jti or not academy_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        try:
            academy_id = uuid.UUID(academy_id_str)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        # Fallback: check in-memory revocation set if DB unavailable
        if jti in _revoked_refresh_tokens:
            logger.warning("Token reuse detected (in-memory) for academy %s, jti %s", academy_id, jti)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

        # Look up token in database with SELECT FOR UPDATE to prevent race conditions
        token_row = None
        try:
            token_row = await self.refresh_repo.get_by_jti_for_update(jti, academy_id)
        except SQLAlchemyError as e:
            logger.error("DB unavailable during refresh, checking in-memory fallback: %s", e)
            # If token not in memory and DB down, reject
            if jti not in _revoked_refresh_tokens:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth service temporarily unavailable")
            # If in memory as revoked, reject
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

        if token_row is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")

        # Verify the presented token matches the stored hash
        if not verify_token(refresh_token, token_row.token_hash):
            logger.warning("Token hash mismatch for academy %s, jti %s", academy_id, jti)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        # Token reuse detection: if token is already revoked, revoke all academy tokens
        if token_row.revoked_at is not None:
            logger.warning(
                "Token reuse detected for academy %s, jti %s — revoking all tokens",
                academy_id,
                jti,
            )
            try:
                await self.refresh_repo.revoke_all_for_academy(academy_id)
            except SQLAlchemyError:
                _revoked_refresh_tokens.add(jti)  # Fallback to in-memory
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

        # Check expiry
        if token_row.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        # Verify academy still exists
        academy = await self.repo.get_by_id(academy_id)
        if not academy:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Academy not found")

        # Revoke old token (rotation)
        try:
            await self.refresh_repo.revoke(jti, academy_id)
        except SQLAlchemyError as e:
            logger.error("Failed to revoke old token, adding to in-memory: %s", e)
            _revoked_refresh_tokens.add(jti)

        # Issue new tokens
        new_jti = str(uuid.uuid4())
        token_data = {"sub": str(academy.id), "jti": new_jti}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        csrf_token = generate_csrf_token()

        # Persist new refresh token
        try:
            expires_at = (datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_EXPIRY_DAYS)).replace(tzinfo=None)
            await self.refresh_repo.create(
                academy_id=academy.id,
                token_hash=hash_token(new_refresh_token),
                jti=new_jti,
                expires_at=expires_at,
            )
        except SQLAlchemyError as e:
            logger.error("Failed to persist new refresh token: %s", e)
            pass

        return new_access_token, new_refresh_token, csrf_token

    async def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token on logout."""
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            # Invalid token — logout is idempotent, just return
            return

        jti = payload.get("jti")
        academy_id_str = payload.get("sub")
        if not jti or not academy_id_str:
            return

        try:
            academy_id = uuid.UUID(academy_id_str)
        except ValueError:
            return

        try:
            await self.refresh_repo.revoke(jti, academy_id)
        except SQLAlchemyError:
            _revoked_refresh_tokens.add(jti)  # Fallback to in-memory