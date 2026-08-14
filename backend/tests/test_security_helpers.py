"""Unit tests for hash_token / verify_token helpers and cookie/CSRF helpers."""
import hashlib
import re

import pytest
from starlette.responses import Response

from app.core.security import (
    clear_auth_cookies,
    generate_csrf_token,
    hash_token,
    set_auth_cookies,
    verify_token,
)


# Override the autouse setup_db fixture to make these tests DB-free
@pytest.fixture(autouse=True)
def _no_db_setup():
    """Skip database setup for pure unit tests."""
    yield


class TestHashToken:
    def test_deterministic_sha256(self):
        token = "test-refresh-token-abc123"
        result1 = hash_token(token)
        result2 = hash_token(token)
        assert result1 == result2
        assert len(result1) == 64  # SHA-256 hex digest length

    def test_different_tokens_produce_different_hashes(self):
        h1 = hash_token("token-a")
        h2 = hash_token("token-b")
        assert h1 != h2

    def test_empty_string(self):
        result = hash_token("")
        assert len(result) == 64

    def test_known_vector(self):
        token = "hello"
        expected = hashlib.sha256(b"hello").hexdigest()
        assert hash_token(token) == expected


class TestVerifyToken:
    def test_valid_token_matches_hash(self):
        token = "my-secret-refresh-token"
        token_hash = hash_token(token)
        assert verify_token(token, token_hash) is True

    def test_wrong_token_returns_false(self):
        token = "my-secret-refresh-token"
        wrong_token = "wrong-token"
        token_hash = hash_token(token)
        assert verify_token(wrong_token, token_hash) is False

    def test_tampered_hash_returns_false(self):
        token = "my-secret-refresh-token"
        token_hash = hash_token(token)
        tampered = token_hash[:-1] + ("0" if token_hash[-1] != "0" else "1")
        assert verify_token(token, tampered) is False

    def test_empty_token(self):
        token_hash = hash_token("")
        assert verify_token("", token_hash) is True
        assert verify_token("not-empty", token_hash) is False


class TestGenerateCsrfToken:
    def test_returns_32_char_hex(self):
        token = generate_csrf_token()
        assert len(token) == 32
        assert re.fullmatch(r"[0-9a-f]{32}", token)

    def test_returns_unique_values(self):
        t1 = generate_csrf_token()
        t2 = generate_csrf_token()
        assert t1 != t2


class TestSetAuthCookies:
    def test_sets_three_cookies(self):
        response = Response()
        set_auth_cookies(response, "access123", "refresh456", "csrf789", "development")
        set_cookie_headers = response.headers.getlist("set-cookie")
        cookie_names = [h.split("=")[0] for h in set_cookie_headers]
        assert "access_token" in cookie_names
        assert "refresh_token" in cookie_names
        assert "csrf_token" in cookie_names

    def test_dev_mode_cookies_lack_secure_flag(self):
        response = Response()
        set_auth_cookies(response, "at", "rt", "ct", "development")
        for header in response.headers.getlist("set-cookie"):
            assert "Secure" not in header

    def test_prod_mode_cookies_have_secure_flag(self):
        response = Response()
        set_auth_cookies(response, "at", "rt", "ct", "production")
        for header in response.headers.getlist("set-cookie"):
            assert "Secure" in header

    def test_access_token_attributes(self):
        response = Response()
        set_auth_cookies(response, "at", "rt", "ct", "development")
        access = [h for h in response.headers.getlist("set-cookie") if h.startswith("access_token=")][0]
        assert "HttpOnly" in access
        assert "SameSite=lax" in access
        assert "Max-Age=1800" in access

    def test_refresh_token_attributes(self):
        response = Response()
        set_auth_cookies(response, "at", "rt", "ct", "development")
        refresh = [h for h in response.headers.getlist("set-cookie") if h.startswith("refresh_token=")][0]
        assert "HttpOnly" in refresh
        assert "SameSite=strict" in refresh
        assert "Max-Age=604800" in refresh

    def test_csrf_token_not_httponly(self):
        response = Response()
        set_auth_cookies(response, "at", "rt", "ct", "development")
        csrf = [h for h in response.headers.getlist("set-cookie") if h.startswith("csrf_token=")][0]
        assert "HttpOnly" not in csrf
        assert "SameSite=lax" in csrf


class TestClearAuthCookies:
    def test_sets_max_age_zero(self):
        response = Response()
        clear_auth_cookies(response)
        for header in response.headers.getlist("set-cookie"):
            assert "Max-Age=0" in header

    def test_clears_all_three_cookies(self):
        response = Response()
        clear_auth_cookies(response)
        cookie_names = [h.split("=")[0] for h in response.headers.getlist("set-cookie")]
        assert "access_token" in cookie_names
        assert "refresh_token" in cookie_names
        assert "csrf_token" in cookie_names
