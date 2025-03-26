# tests/unit/test_alert_service.py
from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import UUID
from uuid import uuid4

import pytest

from pydantic import ValidationError

from src.core.interfaces.alert_notifier import AlertRecipient
from src.core.interfaces.alert_notifier import AlertType
from src.core.interfaces.alert_notifier import IAlertNotifier
from src.core.interfaces.telemetry_repository import ITelemetryRepository
from src.core.interfaces.telemetry_repository import MetricType
from src.core.interfaces.telemetry_repository import TelemetryData
from src.core.interfaces.zone_repository import IZoneRepository
from src.core.services.alert_service import AlertRule
from src.core.services.alert_service import AlertService


@pytest.fixture
def mock_deps() -> tuple[AsyncMock, AsyncMock, AsyncMock]:
    zone_repo = AsyncMock(spec=IZoneRepository)
    telemetry_repo = AsyncMock(spec=ITelemetryRepository)
    notifier = AsyncMock(spec=IAlertNotifier)
    return zone_repo, telemetry_repo, notifier


@pytest.fixture
def sample_recipient() -> AlertRecipient:
    return AlertRecipient(
        id=uuid4(),
        name="Test Recipient",
        contact_method="email",
        contact_details="test@example.com"
    )


@pytest.fixture
def sample_telemetry() -> TelemetryData:
    return TelemetryData(
        object_id=uuid4(),
        metric_type=MetricType.TEMPERATURE,
        value=42.5,
        sensor_id=uuid4()
    )


@pytest.mark.asyncio
async def test_no_alerts_when_below_threshold(mock_deps: tuple[AsyncMock, AsyncMock, AsyncMock],
                                              sample_telemetry: TelemetryData) -> None:
    """Тест: отсутствие оповещений при нормальных значениях"""
    zone_repo, telemetry_repo, notifier = mock_deps

    service = AlertService(
        zone_repo,
        telemetry_repo,
        notifier,
        default_recipients=[]
    )

    # Правило с большим порогом
    await service.add_alert_rule(
        AlertRule(
            name="High Temp",
            metric_type=MetricType.TEMPERATURE,
            condition={"operator": ">", "value": 50}
        )
    )

    alerts = await service.process_telemetry(sample_telemetry)

    assert len(alerts) == 0
    notifier.send_alert.assert_not_awaited()


@pytest.mark.asyncio
async def test_alert_rule_management(mock_deps: tuple[AsyncMock, AsyncMock, AsyncMock]) -> None:
    """Тест: добавление и обновление правил"""
    zone_repo, telemetry_repo, notifier = mock_deps
    service = AlertService(zone_repo, telemetry_repo, notifier, [])

    # Добавление правила
    rule_id = await service.add_alert_rule(
        AlertRule(name="Test Rule", condition={"operator": ">", "value": 0})
    )
    assert isinstance(rule_id, UUID)
    assert len(service._alert_rules) == 1

    # Обновление правила
    success = await service.update_alert_rule(
        rule_id,
        {"condition": {"operator": "<", "value": 100}}
    )
    assert success is True
    assert service._alert_rules[rule_id].condition["operator"] == "<"


@pytest.mark.asyncio
async def test_metric_alert_generation(mock_deps: tuple[AsyncMock, AsyncMock, AsyncMock]) -> None:
    zone_repo, telemetry_repo, notifier = mock_deps
    service = AlertService(
        zone_repo,
        telemetry_repo,
        notifier,
        default_recipients=[]
    )

    rule = AlertRule(
        name="Test Rule",
        metric_type="temperature",
        condition={"operator": ">", "value": 40}
    )
    await service.add_alert_rule(rule)

    telemetry = TelemetryData(
        object_id=uuid4(),
        metric_type=MetricType.TEMPERATURE,
        value=42.5
    )

    alerts = await service.process_telemetry(telemetry)
    assert len(alerts) == 1
    assert alerts[0].type == AlertType.METRIC_THRESHOLD
    notifier.send_alert.assert_awaited_once()


def test_alert_rule_validation() -> None:
    with pytest.raises(ValidationError):
        AlertRule(
            name="Invalid",
            condition={"invalid": "data"}
        )
