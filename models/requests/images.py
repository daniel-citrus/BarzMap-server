from pydantic import BaseModel
from typing import Optional
from uuid import UUID


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

