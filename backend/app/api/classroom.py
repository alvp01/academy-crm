import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_academy, get_db
from app.models.academy import Academy
from app.schemas.classroom import ClassroomCreate, ClassroomResponse, ClassroomUpdate, PaginatedClassroomResponse
from app.services.classroom import ClassroomService

router = APIRouter(
    prefix="/api/classrooms",
    tags=["Classrooms"],
    responses={401: {"description": "Invalid or missing authentication token"}},
)


@router.post(
    "",
    response_model=ClassroomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new classroom",
    responses={
        201: {"description": "Classroom created"},
        401: {"description": "Not authenticated"},
        404: {"description": "Headquarters not found"},
    },
)
async def create_classroom(
    data: ClassroomCreate,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new classroom inside an existing headquarters.

    - **headquarters_id**: UUID of the parent headquarters
    - **name**: Classroom name (e.g. "Room A", "Lab 1")
    - **classes_capacity**: Maximum number of students (must be > 0)

    ```bash
    curl -X POST http://localhost:8001/api/classrooms \\
      -H "Authorization: Bearer <access_token>" \\
      -H "Content-Type: application/json" \\
      -d '{"headquarters_id": "<hq_uuid>", "name": "Room A", "classes_capacity": 30}'
    ```
    """
    service = ClassroomService(db)
    return await service.create_classroom(academy.id, data)


@router.get(
    "",
    response_model=PaginatedClassroomResponse,
    summary="List classrooms",
    responses={
        200: {"description": "Paginated list of classrooms"},
    },
)
async def list_classrooms(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Items per page (1-100)"),
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    List all classrooms across all headquarters of the authenticated academy.

    ```bash
    curl "http://localhost:8001/api/classrooms?page=1&size=10" \\
      -H "Authorization: Bearer <access_token>"
    ```
    """
    service = ClassroomService(db)
    return await service.list_classrooms(academy.id, page, size)


@router.get(
    "/{room_id}",
    response_model=ClassroomResponse,
    summary="Get classroom by ID",
    responses={
        200: {"description": "Classroom details"},
        404: {"description": "Classroom not found"},
    },
)
async def get_classroom(
    room_id: uuid.UUID,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific classroom.

    ```bash
    curl http://localhost:8001/api/classrooms/<room_id> \\
      -H "Authorization: Bearer <access_token>"
    ```
    """
    service = ClassroomService(db)
    return await service.get_classroom(room_id, academy.id)


@router.put(
    "/{room_id}",
    response_model=ClassroomResponse,
    summary="Update classroom",
    responses={
        200: {"description": "Classroom updated"},
        404: {"description": "Classroom not found"},
    },
)
async def update_classroom(
    room_id: uuid.UUID,
    data: ClassroomUpdate,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a classroom's name and/or capacity. Only provided fields are updated.

    ```bash
    curl -X PUT http://localhost:8001/api/classrooms/<room_id> \\
      -H "Authorization: Bearer <access_token>" \\
      -H "Content-Type: application/json" \\
      -d '{"name": "Lab 1", "classes_capacity": 25}'
    ```
    """
    service = ClassroomService(db)
    return await service.update_classroom(room_id, academy.id, data)


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete classroom",
    responses={
        204: {"description": "Classroom deleted"},
        404: {"description": "Classroom not found"},
    },
)
async def delete_classroom(
    room_id: uuid.UUID,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    """
    Permanently delete a classroom. This cannot be undone.

    ```bash
    curl -X DELETE http://localhost:8001/api/classrooms/<room_id> \\
      -H "Authorization: Bearer <access_token>"
    ```
    """
    service = ClassroomService(db)
    await service.delete_classroom(room_id, academy.id)
