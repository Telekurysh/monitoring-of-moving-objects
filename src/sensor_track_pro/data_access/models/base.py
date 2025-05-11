from __future__ import annotations

import uuid

from datetime import UTC
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Автоматически определяет имя таблицы из имени класса."""
        return cls.__name__.lower()

    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)
