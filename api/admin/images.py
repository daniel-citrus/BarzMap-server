"""
Admin API routes for Images - require admin authentication.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from services.Database import (
    get_db,
    update_image,
    delete_image,
)
from models.requests.images import ImageUpdate
from models.responses.ImagesResponses import ImageResponse

router = APIRouter()


@router.put("/{image_id}", response_model=ImageResponse, tags=["Admin - Images"])
def update_image_by_id(
    image_id: UUID,
    image_data: ImageUpdate,
    db: Session = Depends(get_db)
):
    """Update an image."""
    image = update_image(
        db=db,
        image_id=image_id,
        image_url=image_data.image_url,
        thumbnail_url=image_data.thumbnail_url,
        alt_text=image_data.alt_text,
        is_approved=image_data.is_approved,
        is_primary=image_data.is_primary,
        is_inappropriate=image_data.is_inappropriate,
    )
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.delete("/{image_id}", tags=["Admin - Images"])
def delete_image_by_id(
    image_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an image."""
    success = delete_image(db, image_id)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}

