import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import asyncio
import pytest
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.sensor_track_pro.data_access.models.base import Base
from src.sensor_track_pro.data_access.models.zones import Zone
from src.sensor_track_pro.data_access.repositories.base import BaseRepository

from src.sensor_track_pro.data_access.database import async_engine, AsyncSessionLocal

@pytest.fixture(scope="module")
async def async_session():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        yield session
    await async_engine.dispose()

@pytest.fixture
def zone_repo(async_session):
    from src.sensor_track_pro.data_access.models.zones import Zone
    from src.sensor_track_pro.data_access.repositories.base import BaseRepository
    return BaseRepository(async_session, Zone)

@pytest.mark.asyncio
async def test_create_get_update_delete_zone(zone_repo: BaseRepository):
    zone = Zone(
        name="Test Zone",
        zone_type="polygon",
        coordinates={"type": "polygon", "points": [(0, 0), (1, 0), (1, 1), (0, 0)]},
        description="Test description",
        boundary_polygon="POLYGON((0 0, 1 0, 1 1, 0 0))",
        center_point="POINT(0.5 0.5)"
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
        id=str(uuid4()),
        name="",
        zone_type="polygon",
        coordinates={"type": "polygon", "points": [(0, 0), (1, 0)]},
        description="Faulty zone",
        boundary_polygon="",
        center_point=""
    )
    with pytest.raises(Exception) as exc_info:
        await zone_repo.create(faulty_zone)
    assert "Ошибка создания зоны:" in str(exc_info.value)
