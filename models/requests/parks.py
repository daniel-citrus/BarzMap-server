from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ParkCreate(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    submitted_by: Optional[UUID] = None
    status: Optional[str] = "pending"  # pending, approved, rejected


class ParkUpdate(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    submitted_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    status: Optional[str] = None  # pending, approved, rejected
    admin_notes: Optional[str] = None
