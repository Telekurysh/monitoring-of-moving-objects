from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import or_  # добавлен импорт true, false и or_
from sqlalchemy import select  # добавлен импорт true, false и or_
from sqlalchemy import insert
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
        data = route_data.model_dump(by_alias=True)
        # Корректно переименовываем metadata -> route_metadata
        if 'metadata' in data:
            data['route_metadata'] = data.pop('metadata')
        db_route = Route(**data)
        data_to_insert = {}
        for col in self._model.__table__.c:
            # Исключаем попадание ключа 'metadata' (MetaData) в insert
            if col.name == "metadata":
                value = getattr(db_route, "route_metadata", None)
            else:
                value = getattr(db_route, col.name, None)
            # Преобразуем Enum в строку для status
            if col.name == "status" and value is not None:
                value = str(value)
            # Удаляем таймзону у datetime перед вставкой
            if isinstance(value, datetime) and value.tzinfo is not None:
                value = value.replace(tzinfo=None)
            if col.name in {"id", "created_at", "updated_at"} and value is None:
                continue
            if value is not None:
                data_to_insert[col.name] = value
        # Удаляем лишний ключ 'metadata', если вдруг он есть
        data_to_insert.pop("metadata", None)
        stmt = insert(self._model).values(**data_to_insert)  # без .returning(...)
        result = await self._session.execute(stmt)
        await self._session.commit()
        pk_value = result.inserted_primary_key[0]
        instance = await self.get_by_id(pk_value)
        return RouteModel.model_validate(instance)

    async def get_by_object_id(
        self,
        object_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[RouteModel]:
        """Получает маршруты объекта."""
        query = select(Route).filter(Route.object_id == object_id).offset(skip).limit(limit)
        result = await self._session.execute(query)
        routes = result.scalars().all()
        route_models = []
        for route in routes:
            route_dict = route.__dict__.copy()
            if hasattr(route, "metadata"):
                if not isinstance(route.metadata, dict):
                    try:
                        route_dict["metadata"] = dict(route.metadata)
                    except Exception:
                        route_dict["metadata"] = {}
                else:
                    route_dict["metadata"] = route.metadata
            route_models.append(RouteModel.model_validate(route_dict))
        return route_models

    async def get_by_status(
        self,
        status: RouteStatus,
        skip: int = 0,
        limit: int = 100
    ) -> list[RouteModel]:
        """Получает маршруты по статусу."""
        query = select(Route).filter(Route.status == status).offset(skip).limit(limit)
        result = await self._session.execute(query)
        routes = result.scalars().all()
        route_models = []
        for route in routes:
            route_dict = route.__dict__.copy()
            if hasattr(route, "metadata"):
                # Преобразуем metadata к dict, если это не dict
                if not isinstance(route.metadata, dict):
                    try:
                        route_dict["metadata"] = dict(route.metadata)
                    except Exception:
                        route_dict["metadata"] = {}
                else:
                    route_dict["metadata"] = route.metadata
            route_models.append(RouteModel.model_validate(route_dict))
        return route_models

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
        # Исправление: если есть поле 'metadata', заменить его на route_metadata
        if db_route:
            # Принудительно подставляем route_metadata в alias metadata для Pydantic
            data = dict(db_route.__dict__)
            if "route_metadata" in data:
                data["metadata"] = data["route_metadata"]
            return RouteModel.model_validate(data)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100, **filters: dict[str, Any]) -> list[RouteModel]:  # type: ignore[override]
        db_list = await super().get_all(skip, limit, **filters)
        result = []
        for r in db_list:
            data = dict(r.__dict__)
            if "route_metadata" in data:
                data["metadata"] = data["route_metadata"]
            result.append(RouteModel.model_validate(data))
        return result

    async def update(self, route_id: UUID, route_data: dict[str, Any]) -> RouteModel | None:  # type: ignore[override]
        db_route = await super().update(route_id, route_data)
        if db_route:
            data = dict(db_route.__dict__)
            if "route_metadata" in data:
                data["metadata"] = data["route_metadata"]
            return RouteModel.model_validate(data)
        return None
