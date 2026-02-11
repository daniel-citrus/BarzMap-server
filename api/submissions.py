"""
Park submission endpoint used by the frontend: submit a new park.
"""
from fastapi import APIRouter, Depends, File, Form, Request
from fastapi.datastructures import UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from services.Manager.ParkSubmissions import process_submission, parse_submission_form_data
from services.Database import get_db

router = APIRouter()


class ParkSubmissionResponse(BaseModel):
    """Response model for park submission."""
    message: str
    submitted: bool


@router.post("/", response_model=ParkSubmissionResponse, tags=["Submissions"])
async def submit_park(
    request: Request,
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
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"Request content-type: {request.headers.get('content-type', 'unknown')}")
    form_data = await request.form()
    logger.info(f"Form fields received: {list(form_data.keys())}")
    if 'images' in form_data:
        images_data = form_data.getlist('images')
        logger.info(f"Images field found: {len(images_data)} items, types: {[type(x).__name__ for x in images_data]}")
    else:
        logger.warning("No 'images' field found in form data. Available fields: " + ", ".join(form_data.keys()))

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

    return ParkSubmissionResponse(
        message="Park submission processed successfully",
        submitted=True
    )
