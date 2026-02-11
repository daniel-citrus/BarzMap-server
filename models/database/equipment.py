"""
Equipment ORM model.
"""
from sqlalchemy import Column, String, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db import Base
import uuid


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon_name = Column(String(100), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    parks = relationship(
        "ParkEquipment",
        back_populates="equipment",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Equipment(id={self.id}, name={self.name})>"

