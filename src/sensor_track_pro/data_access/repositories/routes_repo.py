from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.interfaces.repository.irout_repo import IRouteRepository
from src.sensor_track_pro.business_logic.models.route_model import RouteBase
from src.sensor_track_pro.business_logic.models.route_model import RouteModel
from src.sensor_track_pro.business_logic.models.route_model import RouteStatus
from src.sensor_track_pro.data_access.models.routes import Route
from src.sensor_track_pro.data_access.repositories.base import BaseRepository


class RouteRepository(BaseRepository[Route], IRouteRepository):
    """Репозиторий для работы с маршрутами."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Route)

    async def create(self, route_data: RouteBase) -> RouteModel:
        """Создает новый маршрут."""
        db_route = Route(**route_data.model_dump())
        await super().create(db_route)
        return RouteModel.model_validate(db_route)

    async def get_by_object_id(
        self,
        object_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[RouteModel]:
        """Получает маршруты объекта."""
        query = select(Route).filter(Route.object_id == object_id).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [RouteModel.model_validate(route) for route in result.scalars().all()]

    async def get_by_status(
        self,
        status: RouteStatus,
        skip: int = 0,
        limit: int = 100
    ) -> list[RouteModel]:
        """Получает маршруты по статусу."""
        query = select(Route).filter(Route.status == status).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [RouteModel.model_validate(route) for route in result.scalars().all()]

    async def get_active_routes(self, skip: int = 0, limit: int = 100) -> list[RouteModel]:
        """Получает активные маршруты."""
        query = (
            select(Route)
            .filter(Route.status == RouteStatus.IN_PROGRESS)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [RouteModel.model_validate(route) for route in result.scalars().all()]

    async def get_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> list[RouteModel]:
        """Получает маршруты за временной период."""
        query = (
            select(Route)
            .filter(
                Route.start_time >= start_time,
                (Route.end_time <= end_time if Route.end_time else True)  # type: ignore[arg-type]
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [RouteModel.model_validate(route) for route in result.scalars().all()]
