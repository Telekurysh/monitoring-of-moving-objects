from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.interfaces.repository.ievent_repo import IEventRepository
from src.sensor_track_pro.business_logic.models.event_model import EventBase
from src.sensor_track_pro.business_logic.models.event_model import EventModel
from src.sensor_track_pro.data_access.models.events import Event
from src.sensor_track_pro.data_access.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event], IEventRepository):
    """Репозиторий для работы с событиями."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Event)

    async def create(self, event_data: EventBase) -> EventModel:
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
