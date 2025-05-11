from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.interfaces.repository.itelemetry_repo import ITelemetryRepository
from src.sensor_track_pro.business_logic.models.telemetry_model import TelemetryBase
from src.sensor_track_pro.business_logic.models.telemetry_model import TelemetryModel
from src.sensor_track_pro.data_access.models.telemetry import Telemetry
from src.sensor_track_pro.data_access.repositories.base import BaseRepository


class TelemetryRepository(BaseRepository[Telemetry], ITelemetryRepository):
    """Репозиторий для работы с телеметрией."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Telemetry)

    async def create(self, telemetry_data: TelemetryBase) -> TelemetryModel:  # type: ignore[override]
        """Создает новую запись телеметрии."""
        db_telemetry = Telemetry(**telemetry_data.model_dump())
        instance = await super().create(db_telemetry)
        return TelemetryModel.model_validate(instance)

    async def get_by_id(self, telemetry_id: UUID) -> TelemetryModel | None:  # type: ignore[override]
        """Получает запись телеметрии по ID."""
        db_telemetry = await super().get_by_id(telemetry_id)
        return TelemetryModel.model_validate(db_telemetry) if db_telemetry else None

    async def get_all(self, skip: int = 0, limit: int = 100, **filters: dict[str, Any]) -> list[TelemetryModel]:  # type: ignore[override]
        """Получает все записи телеметрии с возможностью фильтрации."""
        db_list = await super().get_all(skip, limit, **filters)
        return [TelemetryModel.model_validate(t) for t in db_list]

    async def update(self, telemetry_id: UUID, telemetry_data: dict[str, Any]) -> TelemetryModel | None:  # type: ignore[override]
        """Обновляет запись телеметрии по ID."""
        db_telemetry = await super().update(telemetry_id, telemetry_data)
        return TelemetryModel.model_validate(db_telemetry) if db_telemetry else None

    async def get_by_object_id(
        self, object_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[TelemetryModel]:
        """Получает записи телеметрии по ID объекта."""
        query = select(Telemetry).filter(Telemetry.object_id == object_id).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [TelemetryModel.model_validate(t) for t in result.scalars().all()]

    async def get_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> list[TelemetryModel]:
        """Получает записи телеметрии за период времени."""
        query = select(Telemetry).filter(
            Telemetry.timestamp.between(start_time, end_time)
        ).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [TelemetryModel.model_validate(t) for t in result.scalars().all()]

    async def get_by_signal_strength(
        self,
        min_strength: float,
        max_strength: float,
        skip: int = 0,
        limit: int = 100
    ) -> list[TelemetryModel]:
        """Получает записи телеметрии по уровню сигнала."""
        query = select(Telemetry).filter(
            Telemetry.signal_strength.between(min_strength, max_strength)
        ).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [TelemetryModel.model_validate(t) for t in result.scalars().all()]
