from __future__ import annotations

from datetime import UTC
from datetime import datetime
from uuid import UUID

from geopy.distance import geodesic  # type: ignore
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator

from src.core.interfaces.telemetry_repository import ITelemetryRepository
from src.core.interfaces.telemetry_repository import PositionData
from src.core.interfaces.zone_repository import CircleCoordinates
from src.core.interfaces.zone_repository import IZoneRepository
from src.core.interfaces.zone_repository import RectangleCoordinates
from src.core.interfaces.zone_repository import ZoneBoundary
from src.core.interfaces.zone_repository import ZoneCreate
from src.core.interfaces.zone_repository import ZoneType
from src.core.interfaces.zone_repository import ZoneUpdate


class ZoneViolation(BaseModel):
    """Модель нарушения геозоны"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    object_id: UUID
    zone_id: UUID
    violation_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    exit_point: tuple[float, float]  # (latitude, longitude)
    distance: float  # Расстояние от границы в метрах

    @field_validator('distance')
    @classmethod
    def validate_distance(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Distance cannot be negative")
        return round(v, 2)


class ZoneMonitoringResult(BaseModel):
    """Результат проверки геозон"""
    violations: list[ZoneViolation] = Field(default_factory=list)
    checked_zones: int = 0
    checked_objects: int = 0


# Константы для проверки координат
MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180


class ZoneMonitoringService:
    """Полнофункциональный сервис управления геозонами"""

    def __init__(self, zone_repo: IZoneRepository, telemetry_repo: ITelemetryRepository,
                 min_violation_distance: float = 0.0):
        self._zone_repo = zone_repo
        self._telemetry_repo = telemetry_repo
        self._min_distance = min_violation_distance

    # CRUD операции
    async def create_zone(self, zone_data: ZoneCreate) -> ZoneBoundary:
        """
        Создать новую геозону
        :param zone_data: Данные для создания зоны
        :return: Созданная геозона
        """
        await self._validate_zone_coordinates(zone_data)
        return await self._zone_repo.create_zone(zone_data)

    async def update_zone(self, zone_id: UUID, update_data: ZoneUpdate) -> ZoneBoundary | None:
        """
        Обновить геозону
        :param zone_id: ID зоны для обновления
        :param update_data: Данные для обновления
        :return: Обновленная геозона или None если не найдена
        """
        if update_data.coordinates:
            update_data.id = zone_id  # Добавляем id для валидации
            await self._validate_zone_coordinates(update_data)
        return await self._zone_repo.update_zone(zone_id, update_data)

    async def delete_zone(self, zone_id: UUID) -> bool:
        """
        Удалить геозону
        :param zone_id: ID зоны для удаления
        :return: True если удаление успешно
        """
        return await self._zone_repo.delete_zone(zone_id)

    async def get_zone(self, zone_id: UUID) -> ZoneBoundary | None:
        """
        Получить геозону по ID
        :param zone_id: ID зоны
        :return: Геозона или None если не найдена
        """
        return await self._zone_repo.get_zone_by_id(zone_id)

    # Валидация геоданных
    async def _validate_zone_coordinates(self, zone_data: ZoneCreate | ZoneUpdate) -> None:
        """Проверка корректности координат зоны"""
        if isinstance(zone_data, ZoneCreate):
            zone_type = zone_data.type
            coords = zone_data.coordinates
        else:
            # Для ZoneUpdate предполагаем, что координаты уже проверены при создании
            if not zone_data.coordinates:
                return
            # Проверяем наличие ID зоны
            if zone_data.id is None:
                raise ValueError("Zone ID is required for update")
            # Получаем текущую зону для проверки типа
            existing_zone = await self._zone_repo.get_zone_by_id(zone_data.id)
            if not existing_zone:
                raise ValueError("Zone not found")
            zone_type = existing_zone.type
            coords = zone_data.coordinates

        if zone_type == ZoneType.CIRCLE:
            if not isinstance(coords, CircleCoordinates):
                raise ValueError("Invalid coordinates type for circle zone")
            if coords.radius <= 0:
                raise ValueError("Радиус зоны должен быть положительным")
            if not (MIN_LATITUDE <= coords.center[0] <= MAX_LATITUDE and MIN_LONGITUDE <= coords.center[
                1] <= MAX_LONGITUDE):
                raise ValueError("Некорректные координаты центра")
        elif zone_type == ZoneType.RECTANGLE:
            if not isinstance(coords, RectangleCoordinates):
                raise ValueError("Invalid coordinates type for rectangle zone")
            tl = coords.top_left
            br = coords.bottom_right
            if tl[0] < br[0] or tl[1] > br[1]:
                raise ValueError("Некорректные границы прямоугольной зоны")

    async def check_object_zones(self, object_id: UUID) -> ZoneMonitoringResult:
        """
        Проверить все геозоны для указанного объекта
        :return: Обнаруженные нарушения
        """
        result = ZoneMonitoringResult()
        position = await self._telemetry_repo.get_latest_position(object_id)

        if not position:
            return result

        zones = await self._zone_repo.get_zones_for_object(object_id)
        result.checked_zones = len(zones)
        result.checked_objects = 1

        for zone in zones:
            violation = await self._check_zone_violation(
                object_id,
                position,
                zone
            )
            if violation:
                result.violations.append(violation)

        return result

    async def _check_zone_violation(self, object_id: UUID, position: PositionData,
                                    zone: ZoneBoundary) -> ZoneViolation | None:
        """Проверить нарушение конкретной геозоны"""
        if zone.type == ZoneType.CIRCLE:
            return await self._check_circle_zone(
                object_id,
                position,
                zone
            )
        return await self._check_rectangle_zone(
            object_id,
            position,
            zone
        )

    @staticmethod
    async def _check_circle_zone(object_id: UUID, position: PositionData,
                                 zone: ZoneBoundary) -> ZoneViolation | None:
        """Проверить нарушение круговой геозоны"""
        if not isinstance(zone.coordinates, CircleCoordinates):
            return None

        center = zone.coordinates.center
        radius = zone.coordinates.radius

        current_point = (position.latitude, position.longitude)
        distance = geodesic(center, current_point).meters

        if distance > radius:
            return ZoneViolation(
                object_id=object_id,
                zone_id=zone.id,
                exit_point=current_point,
                distance=distance - radius
            )
        return None

    async def _check_rectangle_zone(self, object_id: UUID, position: PositionData,
                                    zone: ZoneBoundary) -> ZoneViolation | None:
        """Проверить нарушение прямоугольной геозоны"""
        if not isinstance(zone.coordinates, RectangleCoordinates):
            return None

        top_left = zone.coordinates.top_left
        bottom_right = zone.coordinates.bottom_right
        lat, lon = position.latitude, position.longitude

        # Проверка нахождения внутри прямоугольника
        is_inside = (
                (bottom_right[0] <= lat <= top_left[0]) and
                (top_left[1] <= lon <= bottom_right[1])
        )
        if is_inside:
            return None

        # Расчет расстояния до ближайшей границы
        distance = self._calculate_rect_distance(
            (lat, lon),
            top_left,
            bottom_right
        )

        if distance > self._min_distance:
            return ZoneViolation(
                object_id=object_id,
                zone_id=zone.id,
                exit_point=(lat, lon),
                distance=distance
            )
        return None

    @staticmethod
    def _calculate_rect_distance(
            point: tuple[float, float],
            top_left: tuple[float, float],
            bottom_right: tuple[float, float]
    ) -> float:
        """Вычислить расстояние от точки до прямоугольной зоны"""
        lat, lon = point
        min_lat, max_lon = top_left
        max_lat, min_lon = bottom_right

        if lat > max_lat:
            if lon < min_lon:  # Левый нижний угол
                return geodesic((max_lat, min_lon), point).meters
            if lon > max_lon:  # Правый нижний угол
                return geodesic((max_lat, max_lon), point).meters
            # Нижняя грань
            return geodesic((max_lat, lon), point).meters
        if lat < min_lat:
            if lon < min_lon:  # Левый верхний угол
                return geodesic((min_lat, min_lon), point).meters
            if lon > max_lon:  # Правый верхний угол
                return geodesic((min_lat, max_lon), point).meters
            # Верхняя грань
            return geodesic((min_lat, lon), point).meters
        if lon < min_lon:  # Левая грань
            return geodesic((lat, min_lon), point).meters
        # Правая грань
        return geodesic((lat, max_lon), point).meters
