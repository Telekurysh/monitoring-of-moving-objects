from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from src.sensor_track_pro.api.dependencies.services import get_telemetry_service
from src.sensor_track_pro.business_logic.models.telemetry_model import TelemetryBase
from src.sensor_track_pro.business_logic.models.telemetry_model import TelemetryModel
from src.sensor_track_pro.business_logic.services.telemetry_service import TelemetryService


_telemetry_service_dep = Depends(get_telemetry_service)

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post("/", response_model=TelemetryModel)
async def create_telemetry(
    telemetry_data: TelemetryBase,
    telemetry_service: TelemetryService = _telemetry_service_dep
) -> TelemetryModel:
    return await telemetry_service.create_telemetry(telemetry_data)


@router.get(
    "/{telemetry_id}",
    response_model=TelemetryModel
)
async def get_telemetry(
    telemetry_id: UUID,
    telemetry_service: TelemetryService = _telemetry_service_dep
) -> TelemetryModel:
    telemetry = await telemetry_service.get_telemetry(telemetry_id)
    if not telemetry:
        raise HTTPException(status_code=404, detail="Telemetry not found")
    return telemetry


@router.get("/", response_model=list[TelemetryModel])
async def get_all_telemetry(
    skip: int = 0,
    limit: int = 100,
    telemetry_service: TelemetryService = _telemetry_service_dep
) -> list[TelemetryModel]:
    return await telemetry_service.get_all_telemetry(skip, limit)


@router.put(
    "/{telemetry_id}",
    response_model=TelemetryModel
)
async def update_telemetry(
    telemetry_id: UUID,
    telemetry_data: dict[str, Any],
    telemetry_service: TelemetryService = _telemetry_service_dep
) -> TelemetryModel:
    updated = await telemetry_service.update_telemetry(telemetry_id, telemetry_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Telemetry not found")
    return updated


@router.delete(
    "/{telemetry_id}",
    response_model=dict[str, str]
)
async def delete_telemetry(
    telemetry_id: UUID,
    telemetry_service: TelemetryService = _telemetry_service_dep
) -> dict[str, str]:
    success = await telemetry_service.delete_telemetry(telemetry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Telemetry not found")
    return {"detail": "Deleted successfully"}


@router.get(
    "/object/{object_id}",
    response_model=list[TelemetryModel]
)
async def get_telemetry_by_object(
    object_id: UUID,
    telemetry_service: TelemetryService = _telemetry_service_dep
) -> list[TelemetryModel]:
    return await telemetry_service.get_telemetry_by_object(object_id)


@router.get(
    "/timerange/",
    response_model=list[TelemetryModel]
)
async def get_telemetry_by_timerange(
    start_time: datetime,
    end_time: datetime,
    telemetry_service: TelemetryService = _telemetry_service_dep
) -> list[TelemetryModel]:
    return await telemetry_service.get_telemetry_by_timerange(start_time, end_time)


@router.get(
    "/signal/",
    response_model=list[TelemetryModel]
)
async def get_telemetry_by_signal(
    min_strength: float,
    max_strength: float,
    telemetry_service: TelemetryService = _telemetry_service_dep
) -> list[TelemetryModel]:
    return await telemetry_service.get_telemetry_by_signal_strength(min_strength, max_strength)