import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, login_academy


@pytest.mark.asyncio
async def test_create_hq_success(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    resp = await client.post(
        "/api/headquarters",
        json={"name": "Main HQ"},
        headers=auth_headers(tokens["access_token"]),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Main HQ"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_hqs_scoped(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    headers = auth_headers(tokens["access_token"])

    # Create 2 HQs
    await client.post("/api/headquarters", json={"name": "HQ 1"}, headers=headers)
    await client.post("/api/headquarters", json={"name": "HQ 2"}, headers=headers)

    resp = await client.get("/api/headquarters", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_hq_by_id(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    headers = auth_headers(tokens["access_token"])

    create_resp = await client.post("/api/headquarters", json={"name": "Get HQ"}, headers=headers)
    hq_id = create_resp.json()["id"]

    resp = await client.get(f"/api/headquarters/{hq_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Get HQ"


@pytest.mark.asyncio
async def test_update_hq(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    headers = auth_headers(tokens["access_token"])

    create_resp = await client.post("/api/headquarters", json={"name": "Old Name"}, headers=headers)
    hq_id = create_resp.json()["id"]

    resp = await client.put(f"/api/headquarters/{hq_id}", json={"name": "New Name"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_hq(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    headers = auth_headers(tokens["access_token"])

    create_resp = await client.post("/api/headquarters", json={"name": "Delete HQ"}, headers=headers)
    hq_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/headquarters/{hq_id}", headers=headers)
    assert resp.status_code == 204

    # Confirm deleted
    resp = await client.get(f"/api/headquarters/{hq_id}", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_hq_name_409(client: AsyncClient, academy_a: dict):
    tokens = await login_academy(client, academy_a["email"], academy_a["password"])
    headers = auth_headers(tokens["access_token"])

    await client.post("/api/headquarters", json={"name": "Unique HQ"}, headers=headers)
    resp = await client.post("/api/headquarters", json={"name": "Unique HQ"}, headers=headers)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_cross_academy_get_hq_404(client: AsyncClient, academy_a: dict, academy_b: dict):
    tokens_a = await login_academy(client, academy_a["email"], academy_a["password"])
    tokens_b = await login_academy(client, academy_b["email"], academy_b["password"])

    create_resp = await client.post(
        "/api/headquarters",
        json={"name": "Secret HQ"},
        headers=auth_headers(tokens_a["access_token"]),
    )
    hq_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/headquarters/{hq_id}",
        headers=auth_headers(tokens_b["access_token"]),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cross_academy_update_hq_404(client: AsyncClient, academy_a: dict, academy_b: dict):
    tokens_a = await login_academy(client, academy_a["email"], academy_a["password"])
    tokens_b = await login_academy(client, academy_b["email"], academy_b["password"])

    create_resp = await client.post(
        "/api/headquarters",
        json={"name": "Protected HQ"},
        headers=auth_headers(tokens_a["access_token"]),
    )
    hq_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/headquarters/{hq_id}",
        json={"name": "Hacked HQ"},
        headers=auth_headers(tokens_b["access_token"]),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cross_academy_delete_hq_404(client: AsyncClient, academy_a: dict, academy_b: dict):
    tokens_a = await login_academy(client, academy_a["email"], academy_a["password"])
    tokens_b = await login_academy(client, academy_b["email"], academy_b["password"])

    create_resp = await client.post(
        "/api/headquarters",
        json={"name": "Safe HQ"},
        headers=auth_headers(tokens_a["access_token"]),
    )
    hq_id = create_resp.json()["id"]

    resp = await client.delete(
        f"/api/headquarters/{hq_id}",
        headers=auth_headers(tokens_b["access_token"]),
    )
    assert resp.status_code == 404

    # Academy A confirms still exists
    resp = await client.get(
        f"/api/headquarters/{hq_id}",
        headers=auth_headers(tokens_a["access_token"]),
    )
    assert resp.status_code == 200
