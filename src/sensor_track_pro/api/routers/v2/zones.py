from __future__ import annotations

from typing import AsyncGenerator
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Body
from fastapi import status
from fastapi import Response
from starlette.status import HTTP_204_NO_CONTENT


from src.sensor_track_pro.business_logic.models.zone_model import ZoneBase
from src.sensor_track_pro.business_logic.models.zone_model import ZoneModel
from src.sensor_track_pro.business_logic.models.zone_model import ZoneType
from pydantic import BaseModel
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


class ZonesResponse(BaseModel):
    items: list[ZoneModel]
    total: int | None = None


@router.get("/", response_model=ZonesResponse)
async def get_zones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    zone_type: ZoneType | None = Query(None),
    latitude: float | None = Query(None),
    longitude: float | None = Query(None),
    service: ZoneService = _zone_service_dep
) -> list[ZoneModel]:
    """
    Получить список зон.

    Параметры фильтрации (опциональные):
    - zone_type: вернуть зоны указанного типа
    - latitude и longitude: вернуть зоны, содержащие точку

    Приоритет фильтров: если заданы latitude и longitude, будет вызван `get_zones_containing_point`.
    Иначе, если задан zone_type, будет вызван `get_zones_by_type`.
    В противном случае возвращаются все зоны с пагинацией.
    """
    # фильтрация по точке имеет приоритет
    if latitude is not None and longitude is not None:
        items = await service.get_zones_containing_point(latitude, longitude)
        return ZonesResponse(items=items, total=len(items))

    if zone_type is not None:
        items = await service.get_zones_by_type(zone_type)
        return ZonesResponse(items=items, total=len(items))

    items = await service.get_zones(skip=skip, limit=limit)
    return ZonesResponse(items=items, total=len(items))


@router.put("/{zone_id}", response_model=ZoneModel)
async def update_zone(
    zone_id: UUID,
    zone_data: ZoneBase = Body(..., example={
        "name": "test",
        "zone_type": "rectangle",
        "coordinates": {
            "top_left": {
            "latitude": 55.83204746935401,
            "longitude": 37.43316650390626
            },
            "bottom_right": {
            "latitude": 55.71927914747206,
            "longitude": 37.81768798828126
            }
      },
      "description": "",
    }),
    service: ZoneService = _zone_service_dep
) -> ZoneModel:
    zone = await service.update_zone(zone_id, zone_data)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.delete("/{zone_id}", status_code=HTTP_204_NO_CONTENT, responses={404: {"description": "Alert not found"}})
async def delete_zone(
    zone_id: UUID,
    service: ZoneService = _zone_service_dep
) -> Response:
    if not await service.delete_zone(zone_id):
        raise HTTPException(status_code=404, detail="Zone not found")
    return Response(status_code=HTTP_204_NO_CONTENT)


# old routes for type and point are consolidated into the root GET / with query params


# @router.get("/map/all", response_model=list[ZoneModel])
# async def get_zones_for_map(
#     service: ZoneService = _zone_service_dep
# ) -> list[ZoneModel]:
#     return await service.get_zones_for_map()
