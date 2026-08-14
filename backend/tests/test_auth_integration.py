"""Integration tests: full auth lifecycle via TestClient + real DB.

Covers: register → login → access protected endpoint → refresh → logout → reject revoked token.

Requires: running PostgreSQL (docker compose up db).
Run: pytest backend/tests/test_auth_integration.py -x --tb=short
"""

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, get_auth_cookie, login_academy


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

    # --- 2. Login → cookies set ---
    login_resp = await client.post("/api/auth/login", json={
        "email": creds["email"],
        "password": creds["password"],
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    access_token = get_auth_cookie(login_resp, "access_token")
    refresh_token = get_auth_cookie(login_resp, "refresh_token")
    assert access_token is not None
    assert refresh_token is not None

    # --- 3. Use access token on protected endpoint (Bearer fallback) ---
    hq_resp = await client.get(
        "/api/headquarters",
        headers=auth_headers(access_token),
    )
    assert hq_resp.status_code == 200, f"Protected endpoint rejected valid token: {hq_resp.text}"
    assert hq_resp.json()["items"] == []

    # --- 4. Refresh → new cookies (client sends refresh_token cookie automatically) ---
    refresh_resp = await client.post("/api/auth/refresh")
    assert refresh_resp.status_code == 200, f"Refresh failed: {refresh_resp.text}"
    new_refresh_token = get_auth_cookie(refresh_resp, "refresh_token")
    new_access_token = get_auth_cookie(refresh_resp, "access_token")
    assert new_refresh_token is not None
    assert new_access_token is not None
    assert new_refresh_token != refresh_token, "Refresh should issue a new token"

    # --- 5. Logout → clear cookies (client sends new refresh_token cookie automatically) ---
    logout_resp = await client.post("/api/auth/logout")
    assert logout_resp.status_code == 204, f"Logout failed: {logout_resp.text}"

    # --- 6. Verify revoked refresh token is rejected ---
    # After logout, cookies are cleared. Try refresh without cookie.
    revoked_resp = await client.post("/api/auth/refresh")
    assert revoked_resp.status_code == 401, (
        f"Revoked token should be rejected, got {revoked_resp.status_code}"
    )


@pytest.mark.asyncio
async def test_logout_is_idempotent(client: AsyncClient):
    """Calling logout twice should not fail."""
    creds = {
        "name": "Idempotent Academy",
        "email": f"idemp_{uuid.uuid4().hex[:8]}@test.com",
        "password": "idemp_pass_123",
    }
    await client.post("/api/auth/register", json=creds)
    login_resp = await client.post("/api/auth/login", json={
        "email": creds["email"],
        "password": creds["password"],
    })
    assert login_resp.status_code == 200

    # First logout
    resp1 = await client.post("/api/auth/logout")
    assert resp1.status_code == 204

    # Second logout — idempotent, still 204
    resp2 = await client.post("/api/auth/logout")
    assert resp2.status_code == 204


@pytest.mark.asyncio
async def test_logout_with_invalid_token_is_idempotent(client: AsyncClient):
    """Logout without a refresh token cookie should return 204 (idempotent, no-op)."""
    resp = await client.post("/api/auth/logout")
    assert resp.status_code == 204
