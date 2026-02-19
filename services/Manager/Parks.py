"""
Park list, location, moderation, and delete business logic.
"""
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.database import Park
from models.requests.admin import ModerateParkSubmissionRequest
from models.requests.parks import ModerateParkRequest
from models.responses.AdminResponses import ParkSubmissionDetail
from models.responses.ParksResponses import ParkResponse
from services.Database import (
    get_park,
    get_all_parks,
    get_parks_by_location,
    moderate_park,
    delete_park,
    get_equipment_by_park,
    get_images_by_park,
)
from services.Adapters.CloudflareAdapter import delete_image as cloudflare_delete_image
from services.Manager.Images import get_images_for_park

def get_parks_list(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
) -> list[ParkResponse]:
    """Get all parks with optional filtering."""
    return get_all_parks(db, skip=skip, limit=limit, status=status)

def get_parks_in_location(
    db: Session,
    min_latitude: float,
    max_latitude: float,
    min_longitude: float,
    max_longitude: float,
    status: str | None = "approved",
) -> list[ParkResponse]:
    """Get parks within a geographic bounding box."""
    return get_parks_by_location(
        db=db,
        min_latitude=Decimal(str(min_latitude)),
        max_latitude=Decimal(str(max_latitude)),
        min_longitude=Decimal(str(min_longitude)),
        max_longitude=Decimal(str(max_longitude)),
        status=status,
    )

def park_to_submission_detail(db: Session, park: Park) -> ParkSubmissionDetail:
    """Convert Park to ParkSubmissionDetail response."""
    equipment_list = get_equipment_by_park(db, park.id)
    equipment_names = [eq.name for eq in equipment_list]
    images_list = get_images_by_park(db, park.id)
    image_urls = [img.image_url for img in images_list if img.image_url]
    submitter_name = park.submitter.name if park.submitter else None
    return ParkSubmissionDetail(
        id=str(park.id),
        title=park.name,
        parkName=park.name,
        description=park.description,
        parkDescription=park.description,
        address=park.address,
        parkAddress=park.address,
        equipment=equipment_names,
        images=image_urls,
        submittedAt=park.submit_date,
        date=park.submit_date,
        submitter=submitter_name,
        user=submitter_name,
        moderationComment=park.admin_notes or "",
        status=park.status,
    )

def moderate_park_submission(
    park_id: UUID,
    body: ModerateParkSubmissionRequest,
    db: Session,
) -> ParkSubmissionDetail:
    """Update park moderation status. Raises HTTPException on not found or invalid."""
    park = get_park(db, park_id)
    if not park:
        raise HTTPException(status_code=404, detail="Park submission not found")
    request = ModerateParkRequest(
        status=body.status,
        admin_notes=(body.comment or "").strip(),
    )
    moderated_park = moderate_park(db=db, park_id=park.id, request=request)
    if not moderated_park:
        raise HTTPException(
            status_code=400,
            detail="Invalid status or failed to moderate park submission",
        )
    return park_to_submission_detail(db, moderated_park)

def _cloudflare_image_id_from_url(url: str) -> str | None:
    """Extract Cloudflare image ID from imagedelivery.net URL (format: .../account_hash/image_id/variant)."""
    if "imagedelivery.net" not in url:
        return None
    parts = url.rstrip("/").split("/")
    if len(parts) >= 5:
        return parts[4]
    return None


async def delete_park_submission(park_id: UUID, db: Session) -> None:
    """Delete a park submission. Raises HTTPException on not found."""
    park = get_park(db, park_id)
    
    if not park:
        raise HTTPException(status_code=404, detail="Park submission not found")

    images = get_images_for_park(db, park_id)

    for img in images:
        cf_id = _cloudflare_image_id_from_url(img.image_url)
        if cf_id:
            try:
                await cloudflare_delete_image(cf_id)
            except Exception:
                pass  # Log but continue; park/image will be deleted from DB anyway

    success = delete_park(db, park.id)

    if not success:
        raise HTTPException(status_code=404, detail="Park submission not found")


