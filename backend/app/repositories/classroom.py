import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.classroom import Classroom


class ClassroomRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, headquarters_id: uuid.UUID, name: str, classes_capacity: int) -> Classroom:
        room = Classroom(headquarters_id=headquarters_id, name=name, classes_capacity=classes_capacity)
        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def get_by_id(self, room_id: uuid.UUID, academy_id: uuid.UUID) -> Classroom | None:
        """Get classroom scoped by academy via headquarters join."""
        from app.models.headquarters import Headquarters

        result = await self.db.execute(
            select(Classroom)
            .join(Headquarters, Headquarters.id == Classroom.headquarters_id)
            .where(Classroom.id == room_id, Headquarters.academy_id == academy_id)
        )
        return result.scalar_one_or_none()

    async def list(self, academy_id: uuid.UUID, page: int = 1, size: int = 20) -> tuple[list[Classroom], int]:
        from app.models.headquarters import Headquarters

        base = (
            select(Classroom)
            .join(Headquarters, Headquarters.id == Classroom.headquarters_id)
            .where(Headquarters.academy_id == academy_id)
        )

        count_q = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_q)).scalar_one()

        q = base.offset((page - 1) * size).limit(size)
        result = await self.db.execute(q)
        return list(result.scalars().all()), total

    async def update(self, room_id: uuid.UUID, academy_id: uuid.UUID, **kwargs) -> Classroom | None:
        room = await self.get_by_id(room_id, academy_id)
        if not room:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(room, key, value)
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def delete(self, room_id: uuid.UUID, academy_id: uuid.UUID) -> bool:
        room = await self.get_by_id(room_id, academy_id)
        if not room:
            return False
        await self.db.delete(room)
        await self.db.commit()
        return True
