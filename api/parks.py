from fastapi import APIRouter, Depends, File, Form, Query
from fastapi.datastructures import UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from models.requests.admin import ModerateParkSubmissionRequest
from models.responses.AdminResponses import ParkSubmissionDetail
from models.responses.ParksResponses import ParkResponse
from services.Database import get_db
from services.Manager.ParkSubmissions import process_submission, parse_submission_form_data
from services.Manager.Parks import (
    get_parks_list,
    get_parks_in_location,
    moderate_park_submission as manager_moderate_park_submission,
    delete_park_submission as manager_delete_park_submission,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class ParkSubmissionResponse(BaseModel):
    """Response model for park submission."""
    message: str
    submitted: bool


@router.get("/", response_model=List[ParkResponse], tags=["Parks"])
def get_parks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, regex="^(pending|approved|rejected)$", description="Filter by park status"),
    db: Session = Depends(get_db)
):
    """Get all parks with optional filtering."""
    return get_parks_list(db, skip=skip, limit=limit, status=status)


@router.get("/location", response_model=List[ParkResponse], tags=["Parks"])
def get_parks_in_location_endpoint(
    min_latitude: float = Query(..., description="Minimum latitude"),
    max_latitude: float = Query(..., description="Maximum latitude"),
    min_longitude: float = Query(..., description="Minimum longitude"),
    max_longitude: float = Query(..., description="Maximum longitude"),
    status: Optional[str] = Query("approved", regex="^(pending|approved|rejected)$", description="Filter by park status"),
    db: Session = Depends(get_db)
):
    """Get parks within a geographic bounding box."""
    return get_parks_in_location(
        db,
        min_latitude=min_latitude,
        max_latitude=max_latitude,
        min_longitude=min_longitude,
        max_longitude=max_longitude,
        status=status,
    )


@router.post("/", response_model=ParkSubmissionResponse, tags=["Parks"])
async def submit_park(
    name: str = Form(..., description="Name of the park"),
    description: Optional[str] = Form(None, description="Park description"),
    latitude: float = Form(..., description="Latitude coordinate"),
    longitude: float = Form(..., description="Longitude coordinate"),
    address: Optional[str] = Form(None, description="Full address display string"),
    submitted_by: Optional[str] = Form(None, description="User ID submitting the park (UUID as string)"),
    equipment_ids: Optional[str] = Form(None, description="JSON array of equipment IDs: [\"uuid1\", \"uuid2\"]"),
    images: List[UploadFile] = File(default=[], description="Image files to upload (max 5). Note: Swagger UI has limitations with multiple file uploads - use Postman or curl for testing."),
    image_alt_texts: Optional[str] = Form(None, description="JSON array of alt texts for images: [\"alt1\", \"alt2\"]"),
    db: Session = Depends(get_db)
) -> ParkSubmissionResponse:
    """
    Submit a new park with images and equipment.

    Accepts multipart/form-data with:
    - Form fields: name, description, latitude, longitude, address, submitted_by, equipment_ids, image_alt_texts
    - File fields: images (multiple files, max 5)

    equipment_ids should be a JSON string array: ["uuid1", "uuid2"]
    image_alt_texts should be a JSON string array: ["alt1", "alt2"] (optional, matches image order)
    """
    submission = await parse_submission_form_data(
        name=name,
        description=description,
        latitude=latitude,
        longitude=longitude,
        address=address,
        submitted_by=submitted_by,
        equipment_ids=equipment_ids,
        images=images if images else [],
        image_alt_texts=image_alt_texts,
    )
    await process_submission(submission, db)
    return ParkSubmissionResponse(message="Park submission processed successfully", submitted=True)


@router.patch("/{park_id}", response_model=ParkSubmissionDetail, tags=["Parks"])
def moderate_park_submission(
    park_id: UUID,
    body: ModerateParkSubmissionRequest,
    db: Session = Depends(get_db),
):
    """Update park moderation status (approve, reject, or set pending)."""
    return manager_moderate_park_submission(park_id, body, db)


@router.delete("/{park_id}", status_code=204, tags=["Parks"])
async def delete_park_submission(park_id: UUID, db: Session = Depends(get_db)):
    """Delete a park submission."""
    await manager_delete_park_submission(park_id, db)
    return None
