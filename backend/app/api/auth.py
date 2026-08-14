from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_academy, get_db
from app.core.security import clear_auth_cookies, set_auth_cookies
from app.models.academy import Academy
from app.schemas.auth import AcademyResponse, LoginRequest, RegisterRequest
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
async def register(data: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Register a new academy account. Sets auth cookies on the response.

    - **name**: Academy name
    - **email**: Unique email address
    - **password**: Plain text password (hashed server-side)
    """
    service = AuthService(db)
    academy, access_token, refresh_token, csrf_token = await service.register(data)
    set_auth_cookies(response, access_token, refresh_token, csrf_token, settings.ENVIRONMENT)
    return academy


@router.post(
    "/login",
    response_model=AcademyResponse,
    summary="Login and set auth cookies",
    responses={
        200: {"description": "Login successful, auth cookies set"},
        401: {"description": "Invalid email or password"},
    },
)
async def login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Authenticate with email and password. Sets httponly auth cookies on the response.
    The response body contains only user data (no tokens).
    """
    service = AuthService(db)
    academy, access_token, refresh_token, csrf_token = await service.login(data)
    set_auth_cookies(response, access_token, refresh_token, csrf_token, settings.ENVIRONMENT)
    return academy


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Refresh access token via cookie",
    responses={
        200: {"description": "New auth cookies set"},
        401: {"description": "Refresh token is invalid or expired"},
    },
)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Rotate refresh token and issue new auth cookies.
    Reads the refresh token from the refresh_token cookie (no request body).
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token cookie missing")

    service = AuthService(db)
    new_access_token, new_refresh_token, csrf_token = await service.refresh(refresh_token)
    set_auth_cookies(response, new_access_token, new_refresh_token, csrf_token, settings.ENVIRONMENT)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout and clear auth cookies",
    responses={
        204: {"description": "Cookies cleared successfully"},
    },
)
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Revoke the refresh token and clear all auth cookies.
    Reads the refresh token from the refresh_token cookie (no request body).
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        service = AuthService(db)
        await service.logout(refresh_token)
    clear_auth_cookies(response)


@router.post(
    "/me",
    response_model=AcademyResponse,
    summary="Get current user from access token cookie",
    responses={
        200: {"description": "Current user data"},
        401: {"description": "Not authenticated"},
    },
)
async def me(academy: Academy = Depends(get_current_academy)):
    """
    Return the current authenticated user's data.
    Requires a valid access_token cookie or Authorization Bearer header.
    """
    return academy
