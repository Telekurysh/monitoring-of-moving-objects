from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.interfaces.repository.isensor_repo import ISensorRepository
from src.sensor_track_pro.business_logic.models.sensor_model import SensorBase
from src.sensor_track_pro.business_logic.models.sensor_model import SensorModel
from src.sensor_track_pro.business_logic.models.sensor_model import SensorStatus
from src.sensor_track_pro.business_logic.models.sensor_model import SensorType
from src.sensor_track_pro.data_access.models.sensors import Sensor
from src.sensor_track_pro.data_access.repositories.base import BaseRepository


class SensorRepository(BaseRepository[Sensor], ISensorRepository):
    """Репозиторий для работы с сенсорами."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Sensor)

    async def create(self, sensor_data: SensorBase) -> SensorModel:
        """Создает новый сенсор."""
        db_sensor = Sensor(**sensor_data.model_dump())
        await super().create(db_sensor)
        return SensorModel.model_validate(db_sensor)

    async def get_by_object_id(
        self,
        object_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[SensorModel]:
        """Получает сенсоры объекта."""
        query = (
            select(Sensor)
            .filter(Sensor.object_id == object_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [SensorModel.model_validate(s) for s in result.scalars().all()]

    async def get_by_type(
        self,
        sensor_type: SensorType,
        skip: int = 0,
        limit: int = 100
    ) -> list[SensorModel]:
        """Получает сенсоры определенного типа."""
        query = (
            select(Sensor)
            .filter(Sensor.type == sensor_type)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [SensorModel.model_validate(s) for s in result.scalars().all()]

    async def get_by_status(
        self,
        status: SensorStatus,
        skip: int = 0,
        limit: int = 100
    ) -> list[SensorModel]:
        """Получает сенсоры в определенном статусе."""
        query = (
            select(Sensor)
            .filter(Sensor.status == status)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [SensorModel.model_validate(s) for s in result.scalars().all()]
