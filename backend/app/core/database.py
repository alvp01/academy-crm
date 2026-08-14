import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


def create_engine():
    """Create async engine with connection pooling and timeout configuration."""
    return create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True,
        connect_args={
            "command_timeout": settings.DB_COMMAND_TIMEOUT,
            "server_settings": {
                "application_name": "academy-crm",
            },
        },
    )


engine = create_engine()
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """Initialize database connection and verify connectivity with retry/backoff."""
    max_retries = 10
    base_delay = 1.0
    max_delay = 30.0

    for attempt in range(1, max_retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully")
            return
        except Exception as e:
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            if attempt == max_retries:
                logger.error("Database connection failed after %d attempts: %s", max_retries, e)
                raise RuntimeError(f"Database connection failed after {max_retries} attempts: {e}") from e
            logger.warning("Database connection attempt %d/%d failed: %s. Retrying in %.1fs...", attempt, max_retries, e, delay)
            await asyncio.sleep(delay)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()