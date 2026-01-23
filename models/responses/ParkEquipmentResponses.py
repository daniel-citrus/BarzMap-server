"""
Response models for park equipment endpoints.
"""
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class ParkEquipmentResponse(BaseModel):
    """Response model for park equipment relationship."""
    id: UUID
    park_id: UUID
    equipment_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

