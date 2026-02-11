"""
ParkEquipment junction table ORM model.
"""
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db import Base
import uuid


class ParkEquipment(Base):
    __tablename__ = "park_equipment"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )
    park_id = Column(
        UUID(as_uuid=True),
        ForeignKey("parks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    equipment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("equipment.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    park = relationship("Park", back_populates="equipment")
    equipment = relationship("Equipment", back_populates="parks")

    __table_args__ = (
        UniqueConstraint("park_id", "equipment_id", name="uq_park_equipment"),
    )

    def __repr__(self):
        return f"<ParkEquipment(park_id={self.park_id}, equipment_id={self.equipment_id})>"

