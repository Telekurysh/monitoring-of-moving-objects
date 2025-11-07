from __future__ import annotations

from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.interfaces.repository.izone_repo import IZoneRepository
from src.sensor_track_pro.business_logic.models.zone_model import ZoneBase
from src.sensor_track_pro.business_logic.models.zone_model import ZoneModel
from src.sensor_track_pro.business_logic.models.zone_model import ZoneType
from src.sensor_track_pro.business_logic.services.base_service import BaseService


class ZoneService(BaseService[ZoneModel]):
    def __init__(self, zone_repository: IZoneRepository):
        super().__init__(zone_repository)
        self._zone_repository = zone_repository

    async def create_zone(self, zone_data: ZoneBase) -> ZoneModel:
        return await self._zone_repository.create_zone(zone_data)

    async def get_zone(self, zone_id: UUID) -> ZoneModel | None:
        return await self._zone_repository.get_by_id(zone_id)

    async def get_zones(self, skip: int = 0, limit: int = 100, **filters: Any) -> list[ZoneModel]:
        return await self._zone_repository.get_all(skip, limit, **filters)

    async def update_zone(self, zone_id: UUID, zone_data: dict[str, Any]) -> ZoneModel | None:
        return await self._zone_repository.update(zone_id, zone_data)

    async def delete_zone(self, zone_id: UUID) -> bool:
        return await self._zone_repository.delete(zone_id)

    async def get_zones_by_type(self, zone_type: ZoneType) -> list[ZoneModel]:
        return await self._zone_repository.get_by_type(zone_type)

    async def get_zones_containing_point(self, latitude: float, longitude: float) -> list[ZoneModel]:
        return await self._zone_repository.get_zones_containing_point(latitude, longitude)

    async def get_zones_for_object(self, object_id: UUID) -> list[ZoneModel]:
        return await self._zone_repository.get_zones_for_object(object_id)

    async def get_zones_for_map(self) -> list[ZoneModel]:
        """Получить все зоны для карты."""
        return await self._zone_repository.get_all_for_map()
