"""
Authenticated event endpoints - require user authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from services.Database import get_db
from services.Database.EventsTable import get_events, haversine_distance
from models.responses.EventsResponses import EventResponse, EventsListResponse

router = APIRouter()


def format_distance(distance_miles: float) -> str:
    """Format distance in miles as a string like '0.8 mi away'."""
    if distance_miles < 0.1:
        return f"{round(distance_miles * 5280)} ft away"
    elif distance_miles < 1:
        return f"{round(distance_miles * 10) / 10} mi away"
    else:
        return f"{round(distance_miles * 10) / 10} mi away"


@router.get("/", response_model=EventsListResponse, tags=["Events"])
def get_events_endpoint(
    lat: Optional[float] = Query(None, description="Latitude for distance calculation"),
    lng: Optional[float] = Query(None, description="Longitude for distance calculation"),
    radius: Optional[float] = Query(None, description="Radius in miles (required if lat/lng provided)"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of events to return"),
    fromDate: Optional[str] = Query(None, description="ISO-8601 timestamp; omit events before this date"),
    db: Session = Depends(get_db)
):
    """
    Get events feed with optional location-based filtering.
    
    Matches FEDC specification for EventsBoard.jsx component.
    """
    # Validate lat/lng/radius combination
    if (lat is not None or lng is not None or radius is not None):
        if lat is None or lng is None or radius is None:
            raise HTTPException(
                status_code=400,
                detail="lat, lng, and radius must all be provided together if any are provided"
            )
    
    # Parse fromDate if provided
    from_date = None
    if fromDate:
        try:
            from_date = datetime.fromisoformat(fromDate.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid fromDate format. Expected ISO-8601 timestamp."
            )
    
    # Get events from database
    events = get_events(
        db=db,
        lat=lat,
        lng=lng,
        radius=radius,
        limit=limit,
        from_date=from_date,
    )
    
    # Convert to response format
    event_responses = []
    for event in events:
        if not event.park:
            continue  # Skip events without a park
        
        # Calculate distance if lat/lng provided
        distance_str = None
        if lat is not None and lng is not None:
            distance_miles = haversine_distance(
                lat, lng,
                float(event.park.latitude),
                float(event.park.longitude)
            )
            distance_str = format_distance(distance_miles)
        
        # Format date
        date_str = None
        if event.event_date:
            date_str = event.event_date.isoformat()
        
        # Format time
        time_str = None
        if event.event_time:
            time_str = event.event_time.strftime("%H:%M")
        
        # Format event ID as string (FEDC expects string IDs like "EVT-2401")
        # For now, we'll use a simple format. In production, you might want a custom ID generator
        event_id = f"EVT-{str(event.id).replace('-', '').upper()[:8]}"
        
        # Format address - use park address or construct from city/state
        address = event.park.address
        if not address:
            address_parts = []
            if event.park.city:
                address_parts.append(event.park.city)
            if event.park.state:
                address_parts.append(event.park.state)
            address = ", ".join(address_parts) if address_parts else "Address not available"
        
        event_responses.append(EventResponse(
            id=event_id,
            parkName=event.park.name,
            address=address,
            distance=distance_str,
            date=date_str,
            time=time_str,
            description=event.description,
            host=event.host,
            ctaLabel="View event"
        ))
    
    return EventsListResponse(data=event_responses)

