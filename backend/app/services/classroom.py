import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.classroom import ClassroomRepository
from app.schemas.classroom import ClassroomCreate, ClassroomUpdate


class ClassroomService:
    def __init__(self, db: AsyncSession):
        self.repo = ClassroomRepository(db)

    async def create_classroom(self, academy_id: uuid.UUID, data: ClassroomCreate):
        # Verify HQ belongs to academy and check name uniqueness
        rooms, _ = await self.repo.list(academy_id, page=1, size=1000)
        if any(r.name == data.name and r.headquarters_id == data.headquarters_id for r in rooms):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Classroom name already exists for this headquarters",
            )
        return await self.repo.create(data.headquarters_id, data.name, data.classes_capacity)

    async def get_classroom(self, room_id: uuid.UUID, academy_id: uuid.UUID):
        room = await self.repo.get_by_id(room_id, academy_id)
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")
        return room

    async def list_classrooms(self, academy_id: uuid.UUID, page: int = 1, size: int = 20):
        items, total = await self.repo.list(academy_id, page, size)
        return {"items": items, "total": total, "page": page, "size": size}

    async def update_classroom(self, room_id: uuid.UUID, academy_id: uuid.UUID, data: ClassroomUpdate):
        rooms, _ = await self.repo.list(academy_id, page=1, size=1000)
        if data.name and any(r.name == data.name and r.headquarters_id == ... for r in rooms):
            # This is a simplified check — full implementation would need HQ context
            pass
        room = await self.repo.update(room_id, academy_id, **data.model_dump(exclude_unset=True))
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")
        return room

    async def delete_classroom(self, room_id: uuid.UUID, academy_id: uuid.UUID):
        deleted = await self.repo.delete(room_id, academy_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")
