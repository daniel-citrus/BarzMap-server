"""
Park-equipment list business logic.
"""
from uuid import UUID

from sqlalchemy.orm import Session

from models.responses.EquipmentResponses import EquipmentResponse
from services.Database import get_equipment_by_park


def get_equipment_for_park(db: Session, park_id: UUID) -> list[EquipmentResponse]:
    """Get all equipment for a park."""
    return get_equipment_by_park(db, park_id)
