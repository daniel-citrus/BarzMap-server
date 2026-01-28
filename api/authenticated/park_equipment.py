"""
Authenticated park equipment endpoints - require user authentication.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from services.Database import (
    get_db,
    get_park_equipment,
    get_equipment_by_park,
    get_parks_by_equipment,
)
from models.responses.ParkEquipmentResponses import ParkEquipmentResponse
from models.responses.EquipmentResponses import EquipmentResponse
from models.responses.ParksResponses import ParkResponse

router = APIRouter()


@router.get("/park/{park_id}/equipment", response_model=List[EquipmentResponse], tags=["Park Equipment"])
def get_equipment_for_park(
    park_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all equipment for a park."""
    return get_equipment_by_park(db, park_id)


@router.get("/equipment/{equipment_id}/parks", response_model=List[ParkResponse], tags=["Park Equipment"])
def get_parks_with_equipment(
    equipment_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all parks that have a specific equipment."""
    return get_parks_by_equipment(db, equipment_id)


@router.get("/park/{park_id}/equipment/{equipment_id}", response_model=ParkEquipmentResponse, tags=["Park Equipment"])
def get_park_equipment_relationship(
    park_id: UUID,
    equipment_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific park-equipment relationship."""
    relationship = get_park_equipment(db, park_id, equipment_id)
    if not relationship:
        raise HTTPException(status_code=404, detail="Park-equipment relationship not found")
    return relationship

