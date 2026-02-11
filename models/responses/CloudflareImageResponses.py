"""
Response/DTO models for Cloudflare Images API (upload results).
"""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class UploadedImage(BaseModel):
    """Model representing an uploaded image from Cloudflare."""

    id: str
    filename: str | None = None
    variants: List[str] | None = None

    model_config = ConfigDict(extra="allow")


class ImageUploadError(BaseModel):
    """Model representing an error that occurred during image upload."""

    index: int = Field(..., description="Index of the image that failed to upload")
    error: str = Field(..., description="Type of error that occurred")
    message: str = Field(..., description="Detailed error message")


class SingleImageUploadResult(BaseModel):
    """Result of uploading a single image to Cloudflare."""

    uploaded_image: Optional[UploadedImage] = Field(
        None,
        description="The uploaded image if upload was successful",
    )
    error: Optional[ImageUploadError] = Field(
        None,
        description="Error information if upload failed",
    )
