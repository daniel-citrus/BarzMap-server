"""
Images-for-park business logic.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.responses.ImagesResponses import ImageResponse
from services.Database import get_images_by_park


def get_images_for_park(
    db: Session,
    park_id: UUID,
    is_approved: Optional[bool] = None,
    is_primary: Optional[bool] = None,
) -> list[ImageResponse]:
    """Get all images for a park with optional filtering."""
    return get_images_by_park(
        db=db,
        park_id=park_id,
        is_approved=is_approved,
        is_primary=is_primary,
    )
