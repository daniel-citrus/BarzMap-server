"""
Response models for reviews endpoints.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ReviewResponse(BaseModel):
    """Response model for review data."""
    id: UUID
    park_id: UUID
    user_id: UUID
    rating: int
    comment: Optional[str] = None
    is_approved: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

