from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class EquipmentCreate(BaseModel):
    name: str
    description: str
    icon_name: str


class EquipmentUpdate(BaseModel):
    id: str
    name: str
    icon_name: str
    description: Optional[str] = None


class EquipmentResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    icon_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
