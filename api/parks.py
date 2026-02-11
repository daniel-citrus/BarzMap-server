"""
Park endpoints used by the frontend: list parks and parks by location.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from models.responses.ParksResponses import ParkResponse
from services.Database import get_db, get_all_parks, get_parks_by_location

router = APIRouter()


@router.get("/", response_model=List[ParkResponse], tags=["Parks"])
def get_parks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, regex="^(pending|approved|rejected)$", description="Filter by park status"),
    db: Session = Depends(get_db)
):
    """Get all parks with optional filtering."""
    return get_all_parks(db, skip=skip, limit=limit, status=status)


@router.get("/location", response_model=List[ParkResponse], tags=["Parks"])
def get_parks_in_location(
    min_latitude: float = Query(..., description="Minimum latitude"),
    max_latitude: float = Query(..., description="Maximum latitude"),
    min_longitude: float = Query(..., description="Minimum longitude"),
    max_longitude: float = Query(..., description="Maximum longitude"),
    status: Optional[str] = Query("approved", regex="^(pending|approved|rejected)$", description="Filter by park status"),
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
