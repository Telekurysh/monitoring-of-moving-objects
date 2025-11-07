from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Body
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response
from starlette.status import HTTP_204_NO_CONTENT

from src.sensor_track_pro.business_logic.models.alert_model import AlertBase
from src.sensor_track_pro.business_logic.models.alert_model import AlertModel
from src.sensor_track_pro.business_logic.models.alert_model import AlertSeverity
from src.sensor_track_pro.business_logic.models.alert_model import AlertType
from src.sensor_track_pro.business_logic.services.alert_service import AlertService
from src.sensor_track_pro.data_access.database import get_async_db
from src.sensor_track_pro.data_access.repositories.alerts_repo import AlertRepository


router = APIRouter()

# Определяем модульную переменную для get_async_db
_db_dep = Depends(get_async_db)


def get_alert_service(session: AsyncSession = _db_dep) -> AlertService:
    return AlertService(AlertRepository(session))


alert_service_dep = Depends(get_alert_service)


@router.post("/", response_model=AlertModel)
async def create_alert(
    alert_data: AlertBase,
    service: AlertService = alert_service_dep
) -> AlertModel:
    return await service.create_alert(alert_data)


@router.get("/{alert_id}", response_model=AlertModel)
async def get_alert(
    alert_id: UUID,
    service: AlertService = alert_service_dep
) -> AlertModel:
    alert = await service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.get("/", response_model=list[AlertModel])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    severity: AlertSeverity | None = Query(None),
    alert_type: AlertType | None = Query(None),
    event_id: UUID | None = Query(None),
    service: AlertService = alert_service_dep
) -> list[AlertModel]:
    # Приоритет фильтров: event_id -> severity -> alert_type
    if event_id is not None:
        return await service.get_alerts_by_event(event_id)

    if severity is not None:
        return await service.get_alerts_by_severity(severity)

    if alert_type is not None:
        return await service.get_alerts_by_type(alert_type)

    return await service.get_alerts(skip=skip, limit=limit)


@router.put("/{alert_id}", response_model=AlertModel)
async def update_alert(
    alert_id: UUID,
    alert_data: AlertBase = Body(..., example={
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "event_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "alert_type": "zone_exit",
        "severity": "low",
        "message": "string",
        "timestamp": "2025-10-11T10:05:25.532Z",
    }),
    service: AlertService = alert_service_dep
) -> AlertModel:
    alert = await service.update_alert(alert_id, alert_data)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.delete("/{alert_id}", status_code=HTTP_204_NO_CONTENT, responses={404: {"description": "Alert not found"}})
async def delete_alert(
    alert_id: UUID,
    service: AlertService = alert_service_dep
) -> Response:
    if not await service.delete_alert(alert_id):
        raise HTTPException(status_code=404, detail="Alert not found")
    return Response(status_code=HTTP_204_NO_CONTENT)


# old routes for severity/type/event consolidated into root GET / with query params
