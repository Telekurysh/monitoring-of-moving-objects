from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.interfaces.repository.ialert_repo import IAlertRepository
from src.sensor_track_pro.business_logic.models.alert_model import AlertBase
from src.sensor_track_pro.business_logic.models.alert_model import AlertModel
from src.sensor_track_pro.business_logic.models.alert_model import AlertSeverity
from src.sensor_track_pro.business_logic.models.alert_model import AlertType
from src.sensor_track_pro.business_logic.models.common_types import FilterParams
from src.sensor_track_pro.business_logic.services.base_service import BaseService


class AlertService(BaseService[AlertModel]):
    def __init__(self, alert_repository: IAlertRepository):
        super().__init__(alert_repository)
        self._alert_repository = alert_repository

    async def create_alert(self, alert_data: AlertBase) -> AlertModel:
        return await self._alert_repository.create(alert_data)

    async def get_alert(self, alert_id: UUID) -> AlertModel | None:
        return await self._alert_repository.get_by_id(alert_id)

    async def get_alerts(self, skip: int = 0, limit: int = 100, **filters: FilterParams) -> list[AlertModel]:
        return await self._alert_repository.get_all(skip, limit, **filters)

    async def update_alert(self, alert_id: UUID, alert_data: dict[str, Any]) -> AlertModel | None:
        return await self._alert_repository.update(alert_id, alert_data)

    async def delete_alert(self, alert_id: UUID) -> bool:
        return await self._alert_repository.delete(alert_id)

    async def get_alerts_by_event(self, event_id: UUID) -> list[AlertModel]:
        return await self._alert_repository.get_by_event_id(event_id)

    async def get_alerts_by_severity(self, severity: AlertSeverity) -> list[AlertModel]:
        return await self._alert_repository.get_by_severity(severity)

    async def get_alerts_by_type(self, alert_type: AlertType) -> list[AlertModel]:
        return await self._alert_repository.get_by_type(alert_type)

    async def get_alerts_by_timerange(self, start_time: datetime, end_time: datetime) -> list[AlertModel]:
        return await self._alert_repository.get_by_time_range(start_time, end_time)
