"""
Authenticated park submission endpoints - require user authentication.
"""
from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
import math
from models.requests.ParkSubmissionRequest import ParkSubmissionRequest
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
    submission: ParkSubmissionRequest = Body(
        ...,
        example={
            "name": "Washington Park",
            "description": "A small outdoor gym located next to the Washington Park lower baseball field.",
            "latitude": 40.785091,
            "longitude": -73.968285,
            "address": "Central Park, Upper East Side",
            "city": "Alameda",
            "state": "CA",
            "country": "USA",
            "postal_code": "94501",
            "submitted_by": None,
            "images": [
                {
                    "file_data": "",
                    "url": "https://i.pinimg.com/736x/ff/35/01/ff3501402d2b46257e8d104508323a53.jpg",
                    "alt_text": "Outdoor gym equipment at Central Park"
                },
                {
                    "file_data": "",
                    "url": "https://c4.wallpaperflare.com/wallpaper/635/923/784/anime-my-hero-academia-all-might-hd-wallpaper-preview.jpg",
                    "alt_text": "Park overview"
                },
                {
                    "file_data": "",
                    "url": "https://c4.wallpaperflare.com/wallpaper/635/923/784/anime-my-hero-academia-all-might-hd-wallpaper-preview.jpg",
                    "alt_text": "Park overvie2"
                }
            ],
            "equipment_ids": None
        }
    ),
    db: Session = Depends(get_db)
) -> ParkSubmissionResponse:
    """Submit a new park with images and equipment."""
    submittedData = await process_submission(submission, db)
    
    return ParkSubmissionResponse(
        message="Park submission processed successfully",
        submitted=True
    )

