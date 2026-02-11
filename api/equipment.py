"""
Equipment endpoint used by the frontend: list equipment types.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from models.responses.EquipmentResponses import EquipmentResponse
from services.Database import get_db
from services.Manager.Equipment import get_all_equipment_types

router = APIRouter()


@router.get("/", response_model=List[EquipmentResponse], tags=["Equipment"])
def get_all_equipment_types_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all equipment types."""
    return get_all_equipment_types(db, skip=skip, limit=limit)
