from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator
from pydantic_core.core_schema import ValidationInfo
from typing_extensions import Literal


class AlertSeverity(StrEnum):
    """Уровни важности оповещения"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertType(StrEnum):
    """Типы оповещений"""
    ZONE_VIOLATION = "zone_violation"
    METRIC_THRESHOLD = "metric_threshold"
    DEVICE_OFFLINE = "device_offline"
    CUSTOM = "custom"


class AlertRecipient(BaseModel):
    """Модель получателя оповещения"""
    id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    contact_method: Literal["email", "sms", "push", "webhook"]
    contact_details: str
    is_active: bool = True

    @field_validator('contact_details')
    @classmethod
    def validate_contact_details(cls, v: str, info: ValidationInfo) -> str:
        method = info.data.get('contact_method')
        if method == "email" and "@" not in v:
            raise ValueError("Invalid email address")
        if method == "sms" and not v.isdigit():
            raise ValueError("Phone number must contain only digits")
        return v


class AlertPayload(BaseModel):
    """Дополнительные данные оповещения"""
    object_id: UUID
    metric_type: str | None = None
    metric_value: float | None = None
    zone_id: UUID | None = None
    coordinates: dict[str, float] | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AlertMessage(BaseModel):
    """Основная модель оповещения"""
    model_config = ConfigDict(use_enum_values=True)

    id: UUID = Field(default_factory=uuid4)
    type: AlertType
    severity: AlertSeverity = AlertSeverity.MEDIUM
    title: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=10)
    payload: AlertPayload
    recipients: list[AlertRecipient]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_sent: bool = False

    @model_validator(mode='after')
    def validate_alert_content(self) -> AlertMessage:
        """Комплексная проверка содержания оповещения"""
        if self.type == AlertType.ZONE_VIOLATION and not self.payload.zone_id:
            raise ValueError("Zone alerts must have zone_id in payload")
        if self.type == AlertType.METRIC_THRESHOLD and not self.payload.metric_type:
            raise ValueError("Metric alerts must specify metric_type")
        return self


class NotificationResult(BaseModel):
    """Результат отправки оповещения"""
    alert_id: UUID
    recipient_id: UUID
    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error_message: str | None = None
    retry_count: int = 0


class IAlertNotifier(ABC):
    """Абстрактный сервис отправки оповещений"""

    @abstractmethod
    async def send_alert(self, alert: AlertMessage) -> list[NotificationResult]:
        """
        Отправить оповещение всем получателям
        :return: Список результатов отправки
        """
        raise NotImplementedError

    @abstractmethod
    async def get_alert_status(self, alert_id: UUID) -> list[NotificationResult]:
        """
        Получить статус доставки оповещения
        :return: Список статусов для каждого получателя
        """
        raise NotImplementedError

    @abstractmethod
    async def add_recipient(self, recipient: AlertRecipient) -> UUID:
        """
        Добавить нового получателя оповещений
        :return: ID созданного получателя
        """
        raise NotImplementedError

    @abstractmethod
    async def update_recipient(
            self,
            recipient_id: UUID,
            update_data: dict[str, Any]
    ) -> bool:
        """
        Обновить данные получателя
        :return: True если обновление прошло успешно
        """
        raise NotImplementedError
