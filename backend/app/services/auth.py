from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.academy import Academy
from app.repositories.academy import AcademyRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = AcademyRepository(db)

    async def register(self, data: RegisterRequest) -> Academy:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        academy = await self.repo.create(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
        )
        return academy

    async def login(self, data: LoginRequest) -> TokenResponse:
        academy = await self.repo.get_by_email(data.email)
        if not academy or not verify_password(data.password, academy.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token_data = {"sub": str(academy.id)}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        academy = await self.repo.get_by_id(payload["sub"])
        if not academy:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Academy not found")

        token_data = {"sub": str(academy.id)}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )
