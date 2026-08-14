from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.auth import AcademyResponse, LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AcademyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new academy",
    responses={
        201: {"description": "Academy created successfully"},
        409: {"description": "Email already registered"},
        422: {"description": "Validation error in request body"},
    },
)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new academy account.

    - **name**: Academy name
    - **email**: Unique email address
    - **password**: Plain text password (hashed server-side)

    ```bash
    curl -X POST http://localhost:8001/api/auth/register \\
      -H "Content-Type: application/json" \\
      -d '{"name": "Mi Academia", "email": "admin@academia.com", "password": "secret123"}'
    ```
    """
    service = AuthService(db)
    academy = await service.register(data)
    return academy


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get access tokens",
    responses={
        200: {"description": "Login successful, returns JWT tokens"},
        401: {"description": "Invalid email or password"},
    },
)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate with email and password. Returns an **access token** (short-lived)
    and a **refresh token** (long-lived).

    Use the access token in the `Authorization: Bearer <token>` header for
    authenticated endpoints.

    ```bash
    curl -X POST http://localhost:8001/api/auth/login \\
      -H "Content-Type: application/json" \\
      -d '{"email": "admin@academia.com", "password": "secret123"}'
    ```
    """
    service = AuthService(db)
    return await service.login(data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    responses={
        200: {"description": "New token pair issued"},
        401: {"description": "Refresh token is invalid or expired"},
    },
)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    The old refresh token is invalidated (rotation).

    ```bash
    curl -X POST http://localhost:8001/api/auth/refresh \\
      -H "Content-Type: application/json" \\
      -d '{"refresh_token": "<your-refresh-token>"}'
    ```
    """
    service = AuthService(db)
    return await service.refresh(data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a refresh token",
    responses={
        204: {"description": "Token revoked successfully"},
        401: {"description": "Refresh token is invalid"},
    },
)
async def logout(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """
    Revoke (invalidate) a refresh token. The token can no longer be used
    to obtain new access tokens.

    ```bash
    curl -X POST http://localhost:8001/api/auth/logout \\
      -H "Content-Type: application/json" \\
      -d '{"refresh_token": "<your-refresh-token>"}'
    ```
    """
    service = AuthService(db)
    await service.logout(data.refresh_token)
