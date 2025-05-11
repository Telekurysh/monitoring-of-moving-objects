from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.data_access.models.object_zones import ObjectZone
from src.sensor_track_pro.data_access.repositories.base import BaseRepository


class ObjectZoneRepository(BaseRepository[ObjectZone]):
    """Репозиторий для работы со связями объект-зона."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ObjectZone)

    async def add_object_to_zone(self, object_id: UUID, zone_id: UUID) -> ObjectZone:
        """Добавляет объект в зону."""
        object_zone = ObjectZone(
            object_id=str(object_id),
            zone_id=str(zone_id),
            entered_at=datetime.utcnow()
        )
        return await self.create(object_zone)

    async def remove_object_from_zone(self, object_id: UUID, zone_id: UUID) -> bool:
        """Удаляет объект из зоны."""
        query = (
            select(ObjectZone)
            .filter(
                ObjectZone.object_id == str(object_id),
                ObjectZone.zone_id == str(zone_id),
                ObjectZone.exited_at.is_(None)
            )
        )
        result = await self._session.execute(query)
        object_zone = result.scalar_one_or_none()
        
        if object_zone:
            object_zone.exited_at = datetime.utcnow()
            await self._session.flush()
            await self._session.commit()  # добавлено commit
            return True
        return False

    async def get_object_zones(self, object_id: UUID) -> list[ObjectZone]:
        """Получает все зоны объекта."""
        query = select(ObjectZone).filter(ObjectZone.object_id == str(object_id))
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_zone_objects(self, zone_id: UUID) -> list[ObjectZone]:
        """Получает все объекты в зоне."""
        query = (
            select(ObjectZone)
            .filter(
                ObjectZone.zone_id == str(zone_id),
                ObjectZone.exited_at.is_(None)
            )
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())
