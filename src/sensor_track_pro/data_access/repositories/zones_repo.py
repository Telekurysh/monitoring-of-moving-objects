from __future__ import annotations

from typing import Any
from uuid import UUID

from geoalchemy2.functions import ST_Contains
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def create(self, zone_data: ZoneBase) -> ZoneModel:  # type: ignore[override]
        """Создает новую зону."""
        db_zone = Zone(**zone_data.model_dump())
        # Преобразуем координаты в геометрию для PostgreSQL
        db_zone.boundary_polygon = self._coordinates_to_geometry(zone_data.coordinates)
        instance = await super().create(db_zone)
        return ZoneModel.model_validate(instance)

    async def get_by_type(self, zone_type: ZoneType, skip: int = 0, limit: int = 100) -> list[ZoneModel]:
        """Получает зоны по типу."""
        query = select(Zone).filter(Zone.zone_type == zone_type).offset(skip).limit(limit)
        result = await self._session.execute(query)
        return [ZoneModel.model_validate(zone) for zone in result.scalars().all()]

    async def get_zones_containing_point(self, latitude: float, longitude: float) -> list[ZoneModel]:
        """Получает зоны, содержащие точку."""
        point = f'SRID=4326;POINT({longitude} {latitude})'
        query = select(Zone).filter(ST_Contains(Zone.boundary_polygon, point))
        result = await self._session.execute(query)
        return [ZoneModel.model_validate(zone) for zone in result.scalars().all()]

    async def get_zones_for_object(self, object_id: UUID) -> list[ZoneModel]:
        """Получает зоны для объекта."""
        query = (
            select(Zone)
            .join(Zone.objects)  # type: ignore[attr-defined]
            .filter(Zone.objects.any(id=str(object_id)))  # type: ignore[attr-defined]
        )
        result = await self._session.execute(query)
        return [ZoneModel.model_validate(zone) for zone in result.scalars().all()]

    def _coordinates_to_geometry(self, coordinates: Any) -> str:
        """Преобразует координаты в WKT-формат для PostgreSQL."""
        zone_type = coordinates.get("type", "polygon")
        if zone_type == "polygon":
            points = coordinates.get("points")
            if not points or len(points) < MIN_POLYGON_POINTS:
                raise ValueError(f"Для полигона требуется минимум {MIN_POLYGON_POINTS} точки")
            # Закрываем полигон, если первая и последняя точка не совпадают
            if points[0] != points[-1]:
                points.append(points[0])
            points_str = ", ".join(f"{x} {y}" for x, y in points)
            return f"POLYGON(({points_str}))"
        if zone_type == "circle":
            center = coordinates.get("center")
            radius = coordinates.get("radius")
            if not center or radius is None:
                raise ValueError("Для круга требуются центр и радиус")
            import math
            points = []
            for i in range(32):
                angle = 2 * math.pi * i / 32
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.append(f"{x} {y}")
            points.append(points[0])
            points_str = ", ".join(points)
            return f"POLYGON(({points_str}))"
        raise ValueError(f"Неизвестный тип зоны: {zone_type}")
