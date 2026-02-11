"""
User ORM model.
"""
from sqlalchemy import Column, String, Boolean, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.db import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )
    auth0_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    profile_picture_url = Column(String, nullable=True)
    role = Column(
        String(50),
        default="user",
        nullable=False,
        server_default="user"
    )
    join_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False, server_default="true")
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

    __table_args__ = (
        CheckConstraint("role IN ('user', 'moderator', 'admin')", name="check_role"),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"

