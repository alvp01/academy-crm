import uuid

from pydantic import BaseModel, field_validator


class ClassroomCreate(BaseModel):
    headquarters_id: uuid.UUID
    name: str
    classes_capacity: int

    @field_validator("classes_capacity")
    @classmethod
    def capacity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("classes_capacity must be greater than 0")
        return v


class ClassroomUpdate(BaseModel):
    name: str | None = None
    classes_capacity: int | None = None

    @field_validator("classes_capacity")
    @classmethod
    def capacity_must_be_positive(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("classes_capacity must be greater than 0")
        return v


class ClassroomResponse(BaseModel):
    id: uuid.UUID
    headquarters_id: uuid.UUID
    name: str
    classes_capacity: int

    model_config = {"from_attributes": True}


class PaginatedClassroomResponse(BaseModel):
    items: list[ClassroomResponse]
    total: int
    page: int
    size: int
