import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student


class StudentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, academy_id: uuid.UUID, data: dict) -> Student:
        student = Student(academy_id=academy_id, **data)
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def get_by_id(self, student_id: uuid.UUID, academy_id: uuid.UUID) -> Student | None:
        result = await self.db.execute(
            select(Student).where(
                Student.id == student_id,
                Student.academy_id == academy_id,
                Student.status != "deleted",
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_including_deleted(self, student_id: uuid.UUID, academy_id: uuid.UUID) -> Student | None:
        result = await self.db.execute(
            select(Student).where(
                Student.id == student_id,
                Student.academy_id == academy_id,
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        academy_id: uuid.UUID,
        page: int = 1,
        size: int = 20,
        search: str | None = None,
        status: str | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[Student], int]:
        conditions = [Student.academy_id == academy_id]

        if not include_deleted:
            conditions.append(Student.status != "deleted")

        if status:
            conditions.append(Student.status == status)

        if search:
            search_term = f"%{search}%"
            conditions.append(
                or_(
                    Student.first_name.ilike(search_term),
                    Student.last_name.ilike(search_term),
                    Student.email.ilike(search_term),
                    Student.identification_number.ilike(search_term),
                    Student.phone_number.ilike(search_term),
                )
            )

        count_q = select(func.count()).select_from(Student).where(and_(*conditions))
        total = (await self.db.execute(count_q)).scalar_one()

        q = (
            select(Student)
            .where(and_(*conditions))
            .order_by(Student.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.db.execute(q)
        return list(result.scalars().all()), total

    async def update(self, student_id: uuid.UUID, academy_id: uuid.UUID, data: dict) -> Student | None:
        student = await self.get_by_id(student_id, academy_id)
        if not student:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(student, key, value)
        student.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def soft_delete(self, student_id: uuid.UUID, academy_id: uuid.UUID) -> bool:
        student = await self.get_by_id(student_id, academy_id)
        if not student:
            return False
        student.status = "deleted"
        student.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        return True

    async def stats(self, academy_id: uuid.UUID) -> dict:
        base_conditions = [Student.academy_id == academy_id, Student.status != "deleted"]

        total = (await self.db.execute(
            select(func.count()).select_from(Student).where(and_(*base_conditions))
        )).scalar_one()

        active = (await self.db.execute(
            select(func.count()).select_from(Student).where(and_(*base_conditions, Student.status == "active"))
        )).scalar_one()

        inactive = (await self.db.execute(
            select(func.count()).select_from(Student).where(and_(*base_conditions, Student.status == "inactive"))
        )).scalar_one()

        pending = (await self.db.execute(
            select(func.count()).select_from(Student).where(and_(*base_conditions, Student.status == "pending"))
        )).scalar_one()

        graduated = (await self.db.execute(
            select(func.count()).select_from(Student).where(and_(*base_conditions, Student.status == "graduated"))
        )).scalar_one()

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = (await self.db.execute(
            select(func.count()).select_from(Student).where(
                and_(*base_conditions, Student.created_at >= first_of_month)
            )
        )).scalar_one()

        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "pending": pending,
            "graduated": graduated,
            "new_this_month": new_this_month,
        }

    async def check_email_unique(self, academy_id: uuid.UUID, email: str, exclude_id: uuid.UUID | None = None) -> bool:
        conditions = [
            Student.academy_id == academy_id,
            Student.email == email,
            Student.status != "deleted",
        ]
        if exclude_id:
            conditions.append(Student.id != exclude_id)
        result = await self.db.execute(
            select(func.count()).select_from(Student).where(and_(*conditions))
        )
        return result.scalar_one() == 0

    async def check_identification_unique(self, academy_id: uuid.UUID, identification_number: str, exclude_id: uuid.UUID | None = None) -> bool:
        conditions = [
            Student.academy_id == academy_id,
            Student.identification_number == identification_number,
            Student.status != "deleted",
        ]
        if exclude_id:
            conditions.append(Student.id != exclude_id)
        result = await self.db.execute(
            select(func.count()).select_from(Student).where(and_(*conditions))
        )
        return result.scalar_one() == 0
