import uuid

from pydantic import BaseModel


class HQCreate(BaseModel):
    name: str


class HQUpdate(BaseModel):
    name: str


class HQResponse(BaseModel):
    id: uuid.UUID
    academy_id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


class PaginatedHQResponse(BaseModel):
    items: list[HQResponse]
    total: int
    page: int
    size: int
