from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class User(Base):
    """Модель пользователя."""

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String)  # добавлена аннотация для role
    is_active = Column(Boolean, default=True, nullable=False)

    # Связи
    objects = relationship("Object", secondary="userobject", back_populates="users")
