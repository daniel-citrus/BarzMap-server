"""
Cloudflare Images API adapter.

Provides a consistent interface for uploading images to Cloudflare Images.
Handles URL-based image uploads and error management.
"""

import os
import asyncio
from cloudflare import AsyncCloudflare
from typing import List, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field
import logging

try:
    from cloudflare import APIError

    CloudflareAPIError = APIError
except (ImportError, AttributeError):
    # Fallback if cloudflare library doesn't export exceptions
    CloudflareAPIError = Exception

from models.requests.ParkSubmissionRequest import ImageSubmission

logger = logging.getLogger(__name__)

api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

if not api_token:
    logger.warning("CLOUDFLARE_API_TOKEN not set - Cloudflare operations may fail")
if not account_id:
    logger.warning("CLOUDFLARE_ACCOUNT_ID not set - Cloudflare operations may fail")

try:
    client = AsyncCloudflare(api_token=api_token) if api_token else None
except Exception as e:
    logger.error(f"Failed to initialize Cloudflare client: {e}")
    client = None


class UploadedImage(BaseModel):
    """Model representing an uploaded image from Cloudflare."""

    id: str
    filename: str | None = None
    variants: List[str] | None = None

    class Config:
        extra = "allow"


class ImageUploadError(BaseModel):
    """Model representing an error that occurred during image upload."""
    
    index: int = Field(..., description="Index of the image that failed to upload")
    error: str = Field(..., description="Type of error that occurred")
    message: str = Field(..., description="Detailed error message")


class SingleImageUploadResult(BaseModel):
    """Result of uploading a single image to Cloudflare."""
    
    uploaded_image: Optional[UploadedImage] = Field(
        None, 
        description="The uploaded image if upload was successful"
    )
    error: Optional[ImageUploadError] = Field(
        None,
        description="Error information if upload failed"
    )

async def upload_single_image(index: int, image: ImageSubmission) -> SingleImageUploadResult:
    """Upload a single image to Cloudflare."""
    try:
        uploaded = await client.images.v1.create(
            account_id=account_id,
            # file=image.file_data,  # Reserved for future file upload support
            url=image.url,
        )

        uploaded_dict = (
            uploaded if isinstance(uploaded, dict) else uploaded.__dict__
        )
        return SingleImageUploadResult(
            uploaded_image=UploadedImage(**uploaded_dict),
            error=None
        )
    except CloudflareAPIError as e:
        error_msg = f"Cloudflare API error uploading image {index + 1}: {str(e)}"
        logger.error(error_msg)
        return SingleImageUploadResult(
            uploaded_image=None,
            error=ImageUploadError(
                index=index,
                error="API error",
                message=str(e)
            )
        )
    except ValueError as e:
        error_msg = f"Invalid image data at index {index + 1}: {str(e)}"
        logger.warning(error_msg)
        return SingleImageUploadResult(
            uploaded_image=None,
            error=ImageUploadError(
                index=index,
                error="Invalid input",
                message=str(e)
            )
        )
    except Exception as e:
        error_msg = f"Unexpected error uploading image {index + 1}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return SingleImageUploadResult(
            uploaded_image=None,
            error=ImageUploadError(
                index=index,
                error="Unexpected error",
                message=str(e)
            )
        )


async def upload_images(images: List[ImageSubmission]) -> List[UploadedImage]:
    """
    Upload multiple images to Cloudflare Images API via raw data or URL.
    """
    if not images:
        raise HTTPException(status_code=400, detail="No images provided for upload")

    if not client:
        logger.error("Cloudflare client not initialized - missing API token")
        raise HTTPException(
            status_code=503,
            detail="Image upload service unavailable - missing configuration",
        )

    if not account_id:
        logger.error("Cloudflare account ID not configured")
        raise HTTPException(
            status_code=503,
            detail="Image upload service unavailable - missing account ID",
        )

    uploaded_images = []
    failed_uploads = []

    upload_tasks = [
        upload_single_image(index, image) for index, image in enumerate(images)
    ]
    results = await asyncio.gather(*upload_tasks)

    for result in results:
        if result.uploaded_image:
            uploaded_images.append(result.uploaded_image)
        elif result.error:
            failed_uploads.append(result.error.model_dump())

    if not uploaded_images and failed_uploads:
        raise HTTPException(
            status_code=500,
            detail={"message": "All image uploads failed", "failures": failed_uploads},
        )

    if failed_uploads:
        logger.warning(
            f"Partial upload success: {len(uploaded_images)} succeeded, "
            f"{len(failed_uploads)} failed"
        )

    return uploaded_images
