import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, login_academy


async def _create_hq(client: AsyncClient, token: str, name: str) -> str:
    resp = await client.post(
        "/api/headquarters",
        json={"name": name},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_classroom_success(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    hq_id = await _create_hq(client, tokens["access_token"], "HQ for Room")

    resp = await client.post(
        "/api/classrooms",
        json={"headquarters_id": hq_id, "name": "Room A", "classes_capacity": 25},
        headers=auth_headers(tokens["access_token"]),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Room A"
    assert data["classes_capacity"] == 25


@pytest.mark.asyncio
async def test_list_classrooms_scoped(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    hq_id = await _create_hq(client, tokens["access_token"], "HQ List")
    headers = auth_headers(tokens["access_token"])

    await client.post("/api/classrooms", json={"headquarters_id": hq_id, "name": "R1", "classes_capacity": 10}, headers=headers)
    await client.post("/api/classrooms", json={"headquarters_id": hq_id, "name": "R2", "classes_capacity": 20}, headers=headers)

    resp = await client.get("/api/classrooms", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


@pytest.mark.asyncio
async def test_get_classroom_by_id(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    hq_id = await _create_hq(client, tokens["access_token"], "HQ Get")
    headers = auth_headers(tokens["access_token"])

    create_resp = await client.post(
        "/api/classrooms",
        json={"headquarters_id": hq_id, "name": "Room Get", "classes_capacity": 15},
        headers=headers,
    )
    room_id = create_resp.json()["id"]

    resp = await client.get(f"/api/classrooms/{room_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Room Get"


@pytest.mark.asyncio
async def test_update_classroom(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    hq_id = await _create_hq(client, tokens["access_token"], "HQ Update")
    headers = auth_headers(tokens["access_token"])

    create_resp = await client.post(
        "/api/classrooms",
        json={"headquarters_id": hq_id, "name": "Old Room", "classes_capacity": 10},
        headers=headers,
    )
    room_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/classrooms/{room_id}",
        json={"name": "New Room", "classes_capacity": 30},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Room"
    assert resp.json()["classes_capacity"] == 30


@pytest.mark.asyncio
async def test_delete_classroom(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    hq_id = await _create_hq(client, tokens["access_token"], "HQ Delete")
    headers = auth_headers(tokens["access_token"])

    create_resp = await client.post(
        "/api/classrooms",
        json={"headquarters_id": hq_id, "name": "Room Del", "classes_capacity": 10},
        headers=headers,
    )
    room_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/classrooms/{room_id}", headers=headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_duplicate_classroom_name_409(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    hq_id = await _create_hq(client, tokens["access_token"], "HQ Dup")
    headers = auth_headers(tokens["access_token"])

    await client.post(
        "/api/classrooms",
        json={"headquarters_id": hq_id, "name": "Unique Room", "classes_capacity": 10},
        headers=headers,
    )
    resp = await client.post(
        "/api/classrooms",
        json={"headquarters_id": hq_id, "name": "Unique Room", "classes_capacity": 20},
        headers=headers,
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_capacity_validation_error(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    hq_id = await _create_hq(client, tokens["access_token"], "HQ Valid")
    headers = auth_headers(tokens["access_token"])

    resp = await client.post(
        "/api/classrooms",
        json={"headquarters_id": hq_id, "name": "Bad Room", "classes_capacity": -5},
        headers=headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_cross_academy_get_classroom_404(client: AsyncClient, academy_a: dict, academy_b: dict):
    tokens_a = await login_academy(client, academy_a["email"], academy_a["password"])
    tokens_b = await login_academy(client, academy_b["email"], academy_b["password"])

    hq_id = await _create_hq(client, tokens_a["access_token"], "Secret HQ")
    create_resp = await client.post(
        "/api/classrooms",
        json={"headquarters_id": hq_id, "name": "Secret Room", "classes_capacity": 10},
        headers=auth_headers(tokens_a["access_token"]),
    )
    room_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/classrooms/{room_id}",
        headers=auth_headers(tokens_b["access_token"]),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cross_academy_update_classroom_404(client: AsyncClient, academy_a: dict, academy_b: dict):
    tokens_a = await login_academy(client, academy_a["email"], academy_a["password"])
    tokens_b = await login_academy(client, academy_b["email"], academy_b["password"])

    hq_id = await _create_hq(client, tokens_a["access_token"], "Protected HQ")
    create_resp = await client.post(
        "/api/classrooms",
        json={"headquarters_id": hq_id, "name": "Protected Room", "classes_capacity": 10},
        headers=auth_headers(tokens_a["access_token"]),
    )
    room_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/classrooms/{room_id}",
        json={"name": "Hacked Room"},
        headers=auth_headers(tokens_b["access_token"]),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cross_academy_delete_classroom_404(client: AsyncClient, academy_a: dict, academy_b: dict):
    tokens_a = await login_academy(client, academy_a["email"], academy_a["password"])
    tokens_b = await login_academy(client, academy_b["email"], academy_b["password"])

    hq_id = await _create_hq(client, tokens_a["access_token"], "Safe HQ")
    create_resp = await client.post(
        "/api/classrooms",
        json={"headquarters_id": hq_id, "name": "Safe Room", "classes_capacity": 10},
        headers=auth_headers(tokens_a["access_token"]),
    )
    room_id = create_resp.json()["id"]

    resp = await client.delete(
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
