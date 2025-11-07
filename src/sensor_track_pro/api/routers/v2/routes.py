from __future__ import annotations

from datetime import datetime
from uuid import UUID
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Body
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response
from starlette.status import HTTP_204_NO_CONTENT

from src.sensor_track_pro.business_logic.models.route_model import RouteBase
from src.sensor_track_pro.business_logic.models.route_model import RouteModel
from src.sensor_track_pro.business_logic.models.route_model import RouteStatus
from src.sensor_track_pro.business_logic.services.route_service import RouteService
from src.sensor_track_pro.data_access.database import get_async_db
from src.sensor_track_pro.data_access.repositories.routes_repo import RouteRepository


router = APIRouter()

_db_dep = Depends(get_async_db)


def get_route_service(session: AsyncSession = _db_dep) -> RouteService:
    return RouteService(RouteRepository(session))


_route_service_dep = Depends(get_route_service)


@router.post("/", response_model=RouteModel)
async def create_route(
    route_data: RouteBase,
    service: RouteService = _route_service_dep
) -> RouteModel:
    return await service.create_route(route_data)


@router.get("/{route_id}", response_model=RouteModel)
async def get_route(
    route_id: UUID,
    service: RouteService = _route_service_dep
) -> RouteModel:
    route = await service.get_route(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.get("/", response_model=list[RouteModel])
async def get_routes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    status: RouteStatus | None = Query(None),
    object_id: UUID | None = Query(None),
    active: bool | None = Query(None),
    start_time: Optional[datetime] = Query(None, description="Start time in ISO format"),
    end_time: Optional[datetime] = Query(None, description="End time in ISO format"),
    service: RouteService = _route_service_dep
) -> list[RouteModel]:
    """
    Получить маршруты с опциональной фильтрацией.

    Приоритет фильтров:
    1. timerange (start_time и/или end_time)
    2. active (если active=true вернёт активные маршруты)
    3. object_id
    4. status
    5. иначе — общий список с пагинацией
    """
    # timerange имеет наивысший приоритет
    if start_time is not None or end_time is not None:
        return await service.get_routes_by_timerange(start_time, end_time)

    if active:
        return await service.get_active_routes()

    if object_id is not None:
        return await service.get_routes_by_object(object_id)

    if status is not None:
        return await service.get_routes_by_status(status)

    return await service.get_routes(skip=skip, limit=limit)


@router.put("/{route_id}", response_model=RouteModel)
async def update_route(
    route_id: UUID,
    route_data: RouteBase = Body(..., example={
        "object_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "start_time": "2025-10-11T09:46:20.994Z",
        "end_time": "2025-10-11T09:46:20.994Z",
        "status": "planned",
        "name": "string",
        "description": "string",
        "points": [],
        "metadata": {},
    }),
    service: RouteService = _route_service_dep
) -> RouteModel:
    route = await service.update_route(route_id, route_data)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.delete("/{route_id}", status_code=HTTP_204_NO_CONTENT, responses={404: {"description": "Alert not found"}})
async def delete_route(
    route_id: UUID,
    service: RouteService = _route_service_dep
) -> Response:
    if not await service.delete_route(route_id):
        raise HTTPException(status_code=404, detail="Route not found")
    return Response(status_code=HTTP_204_NO_CONTENT)


# old specialized routes for status/object/active/timerange are consolidated into root GET /
