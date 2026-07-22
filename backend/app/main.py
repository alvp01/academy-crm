from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.classroom import router as classroom_router
from app.api.headquarters import router as headquarters_router
from app.core.config import settings
from app.core.database import async_session_factory, close_db, init_db
from app.repositories.refresh_token import RefreshTokenRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify database connection
    await init_db()
    # Startup: cleanup expired refresh tokens
    try:
        async with async_session_factory() as db:
            repo = RefreshTokenRepository(db)
            cleaned = await repo.cleanup_expired()
            if cleaned:
                print(f"Cleaned up {cleaned} expired refresh tokens on startup")
    except Exception as e:
        print(f"Cleanup skipped (table may not exist yet): {e}")
    yield
    # Shutdown: close database connections
    await close_db()


app = FastAPI(title="Academy CRM", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(headquarters_router)
app.include_router(classroom_router)


@app.get("/health")
async def health():
    try:
        async with async_session_factory() as db:
            await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "degraded", "database": "disconnected"}