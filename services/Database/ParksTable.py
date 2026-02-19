"""
CRUD operations for Parks table.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Tuple
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timezone
from models.database import Park
from models.requests.parks import ModerateParkRequest


def create_park(
    db: Session,
    name: str,
    latitude: Decimal,
    longitude: Decimal,
    description: Optional[str] = None,
    address: Optional[str] = None,
    submitted_by: Optional[UUID] = None,
    status: str = "pending",
) -> Park:
    """Create a new park."""
    park = Park(
        name=name,
        description=description,
        latitude=latitude,
        longitude=longitude,
        address=address,
        submitted_by=submitted_by,
        status=status,
    )
    db.add(park)
    db.commit()
    db.refresh(park)
    return park


def get_park(db: Session, park_id: UUID) -> Optional[Park]:
    """Get a park by ID."""
    return db.query(Park).filter(Park.id == park_id).first()


def get_all_parks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
) -> List[Park]:
    """Get all parks with optional filtering."""
    query = db.query(Park)
    if status:
        query = query.filter(Park.status == status)
    return query.offset(skip).limit(limit).all()


def get_parks_by_status(db: Session, status: str) -> List[Park]:
    """Get all parks by status."""
    return db.query(Park).filter(Park.status == status).all()


def get_parks_by_location(
    db: Session,
    min_latitude: Decimal,
    max_latitude: Decimal,
    min_longitude: Decimal,
    max_longitude: Decimal,
    status: Optional[str] = "approved",
) -> List[Park]:
    """Get parks within a geographic bounding box."""
    query = db.query(Park).filter(
        and_(
            Park.latitude >= min_latitude,
            Park.latitude <= max_latitude,
            Park.longitude >= min_longitude,
            Park.longitude <= max_longitude,
        )
    )
    if status:
        query = query.filter(Park.status == status)
    return query.all()


def update_park(
    db: Session,
    park_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    latitude: Optional[Decimal] = None,
    longitude: Optional[Decimal] = None,
    address: Optional[str] = None,
    status: Optional[str] = None,
    approved_by: Optional[UUID] = None,
    approved_at: Optional[datetime] = None,
    admin_notes: Optional[str] = None,
) -> Optional[Park]:
    """Update a park."""
    park = get_park(db, park_id)
    if not park:
        return None
    
    if name is not None:
        park.name = name
    if description is not None:
        park.description = description
    if latitude is not None:
        park.latitude = latitude
    if longitude is not None:
        park.longitude = longitude
    if address is not None:
        park.address = address
    if status is not None:
        park.status = status
    if approved_by is not None:
        park.approved_by = approved_by
    if approved_at is not None:
        park.approved_at = approved_at
    if admin_notes is not None:
        park.admin_notes = admin_notes
    
    db.commit()
    db.refresh(park)
    return park


def delete_park(db: Session, park_id: UUID) -> bool:
    """Delete a park."""
    park = get_park(db, park_id)
    if not park:
        return False
    
    db.delete(park)
    db.commit()
    return True


def get_park_submissions_paginated(
    db: Session,
    status: Optional[str] = "pending",
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Park], int]:
    """
    Get park submissions with pagination, status filtering, and search.
    """
    query = db.query(Park)
    
    # Filter by status
    if status and status != "all":
        query = query.filter(Park.status == status)
    
    # Search filter (fuzzy match on name, address, or submitter name)
    if search:
        from models.database import User
        search_pattern = f"%{search}%"
        query = query.outerjoin(User, Park.submitted_by == User.id).filter(
            or_(
                Park.name.ilike(search_pattern),
                Park.address.ilike(search_pattern),
                User.name.ilike(search_pattern)
            )
        )
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply pagination
    skip = (page - 1) * page_size
    parks = query.order_by(Park.submit_date.desc()).offset(skip).limit(page_size).all()
    
    return parks, total_count


def moderate_park(
    db: Session,
    park_id: UUID,
    request: ModerateParkRequest,
) -> Optional[Park]:
    """
    Moderate a park (approve, deny, or set to pending).
    """
    park = get_park(db, park_id)

    if not park:
        return None

    status = request.status
    park.status = status

    # Set approved_by and approved_at if approving/rejecting
    if status in ("approved", "rejected"):
        if request.approved_by:
            park.approved_by = request.approved_by
        park.approved_at = datetime.now(timezone.utc)
    elif status == "pending":
        park.approved_by = None
        park.approved_at = None

    if request.admin_notes is not None:
        park.admin_notes = request.admin_notes.strip() or ""
    
    db.commit()
    db.refresh(park)
    return park

