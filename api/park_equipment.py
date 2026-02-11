"""
Park-equipment endpoint used by the frontend: list equipment for a park.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from services.Database import get_db, get_equipment_by_park
from models.responses.EquipmentResponses import EquipmentResponse

router = APIRouter()


@router.get("/park/{park_id}/equipment", response_model=List[EquipmentResponse], tags=["Park Equipment"])
def get_equipment_for_park(
    park_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all equipment for a park."""
    return get_equipment_by_park(db, park_id)
