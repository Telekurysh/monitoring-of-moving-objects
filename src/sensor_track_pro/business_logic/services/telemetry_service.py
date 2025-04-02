from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.interfaces.repository.itelemetry_repo import ITelemetryRepository
from src.sensor_track_pro.business_logic.models.common_types import FilterParams
from src.sensor_track_pro.business_logic.models.telemetry_model import TelemetryBase
from src.sensor_track_pro.business_logic.models.telemetry_model import TelemetryModel
from src.sensor_track_pro.business_logic.services.base_service import BaseService


class TelemetryService(BaseService[TelemetryModel]):
    def __init__(self, telemetry_repository: ITelemetryRepository):
        super().__init__(telemetry_repository)
        self._telemetry_repository = telemetry_repository

    async def create_telemetry(self, telemetry_data: TelemetryBase) -> TelemetryModel:
        return await self._telemetry_repository.create(telemetry_data)

    async def get_telemetry(self, telemetry_id: UUID) -> TelemetryModel | None:
        return await self._telemetry_repository.get_by_id(telemetry_id)

    async def get_all_telemetry(self, skip: int = 0, limit: int = 100, **filters: FilterParams) -> list[TelemetryModel]:
        return await self._telemetry_repository.get_all(skip, limit, **filters)

    async def update_telemetry(self, telemetry_id: UUID, telemetry_data: dict[str, Any]) -> TelemetryModel | None:
        return await self._telemetry_repository.update(telemetry_id, telemetry_data)

    async def delete_telemetry(self, telemetry_id: UUID) -> bool:
        return await self._telemetry_repository.delete(telemetry_id)

    async def get_telemetry_by_object(self, object_id: UUID) -> list[TelemetryModel]:
        return await self._telemetry_repository.get_by_object_id(object_id)

    async def get_telemetry_by_timerange(self, start_time: datetime, end_time: datetime) -> list[TelemetryModel]:
        return await self._telemetry_repository.get_by_time_range(start_time, end_time)

    async def get_telemetry_by_signal_strength(self, min_strength: float, max_strength: float) -> list[TelemetryModel]:
        return await self._telemetry_repository.get_by_signal_strength(min_strength, max_strength)
