import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_academy, get_db
from app.models.academy import Academy
from app.schemas.headquarters import HQCreate, HQResponse, HQUpdate, PaginatedHQResponse
from app.services.headquarters import HeadquartersService

router = APIRouter(
    prefix="/api/headquarters",
    tags=["Headquarters"],
    responses={401: {"description": "Invalid or missing authentication token"}},
)


@router.post(
    "",
    response_model=HQResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new headquarters",
    responses={
        201: {"description": "Headquarters created"},
        401: {"description": "Not authenticated"},
    },
)
async def create_hq(
    data: HQCreate,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new headquarters for the authenticated academy.

    - **name**: Headquarters name (e.g. "Main Campus", "Downtown Branch")

    ```bash
    curl -X POST http://localhost:8001/api/headquarters \\
      -H "Authorization: Bearer <access_token>" \\
      -H "Content-Type: application/json" \\
      -d '{"name": "Main Campus"}'
    ```
    """
    service = HeadquartersService(db)
    return await service.create_hq(academy.id, data)


@router.get(
    "",
    response_model=PaginatedHQResponse,
    summary="List headquarters",
    responses={
        200: {"description": "Paginated list of headquarters"},
    },
)
async def list_hqs(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Items per page (1-100)"),
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    List all headquarters belonging to the authenticated academy.

    ```bash
    curl "http://localhost:8001/api/headquarters?page=1&size=10" \\
      -H "Authorization: Bearer <access_token>"
    ```
    """
    service = HeadquartersService(db)
    return await service.list_hqs(academy.id, page, size)


@router.get(
    "/{hq_id}",
    response_model=HQResponse,
    summary="Get headquarters by ID",
    responses={
        200: {"description": "Headquarters details"},
        404: {"description": "Headquarters not found"},
    },
)
async def get_hq(
    hq_id: uuid.UUID,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific headquarters.

    ```bash
    curl http://localhost:8001/api/headquarters/<hq_id> \\
      -H "Authorization: Bearer <access_token>"
    ```
    """
    service = HeadquartersService(db)
    return await service.get_hq(hq_id, academy.id)


@router.put(
    "/{hq_id}",
    response_model=HQResponse,
    summary="Update headquarters",
    responses={
        200: {"description": "Headquarters updated"},
        404: {"description": "Headquarters not found"},
    },
)
async def update_hq(
    hq_id: uuid.UUID,
    data: HQUpdate,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Update headquarters name.

    ```bash
    curl -X PUT http://localhost:8001/api/headquarters/<hq_id> \\
      -H "Authorization: Bearer <access_token>" \\
      -H "Content-Type: application/json" \\
      -d '{"name": "Updated Campus Name"}'
    ```
    """
    service = HeadquartersService(db)
    return await service.update_hq(hq_id, academy.id, data)


@router.delete(
    "/{hq_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete headquarters",
    responses={
        204: {"description": "Headquarters deleted"},
        404: {"description": "Headquarters not found"},
    },
)
async def delete_hq(
    hq_id: uuid.UUID,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Permanently delete a headquarters. This cannot be undone.

    ```bash
    curl -X DELETE http://localhost:8001/api/headquarters/<hq_id> \\
      -H "Authorization: Bearer <access_token>"
    ```
    """
    service = HeadquartersService(db)
    await service.delete_hq(hq_id, academy.id)
