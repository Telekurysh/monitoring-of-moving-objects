from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import or_  # добавлен импорт true, false и or_
from sqlalchemy import select  # добавлен импорт true, false и or_
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

    async def create(self, route_data: RouteBase) -> RouteModel:  # type: ignore[override]
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
        query = select(Route).filter(Route.status == RouteStatus.IN_PROGRESS).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [RouteModel.model_validate(r) for r in result.scalars().all()]

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
                or_(
                    Route.end_time.is_(None),  # заменено условие с использованием or_
                    Route.end_time <= end_time
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [RouteModel.model_validate(route) for route in result.scalars().all()]

    async def get_by_id(self, route_id: UUID) -> RouteModel | None:  # type: ignore[override]
        db_route = await super().get_by_id(route_id)
        return RouteModel.model_validate(db_route) if db_route else None

    async def get_all(self, skip: int = 0, limit: int = 100, **filters: dict[str, Any]) -> list[RouteModel]:  # type: ignore[override]
        db_list = await super().get_all(skip, limit, **filters)
        return [RouteModel.model_validate(r) for r in db_list]

    async def update(self, route_id: UUID, route_data: dict[str, Any]) -> RouteModel | None:  # type: ignore[override]
        db_route = await super().update(route_id, route_data)
        return RouteModel.model_validate(db_route) if db_route else None
