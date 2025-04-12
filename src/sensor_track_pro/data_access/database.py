from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from src.sensor_track_pro.config import get_settings


settings = get_settings()

# Создание движка для асинхронного доступа (FastAPI приложение)
async_engine = create_async_engine(
    f"postgresql+asyncpg://{settings.db_user}@{settings.db_host}:{settings.db_port}/{settings.db_name}",
    echo=settings.debug,
    pool_pre_ping=True
)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


async def get_async_db() -> AsyncGenerator[AsyncSession]:
    """Получение асинхронной сессии базы данных."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()