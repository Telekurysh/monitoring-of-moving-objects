from __future__ import annotations

from datetime import datetime
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

    async def create(self, telemetry_data: TelemetryBase) -> TelemetryModel:
        """Создает новую запись телеметрии."""
        db_telemetry = Telemetry(**telemetry_data.model_dump())
        await super().create(db_telemetry)
        return TelemetryModel.model_validate(db_telemetry)

    async def get_by_id(self, telemetry_id: UUID) -> TelemetryModel | None:
        """Получает запись телеметрии по ID."""
        db_telemetry = await super().get_by_id(telemetry_id)
        return TelemetryModel.model_validate(db_telemetry) if db_telemetry else None

    async def get_by_object_id(self, object_id: UUID) -> list[TelemetryModel]:
        """Получает записи телеметрии по ID объекта."""
        query = select(Telemetry).filter(Telemetry.object_id == object_id)
        result = await self._session.execute(query)
        return [TelemetryModel.model_validate(t) for t in result.scalars().all()]

    async def get_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> list[TelemetryModel]:
        """Получает записи телеметрии за период времени."""
        query = select(Telemetry).filter(
            Telemetry.timestamp.between(start_time, end_time)
        )
        result = await self._session.execute(query)
        return [TelemetryModel.model_validate(t) for t in result.scalars().all()]

    async def get_by_signal_strength(
        self,
        min_strength: float,
        max_strength: float
    ) -> list[TelemetryModel]:
        """Получает записи телеметрии по уровню сигнала."""
        query = select(Telemetry).filter(
            Telemetry.signal_strength.between(min_strength, max_strength)
        )
        result = await self._session.execute(query)
        return [TelemetryModel.model_validate(t) for t in result.scalars().all()]
