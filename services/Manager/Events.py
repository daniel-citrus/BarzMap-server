"""
Events feed business logic.
"""
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.responses.EventsResponses import EventResponse, EventsListResponse
from services.Database.EventsTable import get_events, haversine_distance


def format_distance(distance_miles: float) -> str:
    """Format distance in miles as a string like '0.8 mi away'."""
    if distance_miles < 0.1:
        return f"{round(distance_miles * 5280)} ft away"
    elif distance_miles < 1:
        return f"{round(distance_miles * 10) / 10} mi away"
    else:
        return f"{round(distance_miles * 10) / 10} mi away"


def get_events_feed(
    db: Session,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius: Optional[float] = None,
    limit: int = 10,
    from_date_str: Optional[str] = None,
) -> EventsListResponse:
    """Get events feed with optional location-based filtering. Raises HTTPException on validation errors."""
    if lat is not None or lng is not None or radius is not None:
        if lat is None or lng is None or radius is None:
            raise HTTPException(
                status_code=400,
                detail="lat, lng, and radius must all be provided together if any are provided",
            )

    from_date = None
    if from_date_str:
        try:
            from_date = datetime.fromisoformat(from_date_str.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid fromDate format. Expected ISO-8601 timestamp.",
            )

    events = get_events(
        db=db,
        lat=lat,
        lng=lng,
        radius=radius,
        limit=limit,
        from_date=from_date,
    )

    event_responses = []
    for event in events:
        if not event.park:
            continue

        distance_str = None
        if lat is not None and lng is not None:
            distance_miles = haversine_distance(
                lat,
                lng,
                float(event.park.latitude),
                float(event.park.longitude),
            )
            distance_str = format_distance(distance_miles)

        date_str = None
        if event.event_date:
            date_str = event.event_date.isoformat()

        time_str = None
        if event.event_time:
            time_str = event.event_time.strftime("%H:%M")

        event_id = f"EVT-{str(event.id).replace('-', '').upper()[:8]}"
        address = event.park.address or "Address not available"

        event_responses.append(
            EventResponse(
                id=event_id,
                parkName=event.park.name,
                address=address,
                distance=distance_str,
                date=date_str,
                time=time_str,
                description=event.description,
                host=event.host,
                ctaLabel="View event",
            )
        )

    return EventsListResponse(data=event_responses)
