import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.headquarters import HeadquartersRepository
from app.schemas.headquarters import HQCreate, HQUpdate


class HeadquartersService:
    def __init__(self, db: AsyncSession):
        self.repo = HeadquartersRepository(db)

    async def create_hq(self, academy_id: uuid.UUID, data: HQCreate):
        # Check name uniqueness per academy
        existing_hqs, _ = await self.repo.list(academy_id, page=1, size=1000)
        if any(h.name == data.name for h in existing_hqs):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Headquarters name already exists for this academy")
        return await self.repo.create(academy_id, data.name)

    async def get_hq(self, hq_id: uuid.UUID, academy_id: uuid.UUID):
        hq = await self.repo.get_by_id(hq_id, academy_id)
        if not hq:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Headquarters not found")
        return hq

    async def list_hqs(self, academy_id: uuid.UUID, page: int = 1, size: int = 20):
        items, total = await self.repo.list(academy_id, page, size)
        return {"items": items, "total": total, "page": page, "size": size}

    async def update_hq(self, hq_id: uuid.UUID, academy_id: uuid.UUID, data: HQUpdate):
        # Check name uniqueness per academy (excluding current)
        existing_hqs, _ = await self.repo.list(academy_id, page=1, size=1000)
        if any(h.name == data.name and h.id != hq_id for h in existing_hqs):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Headquarters name already exists for this academy")
        hq = await self.repo.update(hq_id, academy_id, data.name)
        if not hq:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Headquarters not found")
        return hq

    async def delete_hq(self, hq_id: uuid.UUID, academy_id: uuid.UUID):
        deleted = await self.repo.delete(hq_id, academy_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Headquarters not found")
