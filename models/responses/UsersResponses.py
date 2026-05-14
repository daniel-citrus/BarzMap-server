"""
Response models for users endpoints.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID


class UserResponse(BaseModel):
    """Response model for user data."""

    id: UUID
    auth0_id: str
    email: str
    name: str
    profile_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserLoginResponse(BaseModel):
    """User row fields plus Auth0 role ids (not stored on ``users``)."""

    id: UUID
    auth0_id: str
    email: str
    name: str
    profile_picture_url: Optional[str] = None
    roles: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
