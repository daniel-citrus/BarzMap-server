"""
Authenticated equipment endpoints - require user authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from services.Database import (
    get_db,
    get_equipment,
    get_equipment_by_name,
    get_all_equipment,
)
from models.responses.EquipmentResponses import EquipmentResponse

router = APIRouter()


@router.get("/", response_model=List[EquipmentResponse], tags=["Equipment"])
def get_all_equipment_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all equipment types."""
    return get_all_equipment(db, skip=skip, limit=limit)


@router.get("/{equipment_id}", response_model=EquipmentResponse, tags=["Equipment"])
def get_equipment_by_id(
    equipment_id: UUID,
    db: Session = Depends(get_db)
):
    """Get an equipment by ID."""
    equipment = get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.get("/name/{name}", response_model=EquipmentResponse, tags=["Equipment"])
def get_equipment_by_name_endpoint(
    name: str,
    db: Session = Depends(get_db)
):
    """Get an equipment by name."""
    equipment = get_equipment_by_name(db, name)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

