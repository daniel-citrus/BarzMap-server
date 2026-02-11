"""
Park-equipment endpoint used by the frontend: list equipment for a park.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from models.responses.EquipmentResponses import EquipmentResponse
from services.Database import get_db
from services.Manager.ParkEquipment import get_equipment_for_park

router = APIRouter()


@router.get("/park/{park_id}/equipment", response_model=List[EquipmentResponse], tags=["Park Equipment"])
def get_equipment_for_park_endpoint(
    park_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all equipment for a park."""
    return get_equipment_for_park(db, park_id)
