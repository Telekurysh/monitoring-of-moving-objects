from __future__ import annotations

import uuid

from sqlalchemy import Column  # добавлено
from sqlalchemy import Enum
from sqlalchemy import ForeignKey  # добавлено

# --- добавьте определение таблицы object_zone ---
from sqlalchemy import String
from sqlalchemy import Table  # добавлено
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.business_logic.models.object_model import ObjectType
from src.sensor_track_pro.data_access.models.base import Base


metadata = Base.metadata  # используем metadata из Base

object_zone = Table(
    "object_zone",
    metadata,
    Column("object_id", UUID(as_uuid=True), ForeignKey("objects.id", ondelete="CASCADE"), primary_key=True),
    Column("zone_id", UUID(as_uuid=True), ForeignKey("zones.id", ondelete="CASCADE"), primary_key=True),
)


class Object(Base):
    """Модель объекта мониторинга."""

    @declared_attr.directive
    def __tablename__(self) -> str:
        return "objects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Изменено: передаём параметр name в Enum, чтобы использовать существующий тип "object_type" в БД
    object_type: Mapped[ObjectType] = mapped_column("object_type", Enum(ObjectType, name="object_type"), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Связи с использованием строковых ссылок
    sensors = relationship("Sensor", back_populates="object", cascade="all, delete-orphan")
    telemetry = relationship("Telemetry", back_populates="object", cascade="all, delete-orphan")
    routes = relationship("Route", back_populates="object", cascade="all, delete-orphan")
    # Исправлено: используем Table object_zone
    zones = relationship("Zone", secondary=object_zone, back_populates="objects", overlaps="object_zones")
    object_users = relationship("UserObject", back_populates="object", cascade="all, delete-orphan")
    users = relationship(
        "User",
        secondary="userobject",
        back_populates="objects",
        overlaps="object_users,user,user_objects,object"
    )
