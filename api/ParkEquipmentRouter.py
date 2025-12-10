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
    get_park_equipment,
    get_equipment_by_park,
    get_parks_by_equipment,
    remove_all_equipment_from_park,
)
from models.requests.park_equipment import ParkEquipmentResponse
from models.requests.equipment import EquipmentResponse
from models.requests.parks import ParkResponse
from models.database import Equipment, ParkEquipment, Park

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


@router.delete("/park/{park_id}/equipment", tags=["Park Equipment"])
def remove_all_equipment_from_park_endpoint(
    park_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove all equipment from a park."""
    count = remove_all_equipment_from_park(db, park_id)
    return {"message": f"Removed {count} equipment items from park"}

