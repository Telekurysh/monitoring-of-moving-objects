from __future__ import annotations

import uuid

from typing import Any  # добавлен импорт

from geoalchemy2 import Geometry
from sqlalchemy import JSON
from sqlalchemy import Enum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.sensor_track_pro.business_logic.models.zone_model import ZoneType
from src.sensor_track_pro.data_access.models.base import Base


class Zone(Base):
    """Модель зоны мониторинга."""

    __tablename__ = "zone"  # type: ignore

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    zone_type: Mapped[ZoneType] = mapped_column(Enum(ZoneType), nullable=False)
    coordinates: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)  # исправлено any -> Any
    description: Mapped[str | None] = mapped_column(String(500))
    boundary_polygon: Mapped[str] = mapped_column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    center_point: Mapped[str | None] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
