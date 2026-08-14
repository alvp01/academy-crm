"""Integration tests: full auth lifecycle via TestClient + real DB.

Covers: register → login → access protected endpoint → refresh → logout → reject revoked token.

Requires: running PostgreSQL (docker compose up db).
Run: pytest backend/tests/test_auth_integration.py -x --tb=short
"""

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, login_academy


@pytest.mark.asyncio
async def test_full_auth_flow_register_login_refresh_logout(client: AsyncClient):
    """End-to-end: register, login, use access token, refresh, logout, verify revoked."""

    # --- 1. Register ---
    creds = {
        "name": "Integration Academy",
        "email": f"integ_{uuid.uuid4().hex[:8]}@test.com",
        "password": "integ_pass_123",
    }
    reg_resp = await client.post("/api/auth/register", json=creds)
    assert reg_resp.status_code == 201, f"Register failed: {reg_resp.text}"
    academy_id = reg_resp.json()["id"]

    # --- 2. Login → access + refresh tokens ---
    tokens = await login_academy(client, creds["email"], creds["password"])
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # --- 3. Use access token on protected endpoint ---
    hq_resp = await client.get(
        "/api/headquarters",
        headers=auth_headers(access_token),
    )
    assert hq_resp.status_code == 200, f"Protected endpoint rejected valid token: {hq_resp.text}"
    # Empty list is fine — we just need to confirm auth passed
    assert hq_resp.json()["items"] == []

    # --- 4. Refresh → new tokens, old refresh token revoked ---
    refresh_resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 200, f"Refresh failed: {refresh_resp.text}"
    new_tokens = refresh_resp.json()
    new_refresh_token = new_tokens["refresh_token"]
    new_access_token = new_tokens["access_token"]
    assert new_refresh_token != refresh_token, "Refresh should issue a new token"

    # --- 5. Logout → revoke the current refresh token ---
    logout_resp = await client.post(
        "/api/auth/logout",
        json={"refresh_token": new_refresh_token},
    )
    assert logout_resp.status_code == 204, f"Logout failed: {logout_resp.text}"

    # --- 6. Verify revoked refresh token is rejected ---
    revoked_resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": new_refresh_token},
    )
    assert revoked_resp.status_code == 401, (
        f"Revoked token should be rejected, got {revoked_resp.status_code}"
    )

    # --- 7. Also verify the original (pre-rotation) refresh token is rejected ---
    revoked_orig_resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert revoked_orig_resp.status_code == 401, (
        f"Original rotated token should be rejected, got {revoked_orig_resp.status_code}"
    )


@pytest.mark.asyncio
async def test_logout_is_idempotent(client: AsyncClient):
    """Calling logout twice with the same token should not fail."""
    creds = {
        "name": "Idempotent Academy",
        "email": f"idemp_{uuid.uuid4().hex[:8]}@test.com",
        "password": "idemp_pass_123",
    }
    await client.post("/api/auth/register", json=creds)
    tokens = await login_academy(client, creds["email"], creds["password"])
    refresh_token = tokens["refresh_token"]

    # First logout
    resp1 = await client.post("/api/auth/logout", json={"refresh_token": refresh_token})
    assert resp1.status_code == 204

    # Second logout — idempotent, still 204
    resp2 = await client.post("/api/auth/logout", json={"refresh_token": refresh_token})
    assert resp2.status_code == 204


@pytest.mark.asyncio
async def test_logout_with_invalid_token_is_idempotent(client: AsyncClient):
    """Logout with a garbage token should return 204 (idempotent, no-op)."""
    resp = await client.post(
        "/api/auth/logout",
        json={"refresh_token": "totally.invalid.token"},
    )
    assert resp.status_code == 204
