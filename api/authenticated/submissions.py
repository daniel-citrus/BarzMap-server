"""
Authenticated park submission endpoints - require user authentication.
"""
from fastapi import APIRouter, Depends, Body, HTTPException, Query, File, Form
from fastapi.datastructures import UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
import math
import json
import base64
from models.requests.ParkSubmissionRequest import ParkSubmissionRequest, ImageSubmission
from services.Manager.ParkSubmissions import process_submission
from services.Database import (
    get_db,
    get_park,
    get_park_submissions_paginated,
    get_equipment_by_park,
    get_images_by_park,
)
from models.responses.AdminResponses import (
    ParkSubmissionsListResponse,
    ParkSubmissionItem,
    PaginationInfo,
    ParkSubmissionDetail,
)

router = APIRouter()


class ParkSubmissionResponse(BaseModel):
    """Response model for park submission."""
    message: str
    submitted: bool


@router.get("/park-submissions", response_model=ParkSubmissionsListResponse, tags=["Submissions"])
def get_park_submissions(
    status: str = Query("pending", description="Status filter: pending, approved, denied, or all"),
    search: Optional[str] = Query(None, description="Fuzzy search on title, submitter, or address"),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    pageSize: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of park submissions.
    
    Matches FEDC specification for ParkSubmissionAdminDashboard.jsx component.
    """
    # Validate status
    if status not in ['pending', 'approved', 'denied', 'rejected', 'all']:
        raise HTTPException(status_code=400, detail="Invalid status. Must be one of: pending, approved, denied, all")
    
    # Map 'denied' to 'rejected' for database
    if status == 'denied':
        status = 'rejected'
    
    # Get parks with pagination
    parks, total_count = get_park_submissions_paginated(
        db=db,
        status=status if status != 'all' else None,
        search=search,
        page=page,
        page_size=pageSize,
    )
    
    # Convert to response format
    submission_items = []
    for park in parks:
        # Get equipment names
        equipment_list = get_equipment_by_park(db, park.id)
        equipment_names = [eq.name for eq in equipment_list]
        
        # Get image URLs
        images_list = get_images_by_park(db, park.id)
        image_urls = [img.image_url for img in images_list if img.image_url]
        
        # Get submitter name
        submitter_name = None
        if park.submitter:
            submitter_name = park.submitter.name
        
        submission_items.append(ParkSubmissionItem(
            id=str(park.id),
            title=park.name,
            description=park.description,
            address=park.address,
            equipment=equipment_names,
            images=image_urls,
            submittedAt=park.submit_date,
            submitter=submitter_name,
            moderationComment=park.admin_notes or "",
            status=park.status
        ))
    
    # Calculate pagination info
    total_pages = math.ceil(total_count / pageSize) if total_count > 0 else 0
    
    return ParkSubmissionsListResponse(
        data=submission_items,
        pagination=PaginationInfo(
            page=page,
            pageSize=pageSize,
            totalPages=total_pages,
            totalItems=total_count
        )
    )


@router.get("/park-submissions/{park_id}", response_model=ParkSubmissionDetail, tags=["Submissions"])
def get_park_submission_detail(
    park_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get detailed park submission for viewer.
    
    Matches FEDC specification for ParkSubmissionViewer.jsx component.
    """
    park = get_park(db, park_id)
    if not park:
        raise HTTPException(status_code=404, detail="Park submission not found")
    
    # Get equipment names
    equipment_list = get_equipment_by_park(db, park.id)
    equipment_names = [eq.name for eq in equipment_list]
    
    # Get image URLs
    images_list = get_images_by_park(db, park.id)
    image_urls = [img.image_url for img in images_list if img.image_url]
    
    # Get submitter name
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


@router.post("/", response_model=ParkSubmissionResponse, tags=["Submissions"])
async def submit_park(
    name: str = Form(..., description="Name of the park"),
    description: Optional[str] = Form(None, description="Park description"),
    latitude: float = Form(..., description="Latitude coordinate"),
    longitude: float = Form(..., description="Longitude coordinate"),
    address: Optional[str] = Form(None, description="Full address display string"),
    submitted_by: Optional[str] = Form(None, description="User ID submitting the park (UUID as string)"),
    equipment_ids: Optional[str] = Form(None, description="JSON array of equipment IDs: [\"uuid1\", \"uuid2\"]"),
    images: List[UploadFile] = File(default=[], description="Image files to upload (max 5)"),
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
    # Validate image count
    if len(images) > 5:
        raise HTTPException(status_code=400, detail="Maximum of 5 images allowed per park submission")
    
    # Parse equipment_ids if provided
    equipment_ids_list = None
    if equipment_ids:
        try:
            equipment_ids_list = json.loads(equipment_ids)
            if not isinstance(equipment_ids_list, list):
                raise ValueError("equipment_ids must be a JSON array")
            # Convert to UUIDs
            equipment_ids_list = [UUID(eid) for eid in equipment_ids_list]
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid equipment_ids format: {str(e)}")
    
    # Parse submitted_by if provided
    submitted_by_uuid = None
    if submitted_by:
        try:
            submitted_by_uuid = UUID(submitted_by)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid submitted_by UUID format")
    
    # Parse image alt texts if provided
    alt_texts_list = []
    if image_alt_texts:
        try:
            alt_texts_list = json.loads(image_alt_texts)
            if not isinstance(alt_texts_list, list):
                raise ValueError("image_alt_texts must be a JSON array")
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid image_alt_texts format: {str(e)}")
    
    # Process images - read file data and create ImageSubmission objects
    image_submissions = []
    for idx, image_file in enumerate(images):
        # Read file content as bytes
        file_content = await image_file.read()
        
        # Convert bytes to base64 string for the ImageSubmission model
        file_data_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Get alt text for this image (if provided)
        alt_text = alt_texts_list[idx] if idx < len(alt_texts_list) else None
        
        image_submissions.append(ImageSubmission(
            file_data=file_data_base64,
            alt_text=alt_text
        ))
    
    # Create ParkSubmissionRequest from form data
    submission = ParkSubmissionRequest(
        name=name.strip() if name else name,
        description=description,
        latitude=latitude,
        longitude=longitude,
        address=address.strip() if address else address,
        submitted_by=submitted_by_uuid,
        equipment_ids=equipment_ids_list,
        images=image_submissions if image_submissions else None
    )
    
    # Process the submission
    submittedData = await process_submission(submission, db)
     
    return ParkSubmissionResponse(
        message="Park submission processed successfully",
        submitted=True
    )

