"""Unit tests for AuthService rotation — mock repo, verify revoke -> create sequence on refresh."""
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.security import create_refresh_token, hash_token
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

        # Mock: token row exists, not revoked, not expired
        token_row = RefreshToken(
            jti=jti,
            academy_id=academy_id,
            revoked_at=None,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        mock_refresh_repo.get_by_jti.return_value = token_row

        result = await service.refresh(refresh_token)

        # Verify revoke was called for old token
        mock_refresh_repo.revoke.assert_awaited_once_with(jti, academy_id)

        # Verify new token was created
        mock_refresh_repo.create.assert_awaited_once()
        create_call = mock_refresh_repo.create.call_args
        assert create_call.kwargs["academy_id"] == academy_id

        # Verify new tokens are returned
        assert result.access_token is not None
        assert result.refresh_token is not None

    async def test_refresh_reuse_detection(self, service, mock_academy_repo, mock_refresh_repo):
        """Revoked token triggers reuse detection → all academy tokens revoked."""
        academy_id = uuid.uuid4()
        academy = Academy(id=academy_id, name="Test", email="test@test.com")
        mock_academy_repo.get_by_id.return_value = academy

        jti = str(uuid.uuid4())
        token_data = {"sub": str(academy_id), "jti": jti}
        refresh_token = create_refresh_token(token_data)

        # Mock: token row is revoked
        token_row = RefreshToken(
            jti=jti,
            academy_id=academy_id,
            revoked_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        mock_refresh_repo.get_by_jti.return_value = token_row

        with pytest.raises(Exception) as exc_info:
            await service.refresh(refresh_token)

        # Verify all academy tokens were revoked
        mock_refresh_repo.revoke_all_for_academy.assert_awaited_once_with(academy_id)

        # Verify new token was NOT created
        mock_refresh_repo.create.assert_not_awaited()

    async def test_refresh_expired_token(self, service, mock_academy_repo, mock_refresh_repo):
        """Expired token is rejected."""
        academy_id = uuid.uuid4()

        jti = str(uuid.uuid4())
        token_data = {"sub": str(academy_id), "jti": jti}
        refresh_token = create_refresh_token(token_data)

        # Mock: token row exists but expired
        token_row = RefreshToken(
            jti=jti,
            academy_id=academy_id,
            revoked_at=None,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
        mock_refresh_repo.get_by_jti.return_value = token_row

        with pytest.raises(Exception):
            await service.refresh(refresh_token)

        mock_refresh_repo.revoke.assert_not_awaited()
        mock_refresh_repo.create.assert_not_awaited()

    async def test_refresh_unknown_token(self, service, mock_academy_repo, mock_refresh_repo):
        """Token not found in DB is rejected."""
        academy_id = uuid.uuid4()

        jti = str(uuid.uuid4())
        token_data = {"sub": str(academy_id), "jti": jti}
        refresh_token = create_refresh_token(token_data)

        mock_refresh_repo.get_by_jti.return_value = None

        with pytest.raises(Exception):
            await service.refresh(refresh_token)

        mock_refresh_repo.revoke.assert_not_awaited()
        mock_refresh_repo.create.assert_not_awaited()
