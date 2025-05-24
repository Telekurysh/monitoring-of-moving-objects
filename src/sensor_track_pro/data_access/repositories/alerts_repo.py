from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.interfaces.repository.ialert_repo import IAlertRepository
from src.sensor_track_pro.business_logic.models.alert_model import AlertBase
from src.sensor_track_pro.business_logic.models.alert_model import AlertModel
from src.sensor_track_pro.business_logic.models.alert_model import AlertSeverity
from src.sensor_track_pro.business_logic.models.alert_model import AlertType
from src.sensor_track_pro.data_access.models.alerts import Alert
from src.sensor_track_pro.data_access.repositories.base import BaseRepository


class AlertRepository(BaseRepository[Alert], IAlertRepository):  # type: ignore[misc]
    """Репозиторий для работы с оповещениями."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Alert)

    async def create(self, alert_data: AlertBase) -> AlertModel:  # type: ignore[override]
        """Создает новое оповещение."""
        db_alert = Alert(**alert_data.model_dump())
        created_alert = await super().create(db_alert)
        return await self.get_by_id(created_alert.id)

    async def get_by_event_id(self, event_id: UUID) -> list[AlertModel]:
        """Получает оповещения по ID события."""
        query = select(Alert).filter(Alert.event_id == event_id)
        result = await self._session.execute(query)
        return [AlertModel.model_validate(alert) for alert in result.scalars().all()]

    async def get_by_severity(
        self, 
        severity: AlertSeverity,
        skip: int = 0,
        limit: int = 100
    ) -> list[AlertModel]:
        """Получает оповещения по уровню важности."""
        query = select(Alert).filter(Alert.severity == severity).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [AlertModel.model_validate(alert) for alert in result.scalars().all()]

    async def get_by_type(
        self,
        alert_type: AlertType,
        skip: int = 0,
        limit: int = 100
    ) -> list[AlertModel]:
        """Получает оповещения по типу."""
        query = select(Alert).filter(Alert.alert_type == alert_type).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [AlertModel.model_validate(alert) for alert in result.scalars().all()]

    async def get_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> list[AlertModel]:
        """Получает оповещения за временной период."""
        query = (
            select(Alert)
            .filter(Alert.timestamp.between(start_time, end_time))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [AlertModel.model_validate(alert) for alert in result.scalars().all()]
