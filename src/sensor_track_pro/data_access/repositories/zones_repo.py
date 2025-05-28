from __future__ import annotations

from typing import Any
from uuid import UUID

from geoalchemy2.functions import ST_Contains
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func  # добавлено

from src.sensor_track_pro.business_logic.interfaces.repository.izone_repo import IZoneRepository
from src.sensor_track_pro.business_logic.models.zone_model import MIN_POLYGON_POINTS
from src.sensor_track_pro.business_logic.models.zone_model import ZoneBase
from src.sensor_track_pro.business_logic.models.zone_model import ZoneModel
from src.sensor_track_pro.business_logic.models.zone_model import ZoneType
from src.sensor_track_pro.data_access.models.zones import Zone
from src.sensor_track_pro.data_access.repositories.base import BaseRepository


class ZoneRepository(BaseRepository[Zone], IZoneRepository):  # type: ignore[misc]
    """Репозиторий для работы с зонами."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Zone)

    async def create_zone(self, zone_data: ZoneBase) -> ZoneModel:
        """Создает новую зону из ZoneBase по аналогии с create из user_repo."""
        db_zone = Zone(**zone_data.model_dump())
        # Приводим значение zone_type к Enum ZoneType (оставляем только Enum)
        if not isinstance(db_zone.zone_type, ZoneType):
            db_zone.zone_type = ZoneType(db_zone.zone_type)
        db_zone.zone_type = db_zone.zone_type.value  # всегда нижний регистр для БД
        db_zone.boundary_polygon = self._coordinates_to_geometry(zone_data.coordinates)
        # Используем метод create из BaseRepository
        zone = await super().create(db_zone)
        return ZoneModel.model_validate(zone)

    async def get_by_type(self, zone_type: ZoneType, skip: int = 0, limit: int = 100) -> list[ZoneModel]:
        """Получает зоны по типу."""
        query = select(Zone).filter(Zone.zone_type == zone_type).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [ZoneModel.model_validate(zone) for zone in result.scalars().all()]

    async def get_zones_containing_point(self, latitude: float, longitude: float) -> list[ZoneModel]:
        """Получает зоны, содержащие точку."""
        # Используем ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) для создания точки
        point_geom = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
        query = select(Zone).filter(func.ST_Contains(Zone.boundary_polygon, point_geom))
        result = await self._session.execute(query)
        return [ZoneModel.model_validate(zone) for zone in result.scalars().all()]

    async def get_zones_for_object(self, object_id: UUID) -> list[ZoneModel]:
        """Получает зоны для объекта."""
        query = (
            select(Zone)
            .join(Zone.objects)
            .filter(Zone.objects.any(id=str(object_id)))
        )
        result = await self._session.execute(query)
        return [ZoneModel.model_validate(zone) for zone in result.scalars().all()]

    async def get_all_for_map(self) -> list[ZoneModel]:
        """Получить все зоны для карты."""
        query = select(Zone)
        result = await self._session.execute(query)
        return [ZoneModel.model_validate(zone) for zone in result.scalars().all()]

    def _coordinates_to_geometry(self, coordinates: Any) -> str:
        """Преобразует координаты в WKT-формат для PostgreSQL."""
        # coordinates - это Pydantic-модель: CircleZone, RectangleZone или PolygoneZone
        from src.sensor_track_pro.business_logic.models.zone_model import CircleZone, RectangleZone, PolygoneZone, MIN_POLYGON_POINTS

        if isinstance(coordinates, PolygoneZone):
            points = coordinates.points
            if not points or len(points) < MIN_POLYGON_POINTS:
                raise ValueError(f"Для полигона требуется минимум {MIN_POLYGON_POINTS} точки")
            # Закрываем полигон, если первая и последняя точка не совпадают
            if (points[0].latitude != points[-1].latitude) or (points[0].longitude != points[-1].longitude):
                points = points + [points[0]]
            points_str = ", ".join(f"{p.longitude} {p.latitude}" for p in points)
            return f"POLYGON(({points_str}))"
        elif isinstance(coordinates, CircleZone):
            center = coordinates.center
            radius = coordinates.radius
            if not center or radius is None:
                raise ValueError("Для круга требуются центр и радиус")
            import math
            points = []
            for i in range(32):
                angle = 2 * math.pi * i / 32
                x = center.longitude + radius * math.cos(angle)
                y = center.latitude + radius * math.sin(angle)
                points.append(f"{x} {y}")
            points.append(points[0])
            points_str = ", ".join(points)
            return f"POLYGON(({points_str}))"
        elif isinstance(coordinates, RectangleZone):
            # Прямоугольник задается двумя точками: top_left и bottom_right
            tl = coordinates.top_left
            br = coordinates.bottom_right
            tr = type(tl)(latitude=tl.latitude, longitude=br.longitude)
            bl = type(tl)(latitude=br.latitude, longitude=tl.longitude)
            points = [tl, tr, br, bl, tl]
            points_str = ", ".join(f"{p.longitude} {p.latitude}" for p in points)
            return f"POLYGON(({points_str}))"
        else:
            raise ValueError(f"Неизвестный тип зоны: {type(coordinates)}")
