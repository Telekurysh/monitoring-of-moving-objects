from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class Alert(Base):
    """Модель оповещения в базе данных."""

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    event_id = Column(String(36), ForeignKey("event.id"), nullable=False)
    alert_type: Mapped[str] = mapped_column(String)  # аннотация для alert_type
    severity: Mapped[str] = mapped_column(String)    # аннотация для severity
    message = Column(String(500), nullable=False)
    timestamp = Column(DateTime, nullable=False)

    # Связи
    event = relationship("Event", back_populates="alerts")

    __table_args__ = (
        Index("idx_alert_event_type", "event_id", "alert_type"),
        Index("idx_alert_severity", "severity", "timestamp"),
    )
