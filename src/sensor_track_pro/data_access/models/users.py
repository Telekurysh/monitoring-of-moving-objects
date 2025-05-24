from __future__ import annotations

import uuid

from sqlalchemy import Boolean
from sqlalchemy import Enum  # добавить импорт Enum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.business_logic.models.user_model import UserRole
from src.sensor_track_pro.data_access.models.base import Base
from src.sensor_track_pro.data_access.models.user_objects import UserObject  # noqa: F401


class User(Base):
    """Модель пользователя."""

    @declared_attr.directive
    def __tablename__(self) -> str:
        return "users"

    # Используем UUID вместо str
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)  # исправлено имя типа
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Связи
    user_objects = relationship("UserObject", back_populates="user", cascade="all, delete-orphan")
    objects = relationship(
        "Object",
        secondary="userobject",
        back_populates="users",
        overlaps="user,user_objects,object_users"
    )
