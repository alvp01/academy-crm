"""Unit tests for hash_token / verify_token helpers."""
import hashlib
import pytest

from app.core.security import hash_token, verify_token


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
