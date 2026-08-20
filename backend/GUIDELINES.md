# Backend Coding Guidelines

This document establishes conventions for the Python/FastAPI backend.

---

## 1. Layered Architecture

Every feature follows this flow:

```
Router → Service → Repository → Database
```

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Router** | `app/api/{entity}.py` | HTTP handling, request parsing, response formatting |
| **Service** | `app/services/{entity}.py` | Business logic, orchestration, validation |
| **Repository** | `app/repositories/{entity}.py` | Database queries, data access |
| **Model** | `app/models/{entity}.py` | SQLAlchemy ORM definition |
| **Schema** | `app/schemas/{entity}.py` | Pydantic request/response models |

### Rules

1. **Routers never contain business logic** — delegate to services
2. **Services never create DB sessions** — use `Depends(get_db)` injection
3. **Repositories never raise HTTP errors** — return `None` or raise domain exceptions
4. **Models never contain validation** — use Pydantic schemas for that

---

## 2. Tenant Isolation (CRITICAL)

Every query MUST be scoped by `academy_id`. This is the most important constraint.

### Pattern

```python
# Repository
async def get_by_id(self, entity_id: uuid.UUID, academy_id: uuid.UUID) -> Entity | None:
    result = await self.db.execute(
        select(Entity).where(
            Entity.id == entity_id,
            Entity.academy_id == academy_id,  # ALWAYS filter
        )
    )
    return result.scalar_one_or_none()
```

### Checklist for new endpoints

- [ ] Router extracts `academy_id` via `Depends(get_current_academy)`
- [ ] Service accepts `academy_id` as first parameter
- [ ] Repository filters by `academy_id` in ALL queries
- [ ] Cross-academy access returns 404 (never 403)
- [ ] Tests verify isolation (access B's resources with A's token)

---

## 3. Async/Await Patterns

### DO

```python
# Async database operations
async def get_item(self, id: uuid.UUID) -> Item | None:
    result = await self.db.execute(select(Item).where(Item.id == id))
    return result.scalar_one_or_none()

# Async HTTP calls
async def fetch_external(self, url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### DON'T

```python
# Blocking I/O - causes event loop starvation
def get_item(self, id: uuid.UUID) -> Item | None:
    result = self.db.execute(...)  # WRONG: sync call
    return result.scalar_one_or_none()

# Blocking file operations
with open("file.txt") as f:  # WRONG: blocks event loop
    data = f.read()
```

---

## 4. Database Sessions

### Pattern

```python
# ALWAYS use dependency injection
async def endpoint(
    db: AsyncSession = Depends(get_db),
    academy: Academy = Depends(get_current_academy),
):
    service = SomeService(db)
    return await service.do_something(academy.id)
```

### Rules

- Never create sessions manually: `async with session_factory() as s: ...`
- Never pass sessions between requests
- Never store sessions in class instances
- Sessions are request-scoped via FastAPI dependencies

---

## 5. Error Handling

### Pattern

```python
from fastapi import HTTPException, status

# Not found → 404
entity = await repo.get_by_id(entity_id, academy_id)
if entity is None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity_name} not found",
    )

# Validation → 422
if not valid:
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Invalid input",
    )

# Auth → 401
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
)
```

### Status Code Reference

| Code | When |
|------|------|
| 200 | Successful GET/PUT |
| 201 | Successful POST (created) |
| 204 | Successful DELETE (no content) |
| 400 | Bad request (malformed input) |
| 401 | Authentication required or failed |
| 403 | Forbidden (valid token, wrong permissions) |
| 404 | Entity not found (or cross-tenant access) |
| 409 | Conflict (duplicate name, constraint violation) |
| 422 | Validation error (Pydantic/multipart) |

---

## 6. Pydantic Schemas

### Pattern

```python
from pydantic import BaseModel, Field

class EntityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None

class EntityUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None

class EntityResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

class PaginatedEntityResponse(BaseModel):
    items: list[EntityResponse]
    total: int
    page: int
    size: int
    pages: int
```

### Rules

- Use `model_config = {"from_attributes": True}` for ORM compatibility
- Separate Create, Update, Response schemas
- Add validation via `Field()` constraints
- Response schemas match what the API returns (no internal fields)

---

## 7. Repository Pattern

### Base Template

```python
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entity import Entity


class EntityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self, entity_id: uuid.UUID, academy_id: uuid.UUID
    ) -> Entity | None:
        result = await self.db.execute(
            select(Entity).where(
                Entity.id == entity_id,
                Entity.academy_id == academy_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_paginated(
        self,
        academy_id: uuid.UUID,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Entity], int]:
        # Count
        count_query = (
            select(func.count())
            .select_from(Entity)
            .where(Entity.academy_id == academy_id)
        )
        total = (await self.db.execute(count_query)).scalar_one()

        # Items
        items_query = (
            select(Entity)
            .where(Entity.academy_id == academy_id)
            .offset((page - 1) * size)
            .limit(size)
            .order_by(Entity.created_at.desc())
        )
        items = (await self.db.execute(items_query)).scalars().all()

        return list(items), total

    async def create(self, entity: Entity) -> Entity:
        self.db.add(entity)
        await self.db.flush()
        return entity

    async def delete(self, entity: Entity) -> None:
        await self.db.delete(entity)
        await self.db.flush()
```

---

## 8. Service Pattern

### Base Template

```python
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academy import Academy
from app.models.entity import Entity
from app.repositories.entity import EntityRepository
from app.schemas.entity import EntityCreate, EntityUpdate


class EntityService:
    def __init__(self, db: AsyncSession):
        self.repo = EntityRepository(db)

    async def get_entity(
        self, entity_id: uuid.UUID, academy_id: uuid.UUID
    ) -> Entity:
        entity = await self.repo.get_by_id(entity_id, academy_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity

    async def create_entity(
        self, academy_id: uuid.UUID, data: EntityCreate
    ) -> Entity:
        entity = Entity(
            academy_id=academy_id,
            name=data.name,
            description=data.description,
        )
        return await self.repo.create(entity)

    async def update_entity(
        self,
        entity_id: uuid.UUID,
        academy_id: uuid.UUID,
        data: EntityUpdate,
    ) -> Entity:
        entity = await self.get_entity(entity_id, academy_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entity, field, value)
        await self.repo.db.flush()
        return entity

    async def delete_entity(
        self, entity_id: uuid.UUID, academy_id: uuid.UUID
    ) -> None:
        entity = await self.get_entity(entity_id, academy_id)
        await self.repo.delete(entity)
```

---

## 9. Router Pattern

### Base Template

```python
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_academy, get_db
from app.models.academy import Academy
from app.schemas.entity import (
    EntityCreate,
    EntityResponse,
    EntityUpdate,
    PaginatedEntityResponse,
)
from app.services.entity import EntityService

router = APIRouter(
    prefix="/api/entities",
    tags=["Entities"],
    responses={401: {"description": "Invalid or missing authentication token"}},
)


@router.post(
    "",
    response_model=EntityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new entity",
)
async def create_entity(
    data: EntityCreate,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    service = EntityService(db)
    return await service.create_entity(academy.id, data)


@router.get(
    "",
    response_model=PaginatedEntityResponse,
    summary="List entities",
)
async def list_entities(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    service = EntityService(db)
    return await service.list_entities(academy.id, page, size)
```

---

## 10. Testing

### Test Structure

```python
import uuid
import pytest
from httpx import AsyncClient

from app.core.deps import get_db
from app.main import app


@pytest.mark.asyncio
async def test_create_entity(client: AsyncClient, academy_a: dict):
    """Test creating an entity with valid authentication."""
    headers = auth_headers(academy_a["access_token"])
    response = await client.post(
        "/api/entities",
        json={"name": "Test Entity"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Entity"


@pytest.mark.asyncio
async def test_tenant_isolation(
    client: AsyncClient,
    academy_a: dict,
    academy_b: dict,
):
    """Verify academy B cannot access academy A's entities."""
    # Create entity as academy A
    headers_a = auth_headers(academy_a["access_token"])
    resp = await client.post(
        "/api/entities",
        json={"name": "A's Entity"},
        headers=headers_a,
    )
    entity_id = resp.json()["id"]

    # Try to access as academy B → must return 404
    headers_b = auth_headers(academy_b["access_token"])
    resp = await client.get(
        f"/api/entities/{entity_id}",
        headers=headers_b,
    )
    assert resp.status_code == 404  # NOT 403
```

### Test Helpers

```python
# From conftest.py
from tests.conftest import auth_headers, login_academy

# Use these fixtures:
# - client: AsyncClient for HTTP requests
# - academy_a: First test academy (with credentials)
# - academy_b: Second test academy (for isolation tests)

# Login and get auth headers
creds = await login_academy(client, "email@test.com", "password")
headers = auth_headers(creds["access_token"])
```

### Test Categories

| Category | What to test |
|----------|--------------|
| **CRUD** | Create, read, update, delete happy paths |
| **Validation** | Invalid input, missing fields, bad formats |
| **Auth** | Missing token, invalid token, expired token |
| **Isolation** | Cross-academy access returns 404 |
| **Edge cases** | Empty states, pagination, concurrent edits |

---

## 11. Alembic Migrations

### Creating Migrations

```bash
# Auto-generate from model changes
docker compose exec backend alembic revision --autogenerate -m "add entity table"

# Review generated migration
cat backend/alembic/versions/{hash}_add_entity_table.py

# Apply
docker compose exec backend alembic upgrade head
```

### Rules

- **Never modify existing migrations** after they're pushed
- **Always review** auto-generated migrations before committing
- **One logical change** per migration file
- **Test rollback**: `docker compose exec backend alembic downgrade -1`

---

## 12. Code Style

### Formatting

- **Line length**: 88 characters (Black default)
- **Quotes**: Double quotes for strings
- **Trailing commas**: Always on multi-line structures

### Imports

```python
# Standard library
import uuid
from datetime import datetime

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Local
from app.core.deps import get_current_academy, get_db
from app.models.entity import Entity
from app.schemas.entity import EntityCreate
```

---

*Last updated: August 2026*
