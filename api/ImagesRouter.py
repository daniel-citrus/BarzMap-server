"""
API routes for Images.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from services.Database import (
    get_db,
    create_image,
    get_image,
    get_images_by_park,
    get_primary_image,
    update_image,
    delete_image,
)
from models.requests.images import ImageResponse
from models.database import Image

router = APIRouter()


@router.post("/", response_model=ImageResponse, tags=["Images"])
def create_new_image(
    park_id: UUID,
    image_url: str,
    uploaded_by: Optional[UUID] = None,
    thumbnail_url: Optional[str] = None,
    alt_text: Optional[str] = None,
    is_approved: bool = False,
    is_primary: bool = False,
    is_inappropriate: bool = False,
    db: Session = Depends(get_db)
):
    """Create a new image."""
    return create_image(
        db=db,
        park_id=park_id,
        image_url=image_url,
        uploaded_by=uploaded_by,
        thumbnail_url=thumbnail_url,
        alt_text=alt_text,
        is_approved=is_approved,
        is_primary=is_primary,
        is_inappropriate=is_inappropriate,
    )


@router.get("/{image_id}", response_model=ImageResponse, tags=["Images"])
def get_image_by_id(
    image_id: UUID,
    db: Session = Depends(get_db)
):
    """Get an image by ID."""
    image = get_image(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


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


@router.get("/park/{park_id}/primary", response_model=ImageResponse, tags=["Images"])
def get_primary_image_for_park(
    park_id: UUID,
    db: Session = Depends(get_db)
):
    """Get the primary image for a park."""
    image = get_primary_image(db, park_id)
    if not image:
        raise HTTPException(status_code=404, detail="Primary image not found")
    return image


@router.put("/{image_id}", response_model=ImageResponse, tags=["Images"])
def update_image_by_id(
    image_id: UUID,
    image_url: Optional[str] = None,
    thumbnail_url: Optional[str] = None,
    alt_text: Optional[str] = None,
    is_approved: Optional[bool] = None,
    is_primary: Optional[bool] = None,
    is_inappropriate: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Update an image."""
    image = update_image(
        db=db,
        image_id=image_id,
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        alt_text=alt_text,
        is_approved=is_approved,
        is_primary=is_primary,
        is_inappropriate=is_inappropriate,
    )
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.delete("/{image_id}", tags=["Images"])
def delete_image_by_id(
    image_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an image."""
    success = delete_image(db, image_id)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}

