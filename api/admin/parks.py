"""
API routes for Parks.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from services.Database import (
    get_db,
    create_park,
    get_park,
    get_all_parks,
    get_parks_by_status,
    get_parks_by_location,
    update_park,
    delete_park,
)
from models.requests.parks import ParkCreate, ParkUpdate
from models.responses.ParksResponses import ParkResponse

router = APIRouter()


@router.post("/", response_model=ParkResponse, tags=["Parks"])
def create_new_park(
    park_data: ParkCreate,
    db: Session = Depends(get_db)
):
    """Create a new park."""
    return create_park(
        db=db,
        name=park_data.name,
        latitude=Decimal(str(park_data.latitude)),
        longitude=Decimal(str(park_data.longitude)),
        description=park_data.description,
        address=park_data.address,
        city=park_data.city,
        state=park_data.state,
        country=park_data.country,
        postal_code=park_data.postal_code,
        submitted_by=park_data.submitted_by,
        status=park_data.status or "pending",
    )


@router.get("/", response_model=List[ParkResponse], tags=["Parks"])
def get_parks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(pending|approved|rejected)$"),
    db: Session = Depends(get_db)
):
    """Get all parks with optional filtering."""
    return get_all_parks(db, skip=skip, limit=limit, status=status)


@router.get("/status/{status}", response_model=List[ParkResponse], tags=["Parks"])
def get_parks_by_status_filter(
    status: str,
    db: Session = Depends(get_db)
):
    """Get all parks by status."""
    return get_parks_by_status(db, status)


@router.get("/location", response_model=List[ParkResponse], tags=["Parks"])
def get_parks_in_location(
    min_latitude: float = Query(..., description="Minimum latitude"),
    max_latitude: float = Query(..., description="Maximum latitude"),
    min_longitude: float = Query(..., description="Minimum longitude"),
    max_longitude: float = Query(..., description="Maximum longitude"),
    status: Optional[str] = Query(..., regex="^(pending|approved|rejected)$"),
    db: Session = Depends(get_db)
):
    """Get parks within a geographic bounding box."""
    return get_parks_by_location(
        db=db,
        min_latitude=Decimal(str(min_latitude)),
        max_latitude=Decimal(str(max_latitude)),
        min_longitude=Decimal(str(min_longitude)),
        max_longitude=Decimal(str(max_longitude)),
        status=status,
    )


@router.get("/{park_id}", response_model=ParkResponse, tags=["Parks"])
def get_park_by_id(
    park_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a park by ID."""
    park = get_park(db, park_id)
    if not park:
        raise HTTPException(status_code=404, detail="Park not found")
    return park


@router.put("/{park_id}", response_model=ParkResponse, tags=["Parks"])
def update_park_by_id(
    park_id: UUID,
    park_data: ParkUpdate,
    db: Session = Depends(get_db)
):
    """Update a park."""
    park = update_park(
        db=db,
        park_id=park_id,
        name=park_data.name,
        description=park_data.description,
        latitude=Decimal(str(park_data.latitude)) if park_data.latitude else None,
        longitude=Decimal(str(park_data.longitude)) if park_data.longitude else None,
        address=park_data.address,
        city=park_data.city,
        state=park_data.state,
        country=park_data.country,
        postal_code=park_data.postal_code,
        status=park_data.status,
        approved_by=park_data.approved_by,
        approved_at=park_data.approved_at,
        admin_notes=park_data.admin_notes,
    )
    if not park:
        raise HTTPException(status_code=404, detail="Park not found")
    return park


@router.delete("/{park_id}", tags=["Parks"])
def delete_park_by_id(
    park_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a park."""
    success = delete_park(db, park_id)
    if not success:
        raise HTTPException(status_code=404, detail="Park not found")
    return {"message": "Park deleted successfully"}

