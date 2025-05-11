from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.interfaces.repository.ievent_repo import IEventRepository
from src.sensor_track_pro.business_logic.models.common_types import FilterParams
from src.sensor_track_pro.business_logic.models.event_model import EventBase
from src.sensor_track_pro.business_logic.models.event_model import EventModel
from src.sensor_track_pro.business_logic.services.base_service import BaseService


class EventService(BaseService[EventModel]):
    def __init__(self, event_repository: IEventRepository):
        super().__init__(event_repository)
        self._event_repository = event_repository

    async def create_event(self, event_data: EventBase) -> EventModel:
        return await self._event_repository.create(event_data)

    async def get_event(self, event_id: UUID) -> EventModel | None:
        return await self._event_repository.get_by_id(event_id)

    async def get_events(self, skip: int = 0, limit: int = 100, **filters: FilterParams) -> list[EventModel]:
        return await self._event_repository.get_all(skip, limit, **filters)

    async def update_event(self, event_id: UUID, event_data: dict[str, Any]) -> EventModel | None:
        return await self._event_repository.update(event_id, event_data)

    async def delete_event(self, event_id: UUID) -> bool:
        return await self._event_repository.delete(event_id)

    async def get_events_by_sensor(self, sensor_id: UUID) -> list[EventModel]:
        return await self._event_repository.get_by_sensor_id(sensor_id)

    async def get_events_by_timerange(self, start_time: datetime, end_time: datetime) -> list[EventModel]:
        return await self._event_repository.get_by_time_range(start_time, end_time)

    async def get_events_by_coordinates(self, latitude: float, longitude: float, radius: float) -> list[EventModel]:
        return await self._event_repository.get_by_coordinates(latitude, longitude, radius)
