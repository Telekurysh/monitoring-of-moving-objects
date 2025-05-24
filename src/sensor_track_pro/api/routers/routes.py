from __future__ import annotations

from datetime import datetime
from uuid import UUID
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

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
    service: RouteService = _route_service_dep
) -> list[RouteModel]:
    return await service.get_routes(skip=skip, limit=limit)


@router.put("/{route_id}", response_model=RouteModel)
async def update_route(
    route_id: UUID,
    route_data: dict[str, object],
    service: RouteService = _route_service_dep
) -> RouteModel:
    route = await service.update_route(route_id, route_data)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.delete("/{route_id}")
async def delete_route(
    route_id: UUID,
    service: RouteService = _route_service_dep
) -> dict[str, str]:
    if not await service.delete_route(route_id):
        raise HTTPException(status_code=404, detail="Route not found")
    return {"status": "success"}


@router.get("/status/{status}", response_model=list[RouteModel])
async def get_routes_by_status(
    status: RouteStatus,
    service: RouteService = _route_service_dep
) -> list[RouteModel]:
    return await service.get_routes_by_status(status)


@router.get("/object/{object_id}", response_model=list[RouteModel])
async def get_routes_by_object(
    object_id: UUID,
    service: RouteService = _route_service_dep
) -> list[RouteModel]:
    return await service.get_routes_by_object(object_id)


@router.get("/active", response_model=list[RouteModel])
async def get_active_routes(
    service: RouteService = _route_service_dep
) -> list[RouteModel]:
    return await service.get_active_routes()


@router.get("/timerange", response_model=list[RouteModel])
async def get_routes_by_timerange(
    start_time: Optional[datetime] = Query(None, description="Start time in ISO format"),
    end_time: Optional[datetime] = Query(None, description="End time in ISO format"),
    service: RouteService = _route_service_dep
) -> list[RouteModel]:
    return await service.get_routes_by_timerange(start_time, end_time)
