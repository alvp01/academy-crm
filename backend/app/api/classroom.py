import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_academy, get_db
from app.models.academy import Academy
from app.schemas.classroom import ClassroomCreate, ClassroomResponse, ClassroomUpdate, PaginatedClassroomResponse
from app.services.classroom import ClassroomService

router = APIRouter(prefix="/api/classrooms", tags=["classrooms"])


@router.post("", response_model=ClassroomResponse, status_code=201)
async def create_classroom(
    data: ClassroomCreate,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    service = ClassroomService(db)
    return await service.create_classroom(academy.id, data)


@router.get("", response_model=PaginatedClassroomResponse)
async def list_classrooms(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    service = ClassroomService(db)
    return await service.list_classrooms(academy.id, page, size)


@router.get("/{room_id}", response_model=ClassroomResponse)
async def get_classroom(
    room_id: uuid.UUID,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    service = ClassroomService(db)
    return await service.get_classroom(room_id, academy.id)


@router.put("/{room_id}", response_model=ClassroomResponse)
async def update_classroom(
    room_id: uuid.UUID,
    data: ClassroomUpdate,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    service = ClassroomService(db)
    return await service.update_classroom(room_id, academy.id, data)


@router.delete("/{room_id}", status_code=204)
async def delete_classroom(
    room_id: uuid.UUID,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    service = ClassroomService(db)
    await service.delete_classroom(room_id, academy.id)
