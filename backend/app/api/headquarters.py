import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_academy, get_db
from app.models.academy import Academy
from app.schemas.headquarters import HQCreate, HQResponse, HQUpdate, PaginatedHQResponse
from app.services.headquarters import HeadquartersService

router = APIRouter(prefix="/api/headquarters", tags=["headquarters"])


@router.post("", response_model=HQResponse, status_code=201)
async def create_hq(
    data: HQCreate,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    service = HeadquartersService(db)
    return await service.create_hq(academy.id, data)


@router.get("", response_model=PaginatedHQResponse)
async def list_hqs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    service = HeadquartersService(db)
    return await service.list_hqs(academy.id, page, size)


@router.get("/{hq_id}", response_model=HQResponse)
async def get_hq(
    hq_id: uuid.UUID,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    service = HeadquartersService(db)
    return await service.get_hq(hq_id, academy.id)


@router.put("/{hq_id}", response_model=HQResponse)
async def update_hq(
    hq_id: uuid.UUID,
    data: HQUpdate,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    service = HeadquartersService(db)
    return await service.update_hq(hq_id, academy.id, data)


@router.delete("/{hq_id}", status_code=204)
async def delete_hq(
    hq_id: uuid.UUID,
    academy: Academy = Depends(get_current_academy),
    db: AsyncSession = Depends(get_db),
):
    service = HeadquartersService(db)
    await service.delete_hq(hq_id, academy.id)
