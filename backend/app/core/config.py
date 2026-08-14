from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., description="Secret key for JWT signing. Must be set via environment variable.")
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/academy_crm"
    JWT_EXPIRY_MINUTES: int = 30
    REFRESH_EXPIRY_DAYS: int = 7
    FRONTEND_URL: str = Field(default="http://localhost:5173", description="Frontend URL for CORS")
    DB_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Database connection pool max overflow")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Database connection pool timeout (seconds)")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Database connection pool recycle (seconds)")
    DB_COMMAND_TIMEOUT: int = Field(default=60, description="Database command timeout (seconds)")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()