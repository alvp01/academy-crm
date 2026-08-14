"""Unit tests for AuthService rotation — mock repo, verify revoke -> create sequence on refresh."""
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.security import create_refresh_token, hash_token, verify_token
from app.models.academy import Academy
from app.models.refresh_token import RefreshToken
from app.services.auth import AuthService


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.fixture
def mock_academy_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_refresh_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def service(mock_db, mock_academy_repo, mock_refresh_repo):
    svc = AuthService.__new__(AuthService)
    svc.repo = mock_academy_repo
    svc.refresh_repo = mock_refresh_repo
    return svc


class TestAuthServiceRotation:
    async def test_refresh_rotates_token(self, service, mock_academy_repo, mock_refresh_repo):
        """On successful refresh: revoke old token, create new one."""
        academy_id = uuid.uuid4()
        academy = Academy(id=academy_id, name="Test", email="test@test.com")
        mock_academy_repo.get_by_id.return_value = academy

        # Create a valid refresh token
        jti = str(uuid.uuid4())
        token_data = {"sub": str(academy_id), "jti": jti}
        refresh_token = create_refresh_token(token_data)

        # Hash it the same way the service does
        token_hash = hash_token(refresh_token)

        # Mock: token row exists, not revoked, not expired, hash matches
        token_row = RefreshToken(
            jti=jti,
            academy_id=academy_id,
            token_hash=token_hash,
            revoked_at=None,
            expires_at=(datetime.now(timezone.utc) + timedelta(days=7)).replace(tzinfo=None),
        )
        mock_refresh_repo.get_by_jti_for_update.return_value = token_row

        result = await service.refresh(refresh_token)

        # Verify revoke was called for old token
        mock_refresh_repo.revoke.assert_awaited_once_with(jti, academy_id)

        # Verify new token was created
        mock_refresh_repo.create.assert_awaited_once()
        # Check that new token has new jti
        create_args = mock_refresh_repo.create.call_args
        assert "jti" in create_args.kwargs
        assert create_args.kwargs["jti"] != jti

    async def test_refresh_reuse_detection(self, service, mock_academy_repo, mock_refresh_repo):
        """Revoked token triggers reuse detection → all academy tokens revoked."""
        academy_id = uuid.uuid4()
        academy = Academy(id=academy_id, name="Test", email="test@test.com")
        mock_academy_repo.get_by_id.return_value = academy

        jti = str(uuid.uuid4())
        token_data = {"sub": str(academy_id), "jti": jti}
        refresh_token = create_refresh_token(token_data)
        token_hash = hash_token(refresh_token)

        # Mock: token row is already revoked
        token_row = RefreshToken(
            jti=jti,
            academy_id=academy_id,
            token_hash=token_hash,
            revoked_at=datetime.now(timezone.utc).replace(tzinfo=None),
            expires_at=(datetime.now(timezone.utc) + timedelta(days=7)).replace(tzinfo=None),
        )
        mock_refresh_repo.get_by_jti_for_update.return_value = token_row

        with pytest.raises(Exception) as exc_info:
            await service.refresh(refresh_token)

        # Verify all academy tokens were revoked
        mock_refresh_repo.revoke_all_for_academy.assert_awaited_once_with(academy_id)

    async def test_refresh_expired_token(self, service, mock_academy_repo, mock_refresh_repo):
        """Expired token returns 401."""
        academy_id = uuid.uuid4()
        academy = Academy(id=academy_id, name="Test", email="test@test.com")
        mock_academy_repo.get_by_id.return_value = academy

        jti = str(uuid.uuid4())
        token_data = {"sub": str(academy_id), "jti": jti}
        refresh_token = create_refresh_token(token_data)
        token_hash = hash_token(refresh_token)

        # Mock: token row exists but expired
        token_row = RefreshToken(
            jti=jti,
            academy_id=academy_id,
            token_hash=token_hash,
            revoked_at=None,
            expires_at=(datetime.now(timezone.utc) - timedelta(days=1)).replace(tzinfo=None),
        )
        mock_refresh_repo.get_by_jti_for_update.return_value = token_row

        with pytest.raises(Exception) as exc_info:
            await service.refresh(refresh_token)

        assert "expired" in str(exc_info.value).lower()

    async def test_refresh_unknown_token(self, service, mock_academy_repo, mock_refresh_repo):
        """Unknown jti returns 401."""
        academy_id = uuid.uuid4()
        academy = Academy(id=academy_id, name="Test", email="test@test.com")
        mock_academy_repo.get_by_id.return_value = academy

        jti = str(uuid.uuid4())
        token_data = {"sub": str(academy_id), "jti": jti}
        refresh_token = create_refresh_token(token_data)

        # Mock: token not found
        mock_refresh_repo.get_by_jti_for_update.return_value = None

        with pytest.raises(Exception) as exc_info:
            await service.refresh(refresh_token)

        assert "not found" in str(exc_info.value).lower()