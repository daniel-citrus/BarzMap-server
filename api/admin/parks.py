"""
API routes for Parks.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from decimal import Decimal
from services.Database import (
    get_db,
    update_park,
    delete_park,
)
from models.requests.parks import ParkUpdate
from models.responses.ParksResponses import ParkResponse

router = APIRouter()


@router.put("/{park_id}", response_model=ParkResponse, tags=["Parks"])
def update_park_by_id(
    park_id: UUID,
    park_data: ParkUpdate,
    db: Session = Depends(get_db)
):
    """Update a park."""
    park = update_park(
        db=db,
        park_id=park_id,
        name=park_data.name,
        description=park_data.description,
        latitude=Decimal(str(park_data.latitude)) if park_data.latitude else None,
        longitude=Decimal(str(park_data.longitude)) if park_data.longitude else None,
        address=park_data.address,
        status=park_data.status,
        approved_by=park_data.approved_by,
        approved_at=park_data.approved_at,
        admin_notes=park_data.admin_notes,
    )
    if not park:
        raise HTTPException(status_code=404, detail="Park not found")
    return park


@router.delete("/{park_id}", tags=["Parks"])
def delete_park_by_id(
    park_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a park."""
    success = delete_park(db, park_id)
    if not success:
        raise HTTPException(status_code=404, detail="Park not found")
    return {"message": "Park deleted successfully"}

