"""
API routes for Equipment.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from services.Database import (
    get_db,
    create_equipment,
    get_equipment,
    get_equipment_by_name,
    get_all_equipment,
    update_equipment,
    delete_equipment,
)
from models.requests.equipment import EquipmentCreate, EquipmentUpdate
from models.responses.EquipmentResponses import EquipmentResponse

router = APIRouter()


@router.post("/", response_model=EquipmentResponse, tags=["Equipment"])
def create_new_equipment(
    equipment_data: EquipmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new equipment type."""
    # Check if equipment with same name already exists
    existing = get_equipment_by_name(db, equipment_data.name)
    if existing:
        raise HTTPException(status_code=400, detail="Equipment with this name already exists")
    
    return create_equipment(
        db=db,
        name=equipment_data.name,
        description=equipment_data.description,
        icon_name=equipment_data.icon_name,
    )


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


@router.put("/{equipment_id}", response_model=EquipmentResponse, tags=["Equipment"])
def update_equipment_by_id(
    equipment_id: UUID,
    equipment_data: EquipmentUpdate,
    db: Session = Depends(get_db)
):
    """Update an equipment type."""
    equipment = update_equipment(
        db=db,
        equipment_id=equipment_id,
        name=equipment_data.name,
        description=equipment_data.description,
        icon_name=equipment_data.icon_name,
    )
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.delete("/{equipment_id}", tags=["Equipment"])
def delete_equipment_by_id(
    equipment_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an equipment type."""
    success = delete_equipment(db, equipment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return {"message": "Equipment deleted successfully"}

