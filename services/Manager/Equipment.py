"""
Equipment list business logic.
"""
from sqlalchemy.orm import Session

from models.responses.EquipmentResponses import EquipmentResponse
from services.Database import get_all_equipment


def get_all_equipment_types(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[EquipmentResponse]:
    """Get all equipment types."""
    return get_all_equipment(db, skip=skip, limit=limit)
