from __future__ import annotations

from typing import Any
from uuid import UUID
from uuid import uuid4

from geopy.distance import geodesic  # type: ignore
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator

from src.core.interfaces.alert_notifier import AlertMessage
from src.core.interfaces.alert_notifier import AlertPayload
from src.core.interfaces.alert_notifier import AlertRecipient
from src.core.interfaces.alert_notifier import AlertSeverity
from src.core.interfaces.alert_notifier import AlertType
from src.core.interfaces.alert_notifier import IAlertNotifier
from src.core.interfaces.telemetry_repository import ITelemetryRepository
from src.core.interfaces.telemetry_repository import TelemetryData
from src.core.interfaces.zone_repository import CircleCoordinates
from src.core.interfaces.zone_repository import IZoneRepository
from src.core.interfaces.zone_repository import RectangleCoordinates
from src.core.interfaces.zone_repository import ZoneBoundary
from src.core.interfaces.zone_repository import ZoneType


class AlertRule(BaseModel):
    """Модель правила генерации оповещений"""
    model_config = ConfigDict(extra='forbid')

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=3, max_length=100)
    metric_type: str | None = None
    condition: dict[str, Any] = Field(...,
                                      description="Пример: {'operator': '>', 'value': 30}")
    severity: AlertSeverity = AlertSeverity.MEDIUM
    notification_channels: list[str] = Field(["email"], min_length=1)
    is_active: bool = True

    @field_validator('condition')
    @classmethod
    def validate_condition(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Валидация условия срабатывания"""
        if 'operator' not in v or 'value' not in v:
            raise ValueError("Condition must contain 'operator' and 'value'")
        return v

    @model_validator(mode='after')
    def validate_metric_type(self) -> AlertRule:
        """Проверка согласованности типа метрики"""
        if self.metric_type and not isinstance(self.metric_type, str):
            raise ValueError("Metric type must be a string")
        return self


class AlertService:
    """Сервис управления оповещениями"""

    def __init__(self, zone_repo: IZoneRepository, telemetry_repo: ITelemetryRepository, alert_notifier: IAlertNotifier,
                 default_recipients: list[AlertRecipient]):
        self._zone_repo = zone_repo
        self._telemetry_repo = telemetry_repo
        self._notifier = alert_notifier
        self._default_recipients = default_recipients
        self._alert_rules: dict[UUID, AlertRule] = {}

    async def process_telemetry(self, telemetry: TelemetryData) -> list[AlertMessage]:
        """Обработать новые данные телеметрии и сгенерировать оповещения"""
        alerts = []

        # Проверка метрик
        for rule in self._alert_rules.values():
            if self._check_rule(telemetry, rule):
                alerts.append(self._create_alert(telemetry, rule))

        # Отправка оповещений
        for alert in alerts:
            await self._notifier.send_alert(alert)
        return alerts

    def _check_rule(self, telemetry: TelemetryData, rule: AlertRule) -> bool:
        """Проверить срабатывание правила"""
        if rule.metric_type and telemetry.metric_type != rule.metric_type:
            return False
        return self._evaluate_condition(telemetry.value, rule.condition)

    @staticmethod
    def _evaluate_condition(value: float, condition: dict[str, Any]) -> bool:
        """Вычислить условие"""
        op = condition['operator']
        threshold = condition['value']

        return {
            '>': lambda: value > threshold,
            '<': lambda: value < threshold,
            '>=': lambda: value >= threshold,
            '<=': lambda: value <= threshold,
            '==': lambda: value == threshold
        }.get(op, lambda: False)()

    def _create_alert(self, telemetry: TelemetryData, rule: AlertRule) -> AlertMessage:
        """Создать оповещение"""
        return AlertMessage(
            type=AlertType.METRIC_THRESHOLD,
            severity=rule.severity,
            title=f"Alert: {telemetry.metric_type}",
            message=f"Value {telemetry.value} {rule.condition['operator']} {rule.condition['value']}",
            payload=AlertPayload(
                object_id=telemetry.object_id,
                metric_type=telemetry.metric_type,
                metric_value=telemetry.value
            ),
            recipients=self._default_recipients
        )

    async def _check_zone_violations(
            self,
            object_id: UUID,
            position: tuple[float, float]
    ) -> list[AlertMessage]:
        """Проверить нарушения геозон"""
        zones = await self._zone_repo.get_zones_for_object(object_id)
        alerts = []

        for zone in zones:
            if not self._is_in_zone(position, zone):
                alerts.append(self._create_zone_alert(object_id, position, zone))

        return alerts

    @staticmethod
    def _is_in_zone(position: tuple[float, float], zone: ZoneBoundary) -> bool:
        """Проверить нахождение в зоне (упрощенная реализация)"""
        if zone.type == ZoneType.CIRCLE:
            if not isinstance(zone.coordinates, CircleCoordinates):
                raise ValueError("Invalid coordinates for circle zone")
            center = zone.coordinates.center
            radius = zone.coordinates.radius
            return geodesic(center, position).meters <= radius
        if zone.type == ZoneType.RECTANGLE:
            if not isinstance(zone.coordinates, RectangleCoordinates):
                raise ValueError("Invalid coordinates for rectangle zone")
            # Реализация проверки прямоугольника
            return True
        return False

    def _create_zone_alert(
            self,
            object_id: UUID,
            position: tuple[float, float],
            zone: ZoneBoundary
    ) -> AlertMessage:
        """Создать оповещение о нарушении зоны"""
        return AlertMessage(
            type=AlertType.ZONE_VIOLATION,
            severity=AlertSeverity.HIGH,
            title="Нарушение геозоны",
            message=f"Объект вышел за границы зоны {zone.name}",
            payload=AlertPayload(
                object_id=object_id,
                zone_id=zone.id,
                coordinates={"latitude": position[0], "longitude": position[1]}
            ),
            recipients=self._default_recipients
        )

    async def add_alert_rule(self, rule: AlertRule) -> UUID:
        """Добавить правило"""
        self._alert_rules[rule.id] = rule
        return rule.id

    async def update_alert_rule(self, rule_id: UUID, updates: dict[str, Any]) -> bool:
        """Обновить правило"""
        if rule_id not in self._alert_rules:
            return False
        self._alert_rules[rule_id] = self._alert_rules[rule_id].model_copy(update=updates)
        return True

    def _get_recipients_for_rule(self, rule: AlertRule) -> list[AlertRecipient]:
        """Получить получателей для правила"""
        return self._default_recipients
