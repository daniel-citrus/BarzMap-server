"""
Response models for authentication endpoints.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class AuthenticationResponse(BaseModel):
    """Response model for authentication operations."""
    user_id: UUID
    email: str
    name: str
    is_new_user: bool = False
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

