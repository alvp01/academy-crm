import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.student import StudentRepository
from app.schemas.student import StudentCreate, StudentUpdate


class StudentService:
    def __init__(self, db: AsyncSession):
        self.repo = StudentRepository(db)

    async def create_student(self, academy_id: uuid.UUID, data: StudentCreate):
        if not await self.repo.check_email_unique(academy_id, data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A student with this email already exists in this academy",
            )
        if not await self.repo.check_identification_unique(academy_id, data.identification_number):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A student with this identification number already exists in this academy",
            )
        return await self.repo.create(academy_id, data.model_dump())

    async def get_student(self, student_id: uuid.UUID, academy_id: uuid.UUID):
        student = await self.repo.get_by_id(student_id, academy_id)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    async def list_students(
        self,
        academy_id: uuid.UUID,
        page: int = 1,
        size: int = 20,
        search: str | None = None,
        status_filter: str | None = None,
        include_deleted: bool = False,
    ):
        items, total = await self.repo.list(
            academy_id, page, size, search, status_filter, include_deleted
        )
        return {"items": items, "total": total, "page": page, "size": size}

    async def update_student(self, student_id: uuid.UUID, academy_id: uuid.UUID, data: StudentUpdate):
        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data:
            if not await self.repo.check_email_unique(academy_id, update_data["email"], exclude_id=student_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A student with this email already exists in this academy",
                )

        if "identification_number" in update_data:
            if not await self.repo.check_identification_unique(academy_id, update_data["identification_number"], exclude_id=student_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A student with this identification number already exists in this academy",
                )

        student = await self.repo.update(student_id, academy_id, update_data)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student

    async def delete_student(self, student_id: uuid.UUID, academy_id: uuid.UUID):
        deleted = await self.repo.soft_delete(student_id, academy_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    async def get_stats(self, academy_id: uuid.UUID):
        return await self.repo.stats(academy_id)
