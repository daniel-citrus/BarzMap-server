"""
API routes for Admin park submission moderation.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime
from services.Database import (
    get_db,
    get_park,
    get_park_submissions_paginated,
    moderate_park,
    delete_park,
    get_equipment_by_park,
    get_images_by_park,
)
from models.requests.admin import ModerationComment
from models.responses.AdminResponses import (
    ParkSubmissionsListResponse,
    ParkSubmissionItem,
    PaginationInfo,
    ParkSubmissionDetail,
)
from models.database import Park
import math

router = APIRouter()


def format_park_id(park_id: UUID) -> str:
    """Format park UUID as submission ID like 'SUB-10342'."""
    # Use first 8 characters of UUID (without dashes) for readable ID
    uuid_str = str(park_id).replace('-', '').upper()
    return f"SUB-{uuid_str[:8]}"


@router.get("/park-submissions", response_model=ParkSubmissionsListResponse, tags=["Admin"])
def get_park_submissions(
    status: str = Query("pending", description="Status filter: pending, approved, denied, or all"),
    search: Optional[str] = Query(None, description="Fuzzy search on title, submitter, or address"),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    pageSize: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of park submissions for admin dashboard.
    
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
            id=format_park_id(park.id),
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


@router.get("/park-submissions/{submission_id}", response_model=ParkSubmissionDetail, tags=["Admin"])
def get_park_submission_detail(
    submission_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed park submission for viewer.
    
    Matches FEDC specification for ParkSubmissionViewer.jsx component.
    """
    # Try to parse submission ID - for now, we'll search by matching pattern
    # In production, you might want a mapping table
    # For simplicity, we'll try to find by UUID if it's a valid UUID
    park = None
    
    # Try parsing as UUID first (in case frontend sends UUID directly)
    try:
        park_uuid = UUID(submission_id)
        park = get_park(db, park_uuid)
    except ValueError:
        # Not a valid UUID, try to find by matching ID pattern
        # This is a simplified approach - in production use a mapping
        if submission_id.startswith('SUB-'):
            # For now, we'll need to search all parks and match
            # This is inefficient but works for MVP
            from services.Database import get_all_parks
            all_parks = get_all_parks(db, skip=0, limit=10000)  # Large limit for search
            for p in all_parks:
                if format_park_id(p.id) == submission_id:
                    park = p
                    break
    
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
        id=format_park_id(park.id),
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


@router.post("/park-submissions/{submission_id}/approve", response_model=ParkSubmissionDetail, tags=["Admin"])
def approve_park_submission(
    submission_id: str,
    comment: ModerationComment = ModerationComment(),
    db: Session = Depends(get_db)
):
    """Approve a park submission."""
    park = _get_park_by_submission_id(db, submission_id)
    if not park:
        raise HTTPException(status_code=404, detail="Park submission not found")
    
    # Moderate park
    moderated_park = moderate_park(
        db=db,
        park_id=park.id,
        status='approved',
        admin_notes=comment.comment or "",
    )
    
    if not moderated_park:
        raise HTTPException(status_code=400, detail="Failed to approve park submission")
    
    # Return updated submission detail
    return _park_to_detail_response(db, moderated_park)


@router.post("/park-submissions/{submission_id}/deny", response_model=ParkSubmissionDetail, tags=["Admin"])
def deny_park_submission(
    submission_id: str,
    comment: ModerationComment = ModerationComment(),
    db: Session = Depends(get_db)
):
    """Deny a park submission."""
    park = _get_park_by_submission_id(db, submission_id)
    if not park:
        raise HTTPException(status_code=404, detail="Park submission not found")
    
    # Moderate park (use 'rejected' status)
    moderated_park = moderate_park(
        db=db,
        park_id=park.id,
        status='rejected',
        admin_notes=comment.comment or "",
    )
    
    if not moderated_park:
        raise HTTPException(status_code=400, detail="Failed to deny park submission")
    
    # Return updated submission detail
    return _park_to_detail_response(db, moderated_park)


@router.post("/park-submissions/{submission_id}/pending", response_model=ParkSubmissionDetail, tags=["Admin"])
def set_park_submission_pending(
    submission_id: str,
    comment: ModerationComment = ModerationComment(),
    db: Session = Depends(get_db)
):
    """Set a park submission back to pending status."""
    park = _get_park_by_submission_id(db, submission_id)
    if not park:
        raise HTTPException(status_code=404, detail="Park submission not found")
    
    # Moderate park
    moderated_park = moderate_park(
        db=db,
        park_id=park.id,
        status='pending',
        admin_notes=comment.comment or "",
    )
    
    if not moderated_park:
        raise HTTPException(status_code=400, detail="Failed to set park submission to pending")
    
    # Return updated submission detail
    return _park_to_detail_response(db, moderated_park)


@router.delete("/park-submissions/{submission_id}", status_code=204, tags=["Admin"])
def delete_park_submission(
    submission_id: str,
    db: Session = Depends(get_db)
):
    """Delete a park submission."""
    park = _get_park_by_submission_id(db, submission_id)
    if not park:
        raise HTTPException(status_code=404, detail="Park submission not found")
    
    success = delete_park(db, park.id)
    if not success:
        raise HTTPException(status_code=404, detail="Park submission not found")
    
    return None


def _get_park_by_submission_id(db: Session, submission_id: str) -> Optional[Park]:
    """Helper to get park by submission ID (handles both UUID and SUB- format)."""
    # Try parsing as UUID first
    try:
        park_uuid = UUID(submission_id)
        return get_park(db, park_uuid)
    except ValueError:
        # Not a valid UUID, search by matching ID pattern
        if submission_id.startswith('SUB-'):
            from services.Database import get_all_parks
            all_parks = get_all_parks(db, skip=0, limit=10000)
            for p in all_parks:
                if format_park_id(p.id) == submission_id:
                    return p
    return None


def _park_to_detail_response(db: Session, park: Park) -> ParkSubmissionDetail:
    """Helper to convert Park to ParkSubmissionDetail response."""
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
        id=format_park_id(park.id),
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
