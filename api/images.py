"""
Image endpoint used by the frontend: list images for a park.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from services.Database import get_db, get_images_by_park
from models.responses.ImagesResponses import ImageResponse

router = APIRouter()


@router.get("/park/{park_id}", response_model=List[ImageResponse], tags=["Images"])
def get_images_for_park(
    park_id: UUID,
    is_approved: Optional[bool] = Query(None),
    is_primary: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all images for a park with optional filtering."""
    return get_images_by_park(
        db=db,
        park_id=park_id,
        is_approved=is_approved,
        is_primary=is_primary,
    )
