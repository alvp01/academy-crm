import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, login_academy


@pytest.mark.asyncio
async def test_cross_academy_headquarter_denied(client: AsyncClient, academy_a: dict, academy_b: dict):
    """Academy A creates HQ, Academy B cannot see it."""
    tokens_a = await login_academy(client, academy_a["email"], academy_a["password"])
    tokens_b = await login_academy(client, academy_b["email"], academy_b["password"])

    # Academy A creates a headquarters
    resp = await client.post(
        "/api/headquarters",
        json={"name": "HQ Alpha"},
        headers=auth_headers(tokens_a["access_token"]),
    )
    assert resp.status_code == 201
    hq_id = resp.json()["id"]

    # Academy B tries to read Academy A's headquarters → 404
    resp = await client.get(
        f"/api/headquarters/{hq_id}",
        headers=auth_headers(tokens_b["access_token"]),
    )
    assert resp.status_code == 404

    # Academy A confirms resource still exists
    resp = await client.get(
        f"/api/headquarters/{hq_id}",
        headers=auth_headers(tokens_a["access_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "HQ Alpha"


@pytest.mark.asyncio
async def test_cross_academy_classroom_denied(client: AsyncClient, academy_a: dict, academy_b: dict):
    """Academy A creates Classroom, Academy B cannot see it."""
    tokens_a = await login_academy(client, academy_a["email"], academy_a["password"])
    tokens_b = await login_academy(client, academy_b["email"], academy_b["password"])

    # Academy A creates a headquarters
    resp = await client.post(
        "/api/headquarters",
        json={"name": "HQ For Classroom"},
        headers=auth_headers(tokens_a["access_token"]),
    )
    assert resp.status_code == 201
    hq_id = resp.json()["id"]

    # Academy A creates a classroom under that HQ
    resp = await client.post(
        "/api/classrooms",
        json={"headquarters_id": hq_id, "name": "Room 101", "classes_capacity": 30},
        headers=auth_headers(tokens_a["access_token"]),
    )
    assert resp.status_code == 201
    room_id = resp.json()["id"]

    # Academy B tries to read → 404
    resp = await client.get(
        f"/api/classrooms/{room_id}",
        headers=auth_headers(tokens_b["access_token"]),
    )
    assert resp.status_code == 404

    # Academy A confirms still exists
    resp = await client.get(
        f"/api/classrooms/{room_id}",
        headers=auth_headers(tokens_a["access_token"]),
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_unauthenticated_access_denied(client: AsyncClient):
    """Requests without token → 401/403."""
    resp = await client.get("/api/headquarters")
    assert resp.status_code in (401, 403)

    resp = await client.get("/api/classrooms")
    assert resp.status_code in (401, 403)
