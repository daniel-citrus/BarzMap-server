from pydantic import BaseModel
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime



class ModerateParkRequest(BaseModel):
    """Request model for moderate_park (approve, reject, or set to pending)."""
    status: Literal["approved", "rejected", "pending"]
    approved_by: Optional[UUID] = None
    admin_notes: Optional[str] = None


class ParkCreate(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None
    submitted_by: Optional[UUID] = None
    status: Optional[str] = "pending"  # pending, approved, rejected


class ParkUpdate(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None
    submitted_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    status: Optional[str] = None  # pending, approved, rejected
    admin_notes: Optional[str] = None
