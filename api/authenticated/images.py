"""
Authenticated image endpoints - require user authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, File
from fastapi.datastructures import UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from services.Database import (
    get_db,
    create_image,
    get_image,
    get_images_by_park,
    get_primary_image,
)
from models.requests.images import ImageCreate
from models.requests.ParkSubmissionRequest import ImageSubmission
from models.responses.ImagesResponses import ImageResponse
from services.Adapters.CloudflareAdapter import upload_single_image, SingleImageUploadResult

router = APIRouter()


@router.post("/", response_model=ImageResponse, tags=["Images"])
def create_new_image(
    image_data: ImageCreate,
    db: Session = Depends(get_db)
):
    """Create a new image."""
    return create_image(
        db=db,
        park_id=image_data.park_id,
        image_url=image_data.image_url,
        uploaded_by=image_data.uploaded_by,
        thumbnail_url=image_data.thumbnail_url,
        alt_text=image_data.alt_text,
        is_approved=image_data.is_approved,
        is_primary=image_data.is_primary,
        is_inappropriate=image_data.is_inappropriate,
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


@router.post("/test-submit", response_model=SingleImageUploadResult, tags=["Images"])
async def test_submit_image(
    image: UploadFile = File(..., description="Image file to upload to Cloudflare"),
    alt_text: Optional[str] = None,
) -> SingleImageUploadResult:
    """
    Test endpoint to upload a single image directly to Cloudflare.
    
    This endpoint is for testing the Cloudflare image upload functionality.
    It accepts a single image file and uploads it to Cloudflare Images API.
    """
    # Read file content as bytes
    file_content = await image.read()
    
    # Create ImageSubmission object
    image_submission = ImageSubmission(
        file_data=file_content,
        alt_text=alt_text
    )
    
    # Upload to Cloudflare using the adapter
    result = await upload_single_image(index=0, image=image_submission)
    
    return result

