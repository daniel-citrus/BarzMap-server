"""
CRUD operations for Equipment table.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from models.database import Equipment


def create_equipment(
    db: Session,
    name: str,
    description: Optional[str] = None,
    icon_name: Optional[str] = None,
) -> Equipment:
    """Create a new equipment type."""
    equipment = Equipment(
        name=name,
        description=description,
        icon_name=icon_name,
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


def get_equipment(db: Session, equipment_id: UUID) -> Optional[Equipment]:
    """Get an equipment by ID."""
    return db.query(Equipment).filter(Equipment.id == equipment_id).first()


def get_equipment_by_name(db: Session, name: str) -> Optional[Equipment]:
    """Get an equipment by name."""
    return db.query(Equipment).filter(Equipment.name == name).first()


def get_all_equipment(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[Equipment]:
    """Get all equipment types."""
    return db.query(Equipment).offset(skip).limit(limit).all()


def update_equipment(
    db: Session,
    equipment_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    icon_name: Optional[str] = None,
) -> Optional[Equipment]:
    """Update an equipment type."""
    equipment = get_equipment(db, equipment_id)
    if not equipment:
        return None
    
    if name is not None:
        equipment.name = name
    if description is not None:
        equipment.description = description
    if icon_name is not None:
        equipment.icon_name = icon_name
    
    db.commit()
    db.refresh(equipment)
    return equipment


def delete_equipment(db: Session, equipment_id: UUID) -> bool:
    """Delete an equipment type."""
    equipment = get_equipment(db, equipment_id)
    if not equipment:
        return False
    
    db.delete(equipment)
    db.commit()
    return True

