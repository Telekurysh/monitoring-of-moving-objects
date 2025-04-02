from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.interfaces.repository.irout_repo import IRouteRepository
from src.sensor_track_pro.business_logic.models.common_types import FilterParams
from src.sensor_track_pro.business_logic.models.route_model import RouteBase
from src.sensor_track_pro.business_logic.models.route_model import RouteModel
from src.sensor_track_pro.business_logic.models.route_model import RouteStatus
from src.sensor_track_pro.business_logic.services.base_service import BaseService


class RouteService(BaseService[RouteModel]):
    def __init__(self, route_repository: IRouteRepository):
        super().__init__(route_repository)
        self._route_repository = route_repository

    async def create_route(self, route_data: RouteBase) -> RouteModel:
        return await self._route_repository.create(route_data)

    async def get_route(self, route_id: UUID) -> RouteModel | None:
        return await self._route_repository.get_by_id(route_id)

    async def get_routes(self, skip: int = 0, limit: int = 100, **filters: FilterParams) -> list[RouteModel]:
        return await self._route_repository.get_all(skip, limit, **filters)

    async def update_route(self, route_id: UUID, route_data: dict[str, Any]) -> RouteModel | None:
        return await self._route_repository.update(route_id, route_data)

    async def delete_route(self, route_id: UUID) -> bool:
        return await self._route_repository.delete(route_id)

    async def get_routes_by_object(self, object_id: UUID) -> list[RouteModel]:
        return await self._route_repository.get_by_object_id(object_id)

    async def get_routes_by_status(self, status: RouteStatus) -> list[RouteModel]:
        return await self._route_repository.get_by_status(status)

    async def get_active_routes(self) -> list[RouteModel]:
        return await self._route_repository.get_active_routes()

    async def get_routes_by_timerange(self, start_time: datetime, end_time: datetime) -> list[RouteModel]:
        return await self._route_repository.get_by_time_range(start_time, end_time)
