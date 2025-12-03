"""
CRUD operations for Park_Equipment junction table.
"""
from sqlalchemy.orm import Session
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID
from models.database import ParkEquipment, Equipment

if TYPE_CHECKING:
    from models.database import Park


def add_equipment_to_park(
    db: Session,
    park_id: UUID,
    equipment_id: UUID,
) -> ParkEquipment:
    """Add equipment to a park."""
    # Check if relationship already exists
    existing = get_park_equipment(db, park_id, equipment_id)
    if existing:
        return existing
    
    park_equipment = ParkEquipment(
        park_id=park_id,
        equipment_id=equipment_id,
    )
    db.add(park_equipment)
    db.commit()
    db.refresh(park_equipment)
    return park_equipment


def remove_equipment_from_park(
    db: Session,
    park_id: UUID,
    equipment_id: UUID,
) -> bool:
    """Remove equipment from a park."""
    park_equipment = get_park_equipment(db, park_id, equipment_id)
    if not park_equipment:
        return False
    
    db.delete(park_equipment)
    db.commit()
    return True


def get_park_equipment(
    db: Session,
    park_id: UUID,
    equipment_id: UUID,
) -> Optional[ParkEquipment]:
    """Get a specific park-equipment relationship."""
    return db.query(ParkEquipment).filter(
        ParkEquipment.park_id == park_id,
        ParkEquipment.equipment_id == equipment_id
    ).first()


def get_equipment_by_park(db: Session, park_id: UUID) -> List[Equipment]:
    """Get all equipment for a park."""
    return db.query(Equipment).join(
        ParkEquipment,
        Equipment.id == ParkEquipment.equipment_id
    ).filter(ParkEquipment.park_id == park_id).all()


def get_parks_by_equipment(db: Session, equipment_id: UUID) -> List["Park"]:
    """Get all parks that have a specific equipment."""
    from models.database import Park
    return db.query(Park).join(
        ParkEquipment,
        Park.id == ParkEquipment.park_id
    ).filter(ParkEquipment.equipment_id == equipment_id).all()


def remove_all_equipment_from_park(
    db: Session,
    park_id: UUID,
) -> int:
    """Remove all equipment from a park. Returns count of deleted items."""
    count = db.query(ParkEquipment).filter(
        ParkEquipment.park_id == park_id
    ).delete()
    db.commit()
    return count

