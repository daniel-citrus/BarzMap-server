"""
Review ORM model.
"""
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from services.Database.connection import Base
import uuid


class Review(Base):
    __tablename__ = "reviews"

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
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=True, nullable=False, server_default="true")
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
    park = relationship("Park", back_populates="reviews")
    user = relationship("User", foreign_keys=[user_id], backref="reviews")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
        UniqueConstraint("park_id", "user_id", name="uq_park_user_review"),
    )

    def __repr__(self):
        return f"<Review(id={self.id}, park_id={self.park_id}, user_id={self.user_id}, rating={self.rating})>"

