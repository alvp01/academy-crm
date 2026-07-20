import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Headquarters(Base):
    __tablename__ = "headquarters"
    __table_args__ = (
        UniqueConstraint("academy_id", "name", name="uq_hq_academy_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
