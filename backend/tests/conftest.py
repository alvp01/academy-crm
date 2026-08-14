import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.core.deps import get_db
from app.core.security import hash_password
from app.main import app

# Use a separate test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@academy-crm-db:5432/academy_crm_test"

engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_pre_ping=True)
async_test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_test_session() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def academy_a(client: AsyncClient) -> dict:
    """Register academy A and return response + credentials."""
    creds = {
        "name": "Academy A",
        "email": f"academy_a_{uuid.uuid4().hex[:8]}@test.com",
        "password": "testpass123",
    }
    resp = await client.post("/api/auth/register", json=creds)
    assert resp.status_code == 201
    return {**creds, **resp.json()}


@pytest_asyncio.fixture
async def academy_b(client: AsyncClient) -> dict:
    """Register academy B and return response + credentials."""
    creds = {
        "name": "Academy B",
        "email": f"academy_b_{uuid.uuid4().hex[:8]}@test.com",
        "password": "testpass456",
    }
    resp = await client.post("/api/auth/register", json=creds)
    assert resp.status_code == 201
    return {**creds, **resp.json()}


async def login_academy(client: AsyncClient, email: str, password: str) -> dict:
    """Login and return token response."""
    resp = await client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()


def auth_headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}
