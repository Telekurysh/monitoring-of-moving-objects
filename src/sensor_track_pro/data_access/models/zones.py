from __future__ import annotations

from typing import Any  # добавлен импорт
from uuid import uuid4

from geoalchemy2 import Geometry
from sqlalchemy import JSON
from sqlalchemy import Enum
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.sensor_track_pro.business_logic.models.zone_model import ZoneType
from src.sensor_track_pro.data_access.models.base import Base


class Zone(Base):
    """Модель зоны мониторинга."""

    __tablename__ = "zone"  # type: ignore

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    zone_type: Mapped[ZoneType] = mapped_column(Enum(ZoneType), nullable=False)
    coordinates: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)  # исправлено any -> Any
    description: Mapped[str | None] = mapped_column(String(500))
    boundary_polygon: Mapped[str] = mapped_column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    center_point: Mapped[str | None] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
