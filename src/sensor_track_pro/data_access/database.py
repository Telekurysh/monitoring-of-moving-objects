from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.sensor_track_pro.config import get_settings


settings = get_settings()

_engine = None


def get_async_engine() -> AsyncEngine:
    global _engine
    if (_engine is None):
        # include password if provided
        password_segment = f":{settings.db_password}" if settings.db_password else ""
        _engine = create_async_engine(
            f"postgresql+asyncpg://{settings.db_user}{password_segment}@{settings.db_host}:{settings.db_port}/{settings.db_name}",
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
    return _engine


async_engine = get_async_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession
)


async def get_async_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_models() -> None:
    from src.sensor_track_pro.data_access.models.base import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None