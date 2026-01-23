"""
Response models for users endpoints.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserResponse(BaseModel):
    """Response model for user data."""
    id: UUID
    auth0_id: str
    email: str
    name: str
    profile_picture_url: Optional[str] = None
    role: str
    join_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

