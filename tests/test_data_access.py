from __future__ import annotations

import os
import sys
from typing import AsyncGenerator
from uuid import uuid4
from datetime import datetime, UTC  # Используем UTC из datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sensor_track_pro.data_access.database import get_async_engine, dispose_engine
from src.sensor_track_pro.data_access.models.base import Base
from src.sensor_track_pro.data_access.models.zones import Zone
from src.sensor_track_pro.data_access.repositories.base import BaseRepository

@pytest_asyncio.fixture(scope="function")
async def engine():
    engine = get_async_engine()
    yield engine
    await dispose_engine()  # Явное удаление engine после теста

@pytest_asyncio.fixture(scope="function")
async def prepare_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest_asyncio.fixture(scope="function")
async def db_session(engine, prepare_db) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        try:
            await session.execute(text("TRUNCATE TABLE zones RESTART IDENTITY CASCADE"))
            await session.commit()
            yield session
        finally:
            await session.close()

@pytest_asyncio.fixture
async def zone_repo(db_session: AsyncSession) -> BaseRepository[Zone]:
    return BaseRepository(db_session, Zone)


@pytest.mark.asyncio
async def test_create_get_update_delete_zone(zone_repo: BaseRepository):
    zone = Zone(
        id=uuid4(),
        name="Test Zone",
        zone_type="polygon",
        coordinates={"type": "polygon", "points": [(0, 0), (1, 0), (1, 1), (0, 0)]},
        description="Test description",
        boundary_polygon="POLYGON((0 0, 1 0, 1 1, 0 0))",
        center_point="POINT(0.5 0.5)",
        created_at=datetime.now(UTC),  # Используем timezone-aware datetime
        updated_at=datetime.now(UTC)
    )
    created = await zone_repo.create(zone)
    assert created.id is not None

    fetched = await zone_repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "Test Zone"

    updated = await zone_repo.update(created.id, {"name": "Updated Zone"})
    assert updated is not None
    assert updated.name == "Updated Zone"

    deleted = await zone_repo.delete(created.id)
    assert deleted is True
    fetched_after_delete = await zone_repo.get_by_id(created.id)
    assert fetched_after_delete is None

@pytest.mark.asyncio
async def test_error_handling_on_create(zone_repo: BaseRepository):
    faulty_zone = Zone(
        id=uuid4(),
        name="",
        zone_type="polygon",
        coordinates={"type": "polygon", "points": [(0, 0), (1, 0)]},
        description="Faulty zone",
        boundary_polygon="",
        center_point="",
        created_at=datetime.now(UTC),  # Используем timezone-aware datetime
        updated_at=datetime.now(UTC)
    )
    with pytest.raises(Exception) as exc_info:
        await zone_repo.create(faulty_zone)
    assert "Ошибка создания зоны:" in str(exc_info.value)

