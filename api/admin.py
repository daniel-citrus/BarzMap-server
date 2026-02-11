"""
Admin park submission moderation endpoints.
RESTful: moderation is a PATCH on the submission resource with status in the body.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from services.Database import (
    get_db,
    get_park,
    moderate_park,
    delete_park,
)
from models.requests.admin import ModerateParkSubmissionRequest
from models.database import Park
from models.responses.AdminResponses import ParkSubmissionDetail

router = APIRouter()


@router.patch("/park-submissions/{park_id}", response_model=ParkSubmissionDetail, tags=["Admin"])
def moderate_park_submission(
    park_id: UUID,
    body: ModerateParkSubmissionRequest,
    db: Session = Depends(get_db),
):
    """
    Update park submission moderation status (approve, reject, or set pending).
    RESTful: single endpoint; action is expressed in the request payload.
    """
    park = get_park(db, park_id)
    if not park:
        raise HTTPException(status_code=404, detail="Park submission not found")

    moderated_park = moderate_park(
        db=db,
        park_id=park.id,
        status=body.status,
        admin_notes=(body.comment or "").strip(),
    )
    if not moderated_park:
        raise HTTPException(
            status_code=400,
            detail="Invalid status or failed to moderate park submission",
        )
    return _park_to_detail_response(db, moderated_park)


@router.delete("/park-submissions/{park_id}", status_code=204, tags=["Admin"])
def delete_park_submission(
    park_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a park submission."""
    park = get_park(db, park_id)
    if not park:
        raise HTTPException(status_code=404, detail="Park submission not found")

    success = delete_park(db, park.id)
    if not success:
        raise HTTPException(status_code=404, detail="Park submission not found")

    return None


def _park_to_detail_response(db: Session, park: Park) -> ParkSubmissionDetail:
    """Helper to convert Park to ParkSubmissionDetail response."""
    from services.Database import get_equipment_by_park, get_images_by_park

    equipment_list = get_equipment_by_park(db, park.id)
    equipment_names = [eq.name for eq in equipment_list]

    images_list = get_images_by_park(db, park.id)
    image_urls = [img.image_url for img in images_list if img.image_url]

    submitter_name = None
    if park.submitter:
        submitter_name = park.submitter.name

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
        status=park.status
    )
