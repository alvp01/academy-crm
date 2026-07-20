import uuid

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Classroom(Base):
    __tablename__ = "classrooms"
    __table_args__ = (
        UniqueConstraint("headquarters_id", "name", name="uq_classroom_hq_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    headquarters_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("headquarters.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    classes_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
