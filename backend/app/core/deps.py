import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.security import decode_token
from app.models.academy import Academy

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


async def get_current_academy(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Academy:
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    academy_id = payload.get("sub")
    if academy_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    result = await db.execute(select(Academy).where(Academy.id == uuid.UUID(academy_id)))
    academy = result.scalar_one_or_none()

    if academy is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Academy not found")

    return academy
