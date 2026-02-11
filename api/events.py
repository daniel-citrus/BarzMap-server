"""
Event endpoint used by the frontend: events feed.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from models.responses.EventsResponses import EventsListResponse
from services.Database import get_db
from services.Manager.Events import get_events_feed

router = APIRouter()


@router.get("/", response_model=EventsListResponse, tags=["Events"])
def get_events_endpoint(
    lat: Optional[float] = Query(None, description="Latitude for distance calculation"),
    lng: Optional[float] = Query(None, description="Longitude for distance calculation"),
    radius: Optional[float] = Query(None, description="Radius in miles (required if lat/lng provided)"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of events to return"),
    fromDate: Optional[str] = Query(None, description="ISO-8601 timestamp; omit events before this date"),
    db: Session = Depends(get_db)
):
    """Get events feed with optional location-based filtering."""
    return get_events_feed(
        db,
        lat=lat,
        lng=lng,
        radius=radius,
        limit=limit,
        from_date_str=fromDate,
    )
