"""Unit tests for RefreshTokenRepository — mock AsyncSession, verify SQL calls."""
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.refresh_token import RefreshToken
from app.repositories.refresh_token import RefreshTokenRepository


# Override the autouse setup_db fixture to make these tests DB-free
@pytest.fixture(autouse=True)
def _no_db_setup():
    """Skip database setup for pure unit tests."""
    yield


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture
def repo(mock_db):
    return RefreshTokenRepository(mock_db)


class TestRefreshTokenRepositoryCreate:
    async def test_create_calls_add_and_commit(self, repo, mock_db):
        academy_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=7)

        await repo.create(
            academy_id=academy_id,
            token_hash="abc123hash",
            jti="jti-001",
            expires_at=expires,
            user_agent="Mozilla/5.0",
            ip_address="10.0.0.1",
        )

        mock_db.add.assert_called_once()
        added_obj = mock_db.add.call_args[0][0]
        assert isinstance(added_obj, RefreshToken)
        assert added_obj.academy_id == academy_id
        assert added_obj.token_hash == "abc123hash"
        assert added_obj.jti == "jti-001"
        assert added_obj.expires_at == expires
        assert added_obj.user_agent == "Mozilla/5.0"
        assert added_obj.ip_address == "10.0.0.1"
        mock_db.commit.assert_awaited_once()
        mock_db.refresh.assert_awaited_once()

    async def test_create_optional_fields_none(self, repo, mock_db):
        academy_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=7)

        await repo.create(
            academy_id=academy_id,
            token_hash="hash",
            jti="jti-002",
            expires_at=expires,
        )

        added_obj = mock_db.add.call_args[0][0]
        assert added_obj.user_agent is None
        assert added_obj.ip_address is None


class TestRefreshTokenRepositoryGetByJti:
    async def test_get_by_jti_executes_select(self, repo, mock_db):
        jti = "jti-001"
        academy_id = uuid.uuid4()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = RefreshToken(jti=jti, academy_id=academy_id)
        mock_db.execute.return_value = mock_result

        result = await repo.get_by_jti(jti, academy_id)

        assert result is not None
        assert result.jti == jti
        mock_db.execute.assert_awaited_once()

    async def test_get_by_jti_returns_none_when_not_found(self, repo, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await repo.get_by_jti("unknown-jti", uuid.uuid4())

        assert result is None


class TestRefreshTokenRepositoryRevoke:
    async def test_revoke_sets_revoked_at(self, repo, mock_db):
        jti = "jti-001"
        academy_id = uuid.uuid4()

        await repo.revoke(jti, academy_id)

        mock_db.execute.assert_awaited_once()
        mock_db.commit.assert_awaited_once()


class TestRefreshTokenRepositoryRevokeAll:
    async def test_revoke_all_for_academy(self, repo, mock_db):
        academy_id = uuid.uuid4()

        await repo.revoke_all_for_academy(academy_id)

        mock_db.execute.assert_awaited_once()
        mock_db.commit.assert_awaited_once()


class TestRefreshTokenRepositoryCleanupExpired:
    async def test_cleanup_expired_deletes_tokens(self, repo, mock_db):
        expired_token = RefreshToken(id=uuid.uuid4(), jti="expired-1")
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [expired_token]
        mock_db.execute.return_value = mock_result

        count = await repo.cleanup_expired()

        assert count == 1
        mock_db.delete.assert_awaited_once_with(expired_token)
        mock_db.commit.assert_awaited_once()

    async def test_cleanup_expired_no_tokens(self, repo, mock_db):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        count = await repo.cleanup_expired()

        assert count == 0
        mock_db.delete.assert_not_awaited()
        mock_db.commit.assert_awaited_once()
