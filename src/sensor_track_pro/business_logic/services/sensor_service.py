from __future__ import annotations

from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.interfaces.repository.isensor_repo import ISensorRepository
from src.sensor_track_pro.business_logic.models.common_types import FilterParams
from src.sensor_track_pro.business_logic.models.sensor_model import SensorBase
from src.sensor_track_pro.business_logic.models.sensor_model import SensorModel
from src.sensor_track_pro.business_logic.models.sensor_model import SensorStatus
from src.sensor_track_pro.business_logic.models.sensor_model import SensorType
from src.sensor_track_pro.business_logic.services.base_service import BaseService


class SensorService(BaseService[SensorModel]):
    def __init__(self, sensor_repository: ISensorRepository):
        super().__init__(sensor_repository)
        self._sensor_repository = sensor_repository

    async def create_sensor(self, sensor_data: SensorBase) -> SensorModel:
        return await self._sensor_repository.create(sensor_data)

    async def get_sensor(self, sensor_id: UUID) -> SensorModel | None:
        return await self._sensor_repository.get_by_id(sensor_id)

    async def get_sensors(self, skip: int = 0, limit: int = 100, **filters: FilterParams) -> list[SensorModel]:
        return await self._sensor_repository.get_all(skip, limit, **filters)

    async def update_sensor(self, sensor_id: UUID, sensor_data: dict[str, Any]) -> SensorModel | None:
        return await self._sensor_repository.update(sensor_id, sensor_data)

    async def delete_sensor(self, sensor_id: UUID) -> bool:
        return await self._sensor_repository.delete(sensor_id)

    async def get_sensors_by_object(self, object_id: UUID) -> list[SensorModel]:
        return await self._sensor_repository.get_by_object_id(object_id)

    async def get_sensors_by_type(self, sensor_type: SensorType) -> list[SensorModel]:
        return await self._sensor_repository.get_by_type(sensor_type)

    async def get_sensors_by_status(self, status: SensorStatus) -> list[SensorModel]:
        return await self._sensor_repository.get_by_status(status)
