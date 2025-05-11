from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.interfaces.repository.ievent_repo import IEventRepository
from src.sensor_track_pro.business_logic.models.event_model import EventBase
from src.sensor_track_pro.business_logic.models.event_model import EventModel
from src.sensor_track_pro.data_access.models.events import Event
from src.sensor_track_pro.data_access.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event], IEventRepository):  # type: ignore[misc]
    """Репозиторий для работы с событиями."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Event)

    async def create(self, event_data: EventBase) -> EventModel:  # type: ignore[override]
        """Создает новое событие."""
        db_event = Event(**event_data.model_dump())
        await super().create(db_event)
        return EventModel.model_validate(db_event)

    async def get_by_sensor_id(self, sensor_id: UUID, skip: int = 0, limit: int = 100) -> list[EventModel]:
        """Получает события по ID сенсора."""
        query = select(Event).filter(Event.sensor_id == sensor_id).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [EventModel.model_validate(event) for event in result.scalars().all()]

    async def get_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> list[EventModel]:
        """Получает события за временной период."""
        query = (
            select(Event)
            .filter(Event.timestamp >= start_time, Event.timestamp <= end_time)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [EventModel.model_validate(event) for event in result.scalars().all()]

    async def get_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        skip: int = 0,
        limit: int = 100
    ) -> list[EventModel]:
        """Получает события в радиусе от координат."""
        # Используем PostgreSQL функцию ST_DWithin для поиска в радиусе
        query = (
            select(Event)
            .filter(
                Event.location.ST_DWithin(
                    f'SRID=4326;POINT({longitude} {latitude})',
                    radius * 1000  # конвертируем км в метры
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [EventModel.model_validate(event) for event in result.scalars().all()]

    async def get_by_id(self, event_id: UUID) -> EventModel | None:  # type: ignore[override]
        """Получает событие по ID."""
        db_event = await super().get_by_id(event_id)
        return EventModel.model_validate(db_event) if db_event else None

    async def update(self, event_id: UUID, event_data: dict[str, Any]) -> EventModel | None:  # type: ignore[override]
        """Обновляет событие по ID."""
        db_event = await super().update(event_id, event_data)
        return EventModel.model_validate(db_event) if db_event else None

    async def delete(self, event_id: UUID) -> bool:
        """Удаляет событие по ID."""
        return await super().delete(event_id)
