from __future__ import annotations

from typing import AsyncGenerator
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from src.sensor_track_pro.business_logic.models.zone_model import ZoneBase
from src.sensor_track_pro.business_logic.models.zone_model import ZoneModel
from src.sensor_track_pro.business_logic.models.zone_model import ZoneType
from src.sensor_track_pro.business_logic.services.zone_service import ZoneService
from src.sensor_track_pro.data_access.database import AsyncSessionLocal
from src.sensor_track_pro.data_access.repositories.zones_repo import ZoneRepository


router = APIRouter()


async def get_zone_service() -> AsyncGenerator[ZoneService]:
    async with AsyncSessionLocal() as session:
        yield ZoneService(ZoneRepository(session))


_zone_service_dep = Depends(get_zone_service)


@router.post("/", response_model=ZoneModel, status_code=status.HTTP_201_CREATED)
async def create_zone(
    zone: ZoneBase,
    service: ZoneService = _zone_service_dep
) -> ZoneModel:
    return await service.create_zone(zone)


@router.get("/{zone_id}", response_model=ZoneModel)
async def get_zone(
    zone_id: UUID,
    service: ZoneService = _zone_service_dep
) -> ZoneModel:
    zone = await service.get_zone(zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.get("/", response_model=list[ZoneModel])
async def get_zones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    service: ZoneService = _zone_service_dep
) -> list[ZoneModel]:
    return await service.get_zones(skip=skip, limit=limit)


@router.put("/{zone_id}", response_model=ZoneModel)
async def update_zone(
    zone_id: UUID,
    zone_data: dict[str, object],
    service: ZoneService = _zone_service_dep
) -> ZoneModel:
    zone = await service.update_zone(zone_id, zone_data)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.delete("/{zone_id}")
async def delete_zone(
    zone_id: UUID,
    service: ZoneService = _zone_service_dep
) -> dict[str, str]:
    if not await service.delete_zone(zone_id):
        raise HTTPException(status_code=404, detail="Zone not found")
    return {"status": "success"}


@router.get("/type/{zone_type}", response_model=list[ZoneModel])
async def get_zones_by_type(
    zone_type: ZoneType,
    service: ZoneService = _zone_service_dep
) -> list[ZoneModel]:
    return await service.get_zones_by_type(zone_type)


@router.get("/point/{latitude}/{longitude}", response_model=list[ZoneModel])
async def get_zones_containing_point(
    latitude: float,
    longitude: float,
    service: ZoneService = _zone_service_dep
) -> list[ZoneModel]:
    return await service.get_zones_containing_point(latitude, longitude)
