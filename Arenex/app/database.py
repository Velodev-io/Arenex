import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/arenex"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "dev-secret-key-must-be-changed"
    ADMIN_API_KEY: str = "dev-admin-key"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175"
    GROQ_API_KEY: str = "" # Added to prevent validation errors

    @property
    def async_database_url(self) -> str:
        # Strip query params like sslmode which asyncpg doesn't support in the URL string
        if "?" in self.DATABASE_URL:
            return self.DATABASE_URL.split("?")[0]
        return self.DATABASE_URL

    class Config:
        env_file = ".env"
        extra = "ignore" # Allow extra env vars without crashing

settings = Settings()

# Neon requires SSL. asyncpg uses 'ssl' argument instead of 'sslmode' in URL
engine = create_async_engine(
    settings.async_database_url,
    echo=True,
    connect_args={"ssl": True}
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
