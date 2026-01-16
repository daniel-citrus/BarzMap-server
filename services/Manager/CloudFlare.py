import os
import asyncio
from cloudflare import AsyncCloudflare
from typing import List
from fastapi import HTTPException
from pydantic import BaseModel
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
    logger.warning("CLOUDFLARE_API_TOKEN not set - CloudFlare operations may fail")
if not account_id:
    logger.warning("CLOUDFLARE_ACCOUNT_ID not set - CloudFlare operations may fail")

try:
    client = AsyncCloudflare(api_token=api_token) if api_token else None
except Exception as e:
    logger.error(f"Failed to initialize Cloudflare client: {e}")
    client = None


class UploadedImage(BaseModel):
    id: str
    filename: str | None = None
    variants: List[str] | None = None
    
    class Config:
        extra = "allow"


async def upload_images(images: List[ImageSubmission]) -> List[UploadedImage]:
    if not images:
        raise HTTPException(
            status_code=400, 
            detail="No images provided for upload"
        )
    
    if not client:
        logger.error("Cloudflare client not initialized - missing API token")
        raise HTTPException(
            status_code=503, 
            detail="Image upload service unavailable - missing configuration"
        )
    
    if not account_id:
        logger.error("Cloudflare account ID not configured")
        raise HTTPException(
            status_code=503,
            detail="Image upload service unavailable - missing account ID"
        )
    
    uploaded_images = []
    failed_uploads = []

    async def upload_single_image(index: int, image: ImageSubmission):
        try:
            uploaded = await client.images.v1.create(
                account_id,
                file=image.file_data
            )
            uploaded_dict = uploaded if isinstance(uploaded, dict) else uploaded.__dict__
            return UploadedImage(**uploaded_dict), None
        except CloudflareAPIError as e:
            error_msg = f"Cloudflare API error uploading image {index + 1}: {str(e)}"
            logger.error(error_msg)
            return None, {"index": index, "error": "API error", "message": str(e)}
        except ValueError as e:
            error_msg = f"Invalid image data at index {index + 1}: {str(e)}"
            logger.warning(error_msg)
            return None, {"index": index, "error": "Invalid input", "message": str(e)}
        except Exception as e:
            error_msg = f"Unexpected error uploading image {index + 1}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None, {"index": index, "error": "Unexpected error", "message": str(e)}

    upload_tasks = [upload_single_image(index, image) for index, image in enumerate(images)]
    results = await asyncio.gather(*upload_tasks)

    for uploaded, error in results:
        if uploaded:
            uploaded_images.append(uploaded)
        elif error:
            failed_uploads.append(error)
    
    if not uploaded_images and failed_uploads:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "All image uploads failed",
                "failures": failed_uploads
            }
        )
    
    if failed_uploads:
        logger.warning(
            f"Partial upload success: {len(uploaded_images)} succeeded, "
            f"{len(failed_uploads)} failed"
        )
    
    return uploaded_images
