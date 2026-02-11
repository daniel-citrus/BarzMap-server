"""
Event ORM model.
"""
from sqlalchemy import (
    Column, String, Text, Numeric, DateTime, ForeignKey, Date, Time
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db import Base
import uuid


class Event(Base):
    __tablename__ = "events"

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
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    host = Column(String(255), nullable=True)
    event_date = Column(Date, nullable=True)
    event_time = Column(Time, nullable=True)
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
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
    park = relationship("Park", backref="events")
    creator = relationship("User", foreign_keys=[created_by], backref="created_events")

    def __repr__(self):
        return f"<Event(id={self.id}, name={self.name}, park_id={self.park_id})>"
