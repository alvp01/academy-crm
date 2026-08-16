import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, field_validator


class StudentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    GRADUATED = "graduated"
    DELETED = "deleted"


class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    identification_number: str
    phone_number: str
    address: str
    date_of_birth: datetime
    allergies: str = "N/A"
    referral_source: str
    occupation: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower().strip()


class StudentUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    identification_number: str | None = None
    phone_number: str | None = None
    address: str | None = None
    date_of_birth: datetime | None = None
    allergies: str | None = None
    referral_source: str | None = None
    occupation: str | None = None
    status: StudentStatus | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower().strip()


class StudentResponse(BaseModel):
    id: uuid.UUID
    academy_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    identification_number: str
    phone_number: str
    address: str
    date_of_birth: datetime
    allergies: str
    referral_source: str
    occupation: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedStudentResponse(BaseModel):
    items: list[StudentResponse]
    total: int
    page: int
    size: int


class StudentStatsResponse(BaseModel):
    total: int
    active: int
    inactive: int
    pending: int
    graduated: int
    new_this_month: int
