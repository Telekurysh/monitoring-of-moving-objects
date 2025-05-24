from __future__ import annotations

from typing import Any
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

    async def create(self, sensor_data: SensorBase) -> SensorModel:  # type: ignore[override]
        """Создает новый сенсор."""
        data = sensor_data.model_dump()
        db_sensor = Sensor(**data)
        created_sensor = await super().create(db_sensor)  # сохраняем созданный объект
        return SensorModel.model_validate(created_sensor)

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
            .filter(Sensor.sensor_type == sensor_type)
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
            .filter(Sensor.sensor_status == status)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [SensorModel.model_validate(s) for s in result.scalars().all()]

    async def get_by_id(self, sensor_id: UUID) -> SensorModel | None:  # type: ignore[override]
        db_sensor = await super().get_by_id(sensor_id)
        return SensorModel.model_validate(db_sensor) if db_sensor else None

    async def get_all(self, skip: int = 0, limit: int = 100, **filters: dict[str, Any]) -> list[SensorModel]:  # type: ignore[override]
        db_list = await super().get_all(skip, limit, **filters)
        return [SensorModel.model_validate(s) for s in db_list]

    async def update(self, sensor_id: UUID, sensor_data: dict[str, Any]) -> SensorModel | None:  # type: ignore[override]
        # Переименовываем алиасы в реальные поля модели
        if "type" in sensor_data:
            sensor_data["sensor_type"] = sensor_data.pop("type")
        if "status" in sensor_data:
            sensor_data["sensor_status"] = sensor_data.pop("status")
        db_sensor = await super().update(sensor_id, sensor_data)
        return SensorModel.model_validate(db_sensor) if db_sensor else None
