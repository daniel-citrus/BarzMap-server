from pydantic import BaseModel, ConfigDict
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


class ParkResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    status: str
    submitted_by: Optional[UUID] = None
    submit_date: datetime
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
