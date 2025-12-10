"""
Image ORM model.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from services.Database.PostgresConnection import Base
import uuid


class Image(Base):
    __tablename__ = "images"

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
    uploaded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    image_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    alt_text = Column(String(255), nullable=True)
    is_approved = Column(Boolean, default=False, nullable=False, server_default="false", index=True)
    is_primary = Column(Boolean, default=False, nullable=False, server_default="false")
    is_inappropriate = Column(Boolean, default=False, nullable=False, server_default="false")
    upload_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    park = relationship("Park", back_populates="images")
    uploader = relationship("User", foreign_keys=[uploaded_by], backref="uploaded_images")

    __table_args__ = (
        # Unique constraint: only one primary image per park
        # This is a partial unique index created in the SQL schema
        # SQLAlchemy doesn't fully support partial unique indexes, so this is handled in the SQL file
    )

    def __repr__(self):
        return f"<Image(id={self.id}, park_id={self.park_id}, is_primary={self.is_primary})>"

