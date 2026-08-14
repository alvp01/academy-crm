import uuid

import pytest
from httpx import AsyncClient

from app.core.security import decode_token
from tests.conftest import auth_headers, get_auth_cookie, login_academy


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post("/api/auth/register", json={
        "name": "Test Academy",
        "email": "test@example.com",
        "password": "secret123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test Academy"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "name": "Dup Academy",
        "email": "dup@example.com",
        "password": "secret123",
    }
    resp1 = await client.post("/api/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/auth/register", json=payload)
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    assert "access_token" in tokens
    assert "refresh_token" in tokens


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, academy_a: dict):
    resp = await client.post("/api/auth/login", json={
        "email": academy_a["email"],
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    # Refresh reads token from cookie (client auto-sends it)
    resp = await client.post("/api/auth/refresh")
    assert resp.status_code == 200
    # New cookies should be set
    set_cookie_headers = resp.headers.get_list("set-cookie")
    cookie_names = [h.split("=")[0] for h in set_cookie_headers]
    assert "access_token" in cookie_names
    assert "refresh_token" in cookie_names


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    # No refresh_token cookie set — should return 401
    resp = await client.post("/api/auth/refresh")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_register_duplicate_name_allowed(client: AsyncClient):
    """Two academies with the same name but different emails register successfully.

    The Academy model only enforces email uniqueness, not name uniqueness.
    Duplicate names with different emails should both return 201.
    """
    name = f"Duplicate Name Academy {uuid.uuid4().hex[:8]}"
    payload1 = {
        "name": name,
        "email": f"first_{uuid.uuid4().hex[:8]}@test.com",
        "password": "secret123",
    }
    payload2 = {
        "name": name,
        "email": f"second_{uuid.uuid4().hex[:8]}@test.com",
        "password": "secret123",
    }
    resp1 = await client.post("/api/auth/register", json=payload1)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/auth/register", json=payload2)
    assert resp2.status_code == 201


@pytest.mark.asyncio
async def test_login_unknown_email(client: AsyncClient):
    """Login with an email that doesn't exist should return 401."""
    resp = await client.post("/api/auth/login", json={
        "email": f"nonexistent_{uuid.uuid4().hex[:8]}@nowhere.com",
        "password": "somepassword",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_jwt_sub_contains_academy_id(client: AsyncClient, academy_a: dict):
    """JWT access token's sub claim must contain the academy's UUID."""
    resp = await client.post("/api/auth/login", json={
        "email": academy_a["email"],
        "password": academy_a["password"],
    })
    assert resp.status_code == 200

    access_token = get_auth_cookie(resp, "access_token")
    assert access_token is not None, "access_token cookie not found"

    payload = decode_token(access_token)
    assert payload is not None, "Failed to decode access token"
    assert "sub" in payload, "Missing 'sub' claim in JWT"

    # sub must be a valid UUID matching the academy's id
    sub = payload["sub"]
    assert sub == str(academy_a["id"]), (
        f"JWT sub '{sub}' does not match academy id '{academy_a['id']}'"
    )
