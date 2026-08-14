import uuid

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AcademyResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str

    model_config = {"from_attributes": True}
