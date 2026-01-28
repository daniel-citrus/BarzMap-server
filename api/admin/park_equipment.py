"""
API routes for Park Equipment relationships.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from services.Database import (
    get_db,
    add_equipment_to_park,
    remove_equipment_from_park,
    remove_all_equipment_from_park,
)
from models.responses.ParkEquipmentResponses import ParkEquipmentResponse

router = APIRouter()


@router.post("/park/{park_id}/equipment/{equipment_id}", response_model=ParkEquipmentResponse, tags=["Park Equipment"])
def add_equipment_to_park_endpoint(
    park_id: UUID,
    equipment_id: UUID,
    db: Session = Depends(get_db)
):
    """Add equipment to a park."""
    return add_equipment_to_park(
        db=db,
        park_id=park_id,
        equipment_id=equipment_id,
    )


@router.delete("/park/{park_id}/equipment/{equipment_id}", tags=["Park Equipment"])
def remove_equipment_from_park_endpoint(
    park_id: UUID,
    equipment_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove equipment from a park."""
    success = remove_equipment_from_park(db, park_id, equipment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Park-equipment relationship not found")
    return {"message": "Equipment removed from park successfully"}


@router.delete("/park/{park_id}/equipment", tags=["Park Equipment"])
def remove_all_equipment_from_park_endpoint(
    park_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove all equipment from a park."""
    count = remove_all_equipment_from_park(db, park_id)
    return {"message": f"Removed {count} equipment items from park"}

