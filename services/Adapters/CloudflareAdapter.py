"""
Cloudflare Images API adapter.

Provides a consistent interface for uploading images to Cloudflare Images.
Handles URL-based image uploads and error management.
"""

import os
import asyncio
import io
import httpx
from typing import List, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field
import logging

from models.requests.ParkSubmissionRequest import ImageSubmission

logger = logging.getLogger(__name__)

api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

if not api_token:
    logger.warning("CLOUDFLARE_API_TOKEN not set - Cloudflare operations may fail")
if not account_id:
    logger.warning("CLOUDFLARE_ACCOUNT_ID not set - Cloudflare operations may fail")


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

def _detect_image_type_and_extension(image_bytes: bytes) -> tuple[str, str]:
    """
    Detect image MIME type and file extension from file bytes.
    Returns (content_type, file_extension).
    Cloudflare only accepts: image/jpeg, image/png, image/webp, image/gif
    """
    # Check magic numbers (file signatures)
    if image_bytes.startswith(b'\xff\xd8\xff'):
        return ('image/jpeg', '.jpg')
    if image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return ('image/png', '.png')
    if image_bytes.startswith(b'GIF87a') or image_bytes.startswith(b'GIF89a'):
        return ('image/gif', '.gif')
    if image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:12]:
        return ('image/webp', '.webp')
    if image_bytes.startswith(b'<svg') or image_bytes.startswith(b'<?xml'):
        raise ValueError("SVG images are not supported. Please use JPEG, PNG, WebP, or GIF.")
    
    logger.warning("Could not detect image type from magic numbers, defaulting to JPEG")
    return ('image/jpeg', '.jpg')


def _create_error_result(index: int, error_type: str, message: str) -> SingleImageUploadResult:
    """Helper to create an error result."""
    return SingleImageUploadResult(
        uploaded_image=None,
        error=ImageUploadError(index=index, error=error_type, message=message)
    )


def _extract_error_message(response: dict) -> str:
    """Extract error message from Cloudflare API response."""
    errors = response.get("errors", [])
    return errors[0].get("message", "Unknown error") if errors else "Unknown error"


async def upload_single_image(index: int, image: ImageSubmission) -> SingleImageUploadResult:
    """Upload a single image to Cloudflare."""
    try:
        if not image.file_data:
            raise ValueError("file_data is empty")
        
        content_type, file_ext = _detect_image_type_and_extension(image.file_data)
        logger.debug(f"Uploading image {index + 1} to Cloudflare (size: {len(image.file_data)} bytes, type: {content_type})")
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1"
        files = {"file": (f"image{file_ext}", io.BytesIO(image.file_data), content_type)}
        
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                url,
                headers={"Authorization": f"Bearer {api_token}"},
                files=files,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
        
        # Validate and extract result
        if not result.get("success"):
            raise ValueError(f"Cloudflare API error: {_extract_error_message(result)}")
        
        uploaded_dict = result.get("result")
        if not uploaded_dict or "id" not in uploaded_dict:
            raise ValueError(f"Invalid Cloudflare response: missing result or id field")
        
        logger.debug(f"Successfully uploaded image {index + 1}: {uploaded_dict.get('id')}")
        return SingleImageUploadResult(
            uploaded_image=UploadedImage(**uploaded_dict),
            error=None
        )
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error uploading image {index + 1}: {e}")
        try:
            error_response = e.response.json()
            message = _extract_error_message(error_response)
        except:
            message = str(e)
        return _create_error_result(index, "HTTP error", message)
    
    except ValueError as e:
        logger.warning(f"Invalid image data at index {index + 1}: {e}")
        return _create_error_result(index, "Invalid input", str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error uploading image {index + 1}: {e}", exc_info=True)
        return _create_error_result(index, "Unexpected error", str(e))


async def upload_images(images: List[ImageSubmission]) -> List[UploadedImage]:
    """Upload multiple images to Cloudflare Images API."""
    if not images:
        raise HTTPException(status_code=400, detail="No images provided for upload")

    if not api_token or not account_id:
        raise HTTPException(
            status_code=503,
            detail="Image upload service unavailable - missing configuration"
        )

    results = await asyncio.gather(*[
        upload_single_image(index, image) for index, image in enumerate(images)
    ])

    uploaded_images = [r.uploaded_image for r in results if r.uploaded_image]
    failed_uploads = [r.error.model_dump() for r in results if r.error]

    if not uploaded_images and failed_uploads:
        raise HTTPException(
            status_code=500,
            detail={"message": "All image uploads failed", "failures": failed_uploads}
        )

    if failed_uploads:
        logger.warning(f"Partial upload success: {len(uploaded_images)} succeeded, {len(failed_uploads)} failed")

    return uploaded_images
