"""
Response models for images endpoints.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class ImageResponse(BaseModel):
    """Response model for image data."""
    id: UUID
    park_id: UUID
    uploaded_by: Optional[UUID] = None
    image_url: str
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    is_approved: bool
    is_primary: bool
    is_inappropriate: bool
    upload_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

