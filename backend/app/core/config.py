from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "change-me-in-production"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/academy_crm"
    JWT_EXPIRY_MINUTES: int = 30
    REFRESH_EXPIRY_DAYS: int = 7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
