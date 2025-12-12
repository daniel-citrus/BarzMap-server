"""
CRUD operations for Events table.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, case
from typing import Optional, List, Tuple
from uuid import UUID
from decimal import Decimal
from datetime import date, datetime, time
from models.database import Event, Park
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth (in miles).
    Uses the Haversine formula.
    """
    # Radius of Earth in miles
    R = 3958.8
    
    # Convert to radians
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def calculate_bounding_box(lat: float, lng: float, radius_miles: float) -> Tuple[float, float, float, float]:
    """
    Calculate a bounding box (min_lat, max_lat, min_lng, max_lng) around a center point.
    
    This is an approximation that works well for small to medium distances.
    For more accuracy, we'll still use haversine for the final filtering.
    
    Args:
        lat: Center latitude
        lng: Center longitude
        radius_miles: Radius in miles
    
    Returns:
        Tuple of (min_lat, max_lat, min_lng, max_lng)
    """
    # Earth's radius in miles
    R = 3958.8
    
    # Convert radius to degrees (approximate)
    # 1 degree of latitude ≈ 69 miles
    # 1 degree of longitude ≈ 69 * cos(latitude) miles
    lat_degrees_per_mile = 1.0 / 69.0
    lng_degrees_per_mile = 1.0 / (69.0 * math.cos(math.radians(lat)))
    
    # Calculate bounding box with a small buffer for safety
    buffer = 1.1  # 10% buffer to ensure we don't miss parks near the edge
    lat_delta = radius_miles * lat_degrees_per_mile * buffer
    lng_delta = radius_miles * lng_degrees_per_mile * buffer
    
    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lng = lng - lng_delta
    max_lng = lng + lng_delta
    
    return (min_lat, max_lat, min_lng, max_lng)


def get_events(
    db: Session,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius: Optional[float] = None,
    limit: int = 10,
    from_date: Optional[datetime] = None,
) -> List[Event]:
    """
    Get events with optional location-based filtering and date filtering.
    
    For location filtering, this function:
    1. First filters parks using a bounding box (SQL-level filtering)
    2. Then fetches events for those parks
    3. Finally does precise haversine distance calculation (Python-level filtering)
    
    Args:
        db: Database session
        lat: Optional latitude for distance calculation
        lng: Optional longitude for distance calculation
        radius: Optional radius in miles (required if lat/lng provided)
        limit: Maximum number of events to return (default 10)
        from_date: Optional datetime to filter events after this date
    
    Returns:
        List of Event objects
    """
    # Eagerly load the park relationship to avoid lazy loading issues
    query = db.query(Event).options(joinedload(Event.park)).join(Park)
    
    # Filter by date if provided
    if from_date:
        # Convert from_date to date if it's a datetime
        from_date_only = from_date.date() if isinstance(from_date, datetime) else from_date
        query = query.filter(
            (Event.event_date >= from_date_only) | (Event.event_date.is_(None))
        )
    
    # Filter by location if lat/lng/radius provided
    if lat is not None and lng is not None and radius is not None:
        # Step 1: Calculate bounding box to filter parks at SQL level
        min_lat, max_lat, min_lng, max_lng = calculate_bounding_box(lat, lng, radius)
        
        # Step 2: Filter parks within bounding box using SQL
        # This significantly reduces the number of events we need to process
        query = query.filter(
            and_(
                Park.latitude >= Decimal(str(min_lat)),
                Park.latitude <= Decimal(str(max_lat)),
                Park.longitude >= Decimal(str(min_lng)),
                Park.longitude <= Decimal(str(max_lng)),
            )
        )
        
        # Step 3: Fetch events for parks within bounding box
        events = query.all()
        
        # Step 4: Filter by precise haversine distance (Python-level)
        # This ensures we only return events within the exact radius
        filtered_events = []
        for event in events:
            if event.park:
                distance = haversine_distance(
                    lat, lng,
                    float(event.park.latitude),
                    float(event.park.longitude)
                )
                if distance <= radius:
                    filtered_events.append((event, distance))
        
        # Step 5: Sort by distance and limit
        filtered_events.sort(key=lambda x: x[1])
        events = [event for event, _ in filtered_events[:limit]]
        
        return events
    
    # If no location filtering, just limit and return
    return query.limit(limit).all()


def create_event(
    db: Session,
    park_id: UUID,
    name: str,
    description: Optional[str] = None,
    host: Optional[str] = None,
    event_date: Optional[date] = None,
    event_time: Optional[time] = None,
    created_by: Optional[UUID] = None,
) -> Event:
    """Create a new event."""
    event = Event(
        park_id=park_id,
        name=name,
        description=description,
        host=host,
        event_date=event_date,
        event_time=event_time,
        created_by=created_by,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_event(db: Session, event_id: UUID) -> Optional[Event]:
    """Get an event by ID."""
    return db.query(Event).filter(Event.id == event_id).first()
