"""
Response models for events endpoints.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional


class EventResponse(BaseModel):
    """Response model for events matching FEDC specification."""
    id: str
    parkName: str
    address: str
    distance: Optional[str] = None
    date: Optional[str] = None  # ISO-8601 date format (YYYY-MM-DD)
    time: Optional[str] = None  # 24-hour format (HH:mm) in UTC
    description: Optional[str] = None
    host: Optional[str] = None
    ctaLabel: Optional[str] = "View event"

    model_config = ConfigDict(from_attributes=True)


class EventsListResponse(BaseModel):
    """Response wrapper for events list."""
    data: list[EventResponse]

