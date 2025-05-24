from __future__ import annotations

import uuid

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Enum  # добавьте импорт Enum

from src.sensor_track_pro.business_logic.models.alert_model import AlertType, AlertSeverity  # импортируйте Enum из бизнес-логики

from src.sensor_track_pro.data_access.models.base import Base


class Alert(Base):
    """Модель оповещения в базе данных."""
    @declared_attr.directive
    def __tablename__(self) -> str:
        return "alerts"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType, name="alert_type", create_constraint=False), nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity, name="alert_severity", create_constraint=False), nullable=False)
    message = Column(String(500), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    created_at = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Связи
    event = relationship("Event", back_populates="alerts")

    __table_args__ = (
        Index("idx_alert_event_type", "event_id", "alert_type"),
        Index("idx_alert_severity", "severity", "timestamp"),
    )
