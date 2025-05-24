from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class UserObject(Base):
    """Модель связи пользователя с объектом."""

    @declared_attr.directive
    def __tablename__(self) -> str:
        return "userobject"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)  # исправлено
    object_id = Column(UUID(as_uuid=True), ForeignKey("objects.id"), primary_key=True)
    access_level = Column(String(50), nullable=False)

    # Связи
    user = relationship("User", back_populates="user_objects")
    object = relationship("Object", back_populates="object_users")

    __table_args__ = (
        UniqueConstraint("user_id", "object_id"),
    )