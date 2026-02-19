"""
Cloudflare Images API adapter.

Uploads images to Cloudflare Images and returns uploaded image data.
"""

import asyncio
import io
import logging
import os
from typing import List

import httpx
from fastapi import HTTPException

from models.requests.ParkSubmissionRequest import ImageSubmission
from models.responses.CloudflareImageResponses import (
    ImageUploadError,
    SingleImageUploadResult,
    UploadedImage,
)

logger = logging.getLogger(__name__)

api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

if not api_token:
    logger.warning("CLOUDFLARE_API_TOKEN not set - Cloudflare operations may fail")
if not account_id:
    logger.warning("CLOUDFLARE_ACCOUNT_ID not set - Cloudflare operations may fail")

def _content_type_and_ext(data: bytes) -> tuple[str, str]:
    """(content_type, file_extension). Uses file signature; defaults to JPEG if unknown."""
    if data.startswith(b"\xff\xd8\xff"):
        return ("image/jpeg", ".jpg")
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ("image/png", ".png")
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return ("image/gif", ".gif")
    if data.startswith(b"RIFF") and b"WEBP" in data[:12]:
        return ("image/webp", ".webp")
    if data.startswith(b"<svg") or data.startswith(b"<?xml"):
        raise ValueError("SVG not supported. Use JPEG, PNG, WebP, or GIF.")
    logger.warning("Unknown image type from bytes, defaulting to JPEG")
    return ("image/jpeg", ".jpg")


def _error_result(index: int, kind: str, message: str) -> SingleImageUploadResult:
    return SingleImageUploadResult(
        uploaded_image=None,
        error=ImageUploadError(index=index, error=kind, message=message),
    )


def _message_from_api_body(body: dict) -> str:
    errors = body.get("errors", [])
    if not errors:
        return "Unknown error"
    return errors[0].get("message", "Unknown error")


async def _post_image_to_cloudflare(
    file_data: bytes, content_type: str, file_ext: str
) -> dict:
    """POST image to Cloudflare; returns JSON body. Raises on HTTP or API failure."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1"
    files = {"file": (f"image{file_ext}", io.BytesIO(file_data), content_type)}
    headers = {"Authorization": f"Bearer {api_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    if not data.get("success"):
        raise ValueError(_message_from_api_body(data))
    result = data.get("result")
    if not result or "id" not in result:
        raise ValueError("Cloudflare response missing result or id")
    return result


async def upload_single_image(
    index: int, image: ImageSubmission
) -> SingleImageUploadResult:
    """Upload one image. Returns a result with either uploaded_image or error."""
    if not image.file_data:
        return _error_result(index, "Invalid input", "file_data is empty")

    try:
        content_type, file_ext = _content_type_and_ext(image.file_data)
        logger.debug("Uploading image %s (size=%s, type=%s)", index + 1, len(image.file_data), content_type)

        uploaded = await _post_image_to_cloudflare(
            image.file_data, content_type, file_ext
        )
        logger.debug("Uploaded image %s: %s", index + 1, uploaded.get("id"))
        return SingleImageUploadResult(
            uploaded_image=UploadedImage(**uploaded),
            error=None,
        )
    except httpx.HTTPStatusError as e:
        logger.error("HTTP error image %s: %s", index + 1, e)
        try:
            msg = _message_from_api_body(e.response.json())
        except Exception:
            msg = str(e)
        return _error_result(index, "HTTP error", msg)
    except ValueError as e:
        logger.warning("Invalid image %s: %s", index + 1, e)
        return _error_result(index, "Invalid input", str(e))
    except Exception as e:
        logger.error("Unexpected error image %s: %s", index + 1, e, exc_info=True)
        return _error_result(index, "Unexpected error", str(e))


async def upload_images(images: List[ImageSubmission]) -> List[UploadedImage]:
    """Upload many images in parallel. Returns only successful uploads. Fails if all fail."""
    if not images:
        raise HTTPException(status_code=400, detail="No images provided for upload")
    if not api_token or not account_id:
        raise HTTPException(
            status_code=503,
            detail="Image upload service unavailable - missing configuration",
        )

    tasks = [upload_single_image(i, img) for i, img in enumerate(images)]
    results = await asyncio.gather(*tasks)

    ok = [r.uploaded_image for r in results if r.uploaded_image]
    failures = [r.error.model_dump() for r in results if r.error]

    if not ok and failures:
        raise HTTPException(
            status_code=500,
            detail={"message": "All image uploads failed", "failures": failures},
        )
    if failures:
        logger.warning("Partial upload: %s ok, %s failed", len(ok), len(failures))

    return ok

