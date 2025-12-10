from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class ImageCreate(BaseModel):
    park_id: UUID
    image_url: str
    uploaded_by: Optional[UUID] = None
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    is_approved: bool = False
    is_primary: bool = False
    is_inappropriate: bool = False


class ImageUpdate(BaseModel):
    id: UUID
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    is_approved: Optional[bool] = None
    is_primary: Optional[bool] = None
    is_inappropriate: Optional[bool] = None


class ImageResponse(BaseModel):
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

