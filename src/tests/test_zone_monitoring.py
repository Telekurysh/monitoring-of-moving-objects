# tests/unit/test_zone_monitoring.py
from __future__ import annotations

from datetime import UTC
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from geopy.distance import geodesic  # type: ignore

from src.core.interfaces.telemetry_repository import PositionData
from src.core.interfaces.zone_repository import CircleCoordinates
from src.core.interfaces.zone_repository import RectangleCoordinates
from src.core.interfaces.zone_repository import ZoneBoundary
from src.core.interfaces.zone_repository import ZoneCreate
from src.core.interfaces.zone_repository import ZoneType
from src.core.services.zone_monitoring import ZoneMonitoringService
from src.core.services.zone_monitoring import ZoneViolation


# Регистрируем маркер asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_repos() -> tuple[AsyncMock, AsyncMock]:
    zone_repo = AsyncMock()
    telemetry_repo = AsyncMock()
    return zone_repo, telemetry_repo


@pytest.fixture
def sample_position() -> PositionData:
    return PositionData(
        object_id=uuid4(),
        latitude=55.7522,
        longitude=37.6156,
        timestamp=datetime.now(UTC)
    )


@pytest.fixture
def sample_circle_zone() -> ZoneBoundary:
    return ZoneBoundary(
        id=uuid4(),
        name="Test Circle Zone",
        type=ZoneType.CIRCLE,
        coordinates=CircleCoordinates(
            center=(55.7522, 37.6156),
            radius=100.0  # 100 метров
        )
    )


@pytest.fixture
def sample_rect_zone() -> ZoneBoundary:
    return ZoneBoundary(
        id=uuid4(),
        name="Test Rectangle Zone",
        type=ZoneType.RECTANGLE,
        coordinates=RectangleCoordinates(
            top_left=(55.7530, 37.6140),
            bottom_right=(55.7510, 37.6160)
        )
    )


@pytest.mark.asyncio
async def test_check_object_zones_no_position(mock_repos: tuple[AsyncMock, AsyncMock]) -> None:
    """Тест: нет данных о позиции -> пустой результат"""
    zone_repo, telemetry_repo = mock_repos
    telemetry_repo.get_latest_position.return_value = None

    service = ZoneMonitoringService(zone_repo, telemetry_repo)
    result = await service.check_object_zones(uuid4())

    assert len(result.violations) == 0
    assert result.checked_zones == 0
    telemetry_repo.get_latest_position.assert_awaited_once()


async def test_check_object_zones_no_zones(mock_repos: tuple[AsyncMock, AsyncMock],
                                           sample_position: PositionData) -> None:
    """Тест: нет зон для объекта -> пустой результат"""
    zone_repo, telemetry_repo = mock_repos
    telemetry_repo.get_latest_position.return_value = sample_position
    zone_repo.get_zones_for_object.return_value = []

    service = ZoneMonitoringService(zone_repo, telemetry_repo)
    result = await service.check_object_zones(sample_position.object_id)

    assert len(result.violations) == 0
    assert result.checked_zones == 0
    zone_repo.get_zones_for_object.assert_awaited_with(sample_position.object_id)


async def test_circle_zone_violation_detected(mock_repos: tuple[AsyncMock, AsyncMock], sample_position: PositionData,
                                              sample_circle_zone: ZoneBoundary) -> None:
    """Тест: обнаружено нарушение круговой зоны"""
    zone_repo, telemetry_repo = mock_repos
    telemetry_repo.get_latest_position.return_value = sample_position
    zone_repo.get_zones_for_object.return_value = [sample_circle_zone]

    # Позиция за пределами зоны (150м от центра при радиусе 100м)
    outside_position = PositionData(
        object_id=sample_position.object_id,
        latitude=55.7535,  # ~150м севернее
        longitude=37.6156,
        timestamp=datetime.now(UTC)
    )
    telemetry_repo.get_latest_position.return_value = outside_position

    service = ZoneMonitoringService(zone_repo, telemetry_repo)
    result = await service.check_object_zones(sample_position.object_id)

    assert len(result.violations) == 1
    violation = result.violations[0]
    assert violation.zone_id == sample_circle_zone.id
    assert violation.object_id == sample_position.object_id
    assert violation.distance > 0
    
    # Проверяем, что координаты круговые
    assert isinstance(sample_circle_zone.coordinates, CircleCoordinates)
    assert geodesic(
        (violation.exit_point[0], violation.exit_point[1]),
        sample_circle_zone.coordinates.center
    ).meters > sample_circle_zone.coordinates.radius


async def test_circle_zone_no_violation(mock_repos: tuple[AsyncMock, AsyncMock], sample_position: PositionData,
                                        sample_circle_zone: ZoneBoundary) -> None:
    """Тест: нет нарушения круговой зоны"""
    zone_repo, telemetry_repo = mock_repos
    telemetry_repo.get_latest_position.return_value = sample_position
    zone_repo.get_zones_for_object.return_value = [sample_circle_zone]

    service = ZoneMonitoringService(zone_repo, telemetry_repo)
    result = await service.check_object_zones(sample_position.object_id)

    assert len(result.violations) == 0
    assert result.checked_zones == 1


