"""
Response models for equipment endpoints.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class EquipmentResponse(BaseModel):
    """Response model for equipment data."""
    id: UUID
    name: str
    description: Optional[str] = None
    icon_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

