"""Tests for cookie-based auth flows.

Covers: login sets cookies, login response has no token fields,
refresh rotates cookies, logout clears cookies, /me returns user from cookie.
"""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_sets_three_cookies(client: AsyncClient, academy_a: dict):
    """Login sets access_token, refresh_token, and csrf_token cookies."""
    resp = await client.post("/api/auth/login", json={
        "email": academy_a["email"],
        "password": academy_a["password"],
    })
    assert resp.status_code == 200
    set_cookie_headers = resp.headers.get_list("set-cookie")
    cookie_names = [h.split("=")[0] for h in set_cookie_headers]
    assert "access_token" in cookie_names
    assert "refresh_token" in cookie_names
    assert "csrf_token" in cookie_names


@pytest.mark.asyncio
async def test_login_response_has_no_token_fields(client: AsyncClient, academy_a: dict):
    """Login response body contains only user data, not tokens."""
    resp = await client.post("/api/auth/login", json={
        "email": academy_a["email"],
        "password": academy_a["password"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" not in data
    assert "refresh_token" not in data
    assert "id" in data
    assert "email" in data


@pytest.mark.asyncio
async def test_refresh_rotates_cookies(client: AsyncClient, academy_a: dict):
    """Refresh reads token from cookie and returns new Set-Cookie headers."""
    # Login to get cookies
    login_resp = await client.post("/api/auth/login", json={
        "email": academy_a["email"],
        "password": academy_a["password"],
    })
    assert login_resp.status_code == 200

    # Extract refresh token from Set-Cookie
    set_cookie_headers = login_resp.headers.get_list("set-cookie")
    refresh_token = None
    for header in set_cookie_headers:
        if header.startswith("refresh_token="):
            refresh_token = header.split(";")[0].split("=", 1)[1]
            break
    assert refresh_token is not None, "refresh_token cookie not found"

    # Refresh with cookie — client auto-sends it
    refresh_resp = await client.post("/api/auth/refresh")
    assert refresh_resp.status_code == 200
    new_set_cookie = refresh_resp.headers.get_list("set-cookie")
    new_cookie_names = [h.split("=")[0] for h in new_set_cookie]
    assert "access_token" in new_cookie_names
    assert "refresh_token" in new_cookie_names
    assert "csrf_token" in new_cookie_names


@pytest.mark.asyncio
async def test_logout_clears_three_cookies(client: AsyncClient, academy_a: dict):
    """Logout sets Max-Age=0 on all three auth cookies."""
    # Login first
    login_resp = await client.post("/api/auth/login", json={
        "email": academy_a["email"],
        "password": academy_a["password"],
    })
    assert login_resp.status_code == 200

    # Logout — client sends refresh_token cookie automatically
    logout_resp = await client.post("/api/auth/logout")
    assert logout_resp.status_code == 204

    set_cookie_headers = logout_resp.headers.get_list("set-cookie")
    cookie_names = [h.split("=")[0] for h in set_cookie_headers]
    assert "access_token" in cookie_names
    assert "refresh_token" in cookie_names
    assert "csrf_token" in cookie_names
    # Verify Max-Age=0 (clearing)
    for header in set_cookie_headers:
        if header.split("=")[0] in ("access_token", "refresh_token", "csrf_token"):
            assert "Max-Age=0" in header or "max-age=0" in header


@pytest.mark.asyncio
async def test_me_returns_user_from_cookie(client: AsyncClient, academy_a: dict):
    """/me returns current user data from access token cookie."""
    # Login to get cookies
    login_resp = await client.post("/api/auth/login", json={
        "email": academy_a["email"],
        "password": academy_a["password"],
    })
    assert login_resp.status_code == 200

    # Call /me — client sends access_token cookie automatically
    me_resp = await client.post("/api/auth/me")
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["email"] == academy_a["email"]
    assert data["name"] == academy_a["name"]
    assert "id" in data


@pytest.mark.asyncio
async def test_me_401_without_cookie(client: AsyncClient):
    """/me returns 401 when no access token cookie is present."""
    resp = await client.post("/api/auth/me")
    assert resp.status_code == 401
