"""Tests for cookie-first token extraction and CSRF validation in deps.py."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.deps import get_current_academy, validate_csrf


# Override the autouse setup_db fixture to make these tests DB-free
@pytest.fixture(autouse=True)
def _no_db_setup():
    """Skip database setup for pure unit tests."""
    yield


def _make_request(
    method: str = "GET",
    cookies: dict | None = None,
    headers: dict | None = None,
) -> Request:
    """Build a mock Starlette Request with proper scope headers."""
    raw_headers = []
    for k, v in (headers or {}).items():
        raw_headers.append((k.lower().encode(), v.encode()))
    scope = {
        "type": "http",
        "method": method,
        "path": "/test",
        "query_string": b"",
        "headers": raw_headers,
    }
    request = Request(scope)
    request._cookies = cookies or {}
    return request


# --- Token extraction tests ---


class TestGetTokenFromCookie:
    @pytest.mark.asyncio
    async def test_extracts_token_from_cookie(self):
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test"
        request = _make_request(cookies={"access_token": token})

        mock_academy = MagicMock()
        mock_academy.id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_academy
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("app.core.deps.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": str(mock_academy.id), "type": "access"}
            result = await get_current_academy(request=request, db=mock_db)
            assert result == mock_academy
            mock_decode.assert_called_once_with(token)


class TestFallbackToBearerHeader:
    @pytest.mark.asyncio
    async def test_falls_back_to_bearer_header(self):
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test"
        request = _make_request(
            cookies={},
            headers={"Authorization": f"Bearer {token}"},
        )

        mock_academy = MagicMock()
        mock_academy.id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_academy
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=mock_result)

        with patch("app.core.deps.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": str(mock_academy.id), "type": "access"}
            result = await get_current_academy(request=request, db=mock_db)
            assert result == mock_academy
            mock_decode.assert_called_once_with(token)


class TestNoTokenReturns401:
    @pytest.mark.asyncio
    async def test_raises_401_when_no_token(self):
        from fastapi import HTTPException

        request = _make_request(cookies={}, headers={})
        mock_db = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_current_academy(request=request, db=mock_db)
        assert exc_info.value.status_code == 401


# --- CSRF validation tests ---


class TestCsrfValidation:
    def test_valid_csrf_accepted(self):
        request = _make_request(
            method="POST",
            cookies={"csrf_token": "abc123"},
            headers={"X-CSRF-Token": "abc123"},
        )
        # Should not raise
        result = validate_csrf(request)
        assert result is None

    def test_mismatched_csrf_rejected(self):
        from fastapi import HTTPException

        request = _make_request(
            method="POST",
            cookies={"csrf_token": "abc123"},
            headers={"X-CSRF-Token": "wrongvalue"},
        )
        with pytest.raises(HTTPException) as exc_info:
            validate_csrf(request)
        assert exc_info.value.status_code == 403

    def test_missing_csrf_header_rejected(self):
        from fastapi import HTTPException

        request = _make_request(
            method="POST",
            cookies={"csrf_token": "abc123"},
            headers={},
        )
        with pytest.raises(HTTPException) as exc_info:
            validate_csrf(request)
        assert exc_info.value.status_code == 403

    def test_get_bypasses_csrf(self):
        request = _make_request(method="GET", cookies={}, headers={})
        result = validate_csrf(request)
        assert result is None

    def test_head_bypasses_csrf(self):
        request = _make_request(method="HEAD", cookies={}, headers={})
        result = validate_csrf(request)
        assert result is None

    def test_options_bypasses_csrf(self):
        request = _make_request(method="OPTIONS", cookies={}, headers={})
        result = validate_csrf(request)
        assert result is None
