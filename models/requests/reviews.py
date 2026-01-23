from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class ReviewCreate(BaseModel):
    park_id: UUID
    user_id: UUID
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = None
    is_approved: bool = True


class ReviewUpdate(BaseModel):
    id: UUID
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    is_approved: Optional[bool] = None

