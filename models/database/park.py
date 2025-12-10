"""
Park ORM model.
"""
from sqlalchemy import (
    Column, String, Text, Numeric, DateTime, ForeignKey,
    CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from services.Database.PostgresConnection import Base
import uuid


class Park(Base):
    __tablename__ = "parks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(255), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    status = Column(
        String(50),
        default="pending",
        nullable=False,
        server_default="pending",
        index=True
    )
    submitted_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    submit_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    approved_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)
    admin_notes = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    submitter = relationship("User", foreign_keys=[submitted_by], backref="submitted_parks")
    approver = relationship("User", foreign_keys=[approved_by], backref="approved_parks")
    equipment = relationship(
        "ParkEquipment",
        back_populates="park",
        cascade="all, delete-orphan"
    )
    images = relationship("Image", back_populates="park", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="park", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="check_park_status"
        ),
        CheckConstraint(
            "latitude >= -90 AND latitude <= 90",
            name="parks_latitude_range"
        ),
        CheckConstraint(
            "longitude >= -180 AND longitude <= 180",
            name="parks_longitude_range"
        ),
        {"schema": None}  # Use default schema
    )

    def __repr__(self):
        return f"<Park(id={self.id}, name={self.name}, status={self.status})>"

