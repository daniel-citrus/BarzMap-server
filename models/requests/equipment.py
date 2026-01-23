from pydantic import BaseModel
from typing import Optional


class EquipmentCreate(BaseModel):
    name: str
    description: str
    icon_name: str


class EquipmentUpdate(BaseModel):
    id: str
    name: str
    icon_name: str
    description: Optional[str] = None
