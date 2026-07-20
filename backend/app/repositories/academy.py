import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academy import Academy


class AcademyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> Academy:
        academy = Academy(**kwargs)
        self.db.add(academy)
        await self.db.commit()
        await self.db.refresh(academy)
        return academy

    async def get_by_email(self, email: str) -> Academy | None:
        result = await self.db.execute(select(Academy).where(Academy.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, academy_id: uuid.UUID) -> Academy | None:
        result = await self.db.execute(select(Academy).where(Academy.id == academy_id))
        return result.scalar_one_or_none()