async def test_rectangle_zone_violation_detected(mock_repos: tuple[AsyncMock, AsyncMock], sample_position: PositionData,
                                                 sample_rect_zone: ZoneBoundary) -> None:
    """Тест: обнаружено нарушение прямоугольной зоны"""
    zone_repo, telemetry_repo = mock_repos
    zone_repo.get_zones_for_object.return_value = [sample_rect_zone]

    # Позиция за пределами прямоугольника
    outside_position = PositionData(
        object_id=sample_position.object_id,
        latitude=55.7540,  # Севернее верхней границы
        longitude=37.6150,
        timestamp=datetime.now(UTC)
    )
    telemetry_repo.get_latest_position.return_value = outside_position

    service = ZoneMonitoringService(zone_repo, telemetry_repo)
    result = await service.check_object_zones(sample_position.object_id)

    assert len(result.violations) == 1
    violation = result.violations[0]
    assert violation.zone_id == sample_rect_zone.id
    assert violation.object_id == sample_position.object_id
    assert violation.distance > 0


async def test_multiple_zones_check(mock_repos: tuple[AsyncMock, AsyncMock], sample_position: PositionData) -> None:
    """Тест: проверка нескольких зон"""
    zone_repo, telemetry_repo = mock_repos

    # Обновляем позицию объекта
    updated_position = PositionData(
        object_id=sample_position.object_id,
        latitude=55.7505,  # Внутри Zone 3 (55.7500 + 500m radius)
        longitude=37.6105,
        timestamp=datetime.now(UTC)
    )
    telemetry_repo.get_latest_position.return_value = updated_position

    zones = [
        # Zone 1: Объект внутри
        ZoneBoundary(
            id=uuid4(),
            name="Zone 1",
            type=ZoneType.CIRCLE,
            coordinates=CircleCoordinates(
                center=(55.7505, 37.6105),  # Центр рядом с объектом
                radius=1000.0  # Большой радиус
            )
        ),
        # Zone 2: Объект снаружи
        ZoneBoundary(
            id=uuid4(),
            name="Zone 2",
            type=ZoneType.RECTANGLE,
            coordinates=RectangleCoordinates(
                top_left=(55.7520, 37.6150),
                bottom_right=(55.7510, 37.6160)
            )
        ),
        # Zone 3: Объект внутри
        ZoneBoundary(
            id=uuid4(),
            name="Zone 3",
            type=ZoneType.CIRCLE,
            coordinates=CircleCoordinates(
                center=(55.7500, 37.6100),
                radius=500.0  # Объект внутри
            )
        )
    ]
    zone_repo.get_zones_for_object.return_value = zones

    service = ZoneMonitoringService(zone_repo, telemetry_repo)
    result = await service.check_object_zones(sample_position.object_id)

    expected_checked_zones = 3  # Константа для ожидаемого количества проверенных зон
    assert result.checked_zones == expected_checked_zones
    assert len(result.violations) == 1  # Нарушена только Zone 2
    assert result.violations[0].zone_id == zones[1].id  # Проверяем Zone 2


async def test_min_violation_distance(mock_repos: tuple[AsyncMock, AsyncMock], sample_position: PositionData,
                                      sample_circle_zone: ZoneBoundary) -> None:
    """Тест: игнорирование нарушений меньше минимального расстояния"""
    zone_repo, telemetry_repo = mock_repos
    zone_repo.get_zones_for_object.return_value = [sample_circle_zone]

    # Позиция чуть за границей зоны (~5м)
    slightly_outside = PositionData(
        object_id=sample_position.object_id,
        latitude=55.75225,  # ~5м севернее
        longitude=37.6156,
        timestamp=datetime.now(UTC)
    )
    telemetry_repo.get_latest_position.return_value = slightly_outside

    # Сервис с минимальным расстоянием срабатывания 10м
    service = ZoneMonitoringService(
        zone_repo,
        telemetry_repo,
        min_violation_distance=10.0
    )
    result = await service.check_object_zones(sample_position.object_id)

    assert len(result.violations) == 0  # Нарушение должно быть проигнорировано


def test_zone_violation_model_validation() -> None:
    """Тест валидации модели ZoneViolation"""
    with pytest.raises(ValueError):
        ZoneViolation(
            object_id=uuid4(),
            zone_id=uuid4(),
            exit_point=(55.7522, 37.6156),
            distance=-1.0  # Некорректное расстояние
        )

    expected_distance = 10.5  # Константа для ожидаемого расстояния
    valid_violation = ZoneViolation(
        object_id=uuid4(),
        zone_id=uuid4(),
        exit_point=(55.7522, 37.6156),
        distance=expected_distance
    )
    assert valid_violation.distance == expected_distance


@pytest.mark.asyncio
async def test_create_zone_with_invalid_coordinates(mock_repos: tuple[AsyncMock, AsyncMock]) -> None:
    """Тест: создание зоны с некорректными координатами"""
    zone_repo, telemetry_repo = mock_repos
    service = ZoneMonitoringService(zone_repo, telemetry_repo)

    invalid_zone = ZoneCreate(
        name="Invalid Zone",
        type=ZoneType.CIRCLE,
        coordinates=CircleCoordinates(center=(100, 200), radius=10)  # Некорректные координаты
    )

    with pytest.raises(ValueError):
        await service.create_zone(invalid_zone)
