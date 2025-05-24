from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.models.sensor_model import SensorBase
from src.sensor_track_pro.business_logic.models.sensor_model import SensorModel
from src.sensor_track_pro.business_logic.models.sensor_model import SensorStatus
from src.sensor_track_pro.business_logic.models.sensor_model import SensorType
from src.sensor_track_pro.business_logic.services.sensor_service import SensorService
from src.sensor_track_pro.data_access.database import get_async_db
from src.sensor_track_pro.data_access.repositories.sensors_repo import SensorRepository


router = APIRouter()

_db_dep = Depends(get_async_db)


def get_sensor_service(session: AsyncSession = _db_dep) -> SensorService:
    return SensorService(SensorRepository(session))


_sensor_service_dep = Depends(get_sensor_service)


@router.post("/", response_model=SensorModel)
async def create_sensor(
    sensor_data: SensorBase,
    service: SensorService = _sensor_service_dep
) -> SensorModel:
    return await service.create_sensor(sensor_data)


@router.get("/{sensor_id}", response_model=SensorModel)
async def get_sensor(
    sensor_id: UUID,
    service: SensorService = _sensor_service_dep
) -> SensorModel:
    sensor = await service.get_sensor(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.get("/", response_model=list[SensorModel])
async def get_sensors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    service: SensorService = _sensor_service_dep
) -> list[SensorModel]:
    return await service.get_sensors(skip=skip, limit=limit)


@router.put("/{sensor_id}", response_model=SensorModel)
async def update_sensor(
    sensor_id: UUID,
    sensor_data: dict[str, object],
    service: SensorService = _sensor_service_dep
) -> SensorModel:
    sensor = await service.update_sensor(sensor_id, sensor_data)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.delete("/{sensor_id}")
async def delete_sensor(
    sensor_id: UUID,
    service: SensorService = _sensor_service_dep
) -> dict[str, str]:
    if not await service.delete_sensor(sensor_id):
        raise HTTPException(status_code=404, detail="Sensor not found")
    return {"status": "success"}


@router.get("/type/{sensor_type}", response_model=list[SensorModel])
async def get_sensors_by_type(
    sensor_type: SensorType,
    service: SensorService = _sensor_service_dep
) -> list[SensorModel]:
    return await service.get_sensors_by_type(sensor_type)


@router.get("/status/{status}", response_model=list[SensorModel])
async def get_sensors_by_status(
    status: SensorStatus,
    service: SensorService = _sensor_service_dep
) -> list[SensorModel]:
    return await service.get_sensors_by_status(status)
