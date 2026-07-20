import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.headquarters import Headquarters


class HeadquartersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, academy_id: uuid.UUID, name: str) -> Headquarters:
        hq = Headquarters(academy_id=academy_id, name=name)
        self.db.add(hq)
        await self.db.commit()
        await self.db.refresh(hq)
        return hq

    async def get_by_id(self, hq_id: uuid.UUID, academy_id: uuid.UUID) -> Headquarters | None:
        result = await self.db.execute(
            select(Headquarters).where(
                Headquarters.id == hq_id,
                Headquarters.academy_id == academy_id,
            )
        )
        return result.scalar_one_or_none()

    async def list(self, academy_id: uuid.UUID, page: int = 1, size: int = 20) -> tuple[list[Headquarters], int]:
        count_q = select(func.count()).select_from(Headquarters).where(Headquarters.academy_id == academy_id)
        total = (await self.db.execute(count_q)).scalar_one()

        q = (
            select(Headquarters)
            .where(Headquarters.academy_id == academy_id)
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(q)
        return list(result.scalars().all()), total

    async def update(self, hq_id: uuid.UUID, academy_id: uuid.UUID, name: str) -> Headquarters | None:
        hq = await self.get_by_id(hq_id, academy_id)
        if not hq:
            return None
        hq.name = name
        await self.db.commit()
        await self.db.refresh(hq)
        return hq

    async def delete(self, hq_id: uuid.UUID, academy_id: uuid.UUID) -> bool:
        hq = await self.get_by_id(hq_id, academy_id)
        if not hq:
            return False
        await self.db.delete(hq)
        await self.db.commit()
        return True
