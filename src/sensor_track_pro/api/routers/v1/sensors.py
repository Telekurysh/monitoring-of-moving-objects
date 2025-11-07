from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Body
from fastapi import Response
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.models.sensor_model import SensorBase
from src.sensor_track_pro.business_logic.models.sensor_model import SensorModel
from src.sensor_track_pro.business_logic.models.sensor_model import SensorStatus
from src.sensor_track_pro.business_logic.models.sensor_model import SensorType
from pydantic import BaseModel
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


class SensorsResponse(BaseModel):
    items: list[SensorModel]
    total: int | None = None


@router.get("/", response_model=SensorsResponse)
async def get_sensors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    sensor_type: SensorType | None = Query(None),
    status: SensorStatus | None = Query(None),
    service: SensorService = _sensor_service_dep
) -> list[SensorModel]:
    """
    Получить список сенсоров с опциональной фильтрацией по типу и/или статусу.

    Если заданы оба фильтра — отфильтровываем список на уровне роутера.
    """
    items = await service.get_sensors(skip=skip, limit=limit)

    if sensor_type is None and status is None:
        return SensorsResponse(items=items, total=len(items))

    def match(s: SensorModel) -> bool:
        if sensor_type is not None and s.type != sensor_type:
            return False
        if status is not None and s.status != status:
            return False
        return True

    filtered = [s for s in items if match(s)]
    return SensorsResponse(items=filtered, total=len(filtered))


@router.put("/{sensor_id}", response_model=SensorModel)
async def update_sensor(
    sensor_id: UUID,
    sensor_data: SensorBase = Body(..., example={
        "object_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "type": "gps",
        "location": "string",
        "status": "active",
        "latitude": 0,
        "longitude": 0,
    }),
    service: SensorService = _sensor_service_dep
) -> SensorModel:
    sensor = await service.update_sensor(sensor_id, sensor_data)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@router.delete("/{sensor_id}", status_code=HTTP_204_NO_CONTENT, responses={404: {"description": "Alert not found"}})
async def delete_sensor(
    sensor_id: UUID,
    service: SensorService = _sensor_service_dep
) -> Response:
    if not await service.delete_sensor(sensor_id):
        raise HTTPException(status_code=404, detail="Sensor not found")
    return Response(status_code=HTTP_204_NO_CONTENT)


# old routes for type and status are consolidated into the root GET / with query params
