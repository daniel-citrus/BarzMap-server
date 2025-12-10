"""
CRUD operations for Images table.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from models.database import Image


def create_image(
    db: Session,
    park_id: UUID,
    image_url: str,
    uploaded_by: Optional[UUID] = None,
    thumbnail_url: Optional[str] = None,
    alt_text: Optional[str] = None,
    is_approved: bool = False,
    is_primary: bool = False,
    is_inappropriate: bool = False,
) -> Image:
    """Create a new image."""
    # If setting as primary, unset other primary images for this park
    if is_primary:
        db.query(Image).filter(
            Image.park_id == park_id,
            Image.is_primary == True
        ).update({"is_primary": False})
    
    image = Image(
        park_id=park_id,
        uploaded_by=uploaded_by,
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        alt_text=alt_text,
        is_approved=is_approved,
        is_primary=is_primary,
        is_inappropriate=is_inappropriate,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


def get_image(db: Session, image_id: UUID) -> Optional[Image]:
    """Get an image by ID."""
    return db.query(Image).filter(Image.id == image_id).first()


def get_images_by_park(
    db: Session,
    park_id: UUID,
    is_approved: Optional[bool] = None,
    is_primary: Optional[bool] = None,
) -> List[Image]:
    """Get all images for a park with optional filtering."""
    query = db.query(Image).filter(Image.park_id == park_id)
    if is_approved is not None:
        query = query.filter(Image.is_approved == is_approved)
    if is_primary is not None:
        query = query.filter(Image.is_primary == is_primary)
    return query.all()


def get_primary_image(db: Session, park_id: UUID) -> Optional[Image]:
    """Get the primary image for a park."""
    return db.query(Image).filter(
        Image.park_id == park_id,
        Image.is_primary == True
    ).first()


def update_image(
    db: Session,
    image_id: UUID,
    image_url: Optional[str] = None,
    thumbnail_url: Optional[str] = None,
    alt_text: Optional[str] = None,
    is_approved: Optional[bool] = None,
    is_primary: Optional[bool] = None,
    is_inappropriate: Optional[bool] = None,
) -> Optional[Image]:
    """Update an image."""
    image = get_image(db, image_id)
    if not image:
        return None
    
    # If setting as primary, unset other primary images for this park
    if is_primary is True and not image.is_primary:
        db.query(Image).filter(
            Image.park_id == image.park_id,
            Image.is_primary == True
        ).update({"is_primary": False})
    
    if image_url is not None:
        image.image_url = image_url
    if thumbnail_url is not None:
        image.thumbnail_url = thumbnail_url
    if alt_text is not None:
        image.alt_text = alt_text
    if is_approved is not None:
        image.is_approved = is_approved
    if is_primary is not None:
        image.is_primary = is_primary
    if is_inappropriate is not None:
        image.is_inappropriate = is_inappropriate
    
    db.commit()
    db.refresh(image)
    return image


def delete_image(db: Session, image_id: UUID) -> bool:
    """Delete an image."""
    image = get_image(db, image_id)
    if not image:
        return False
    
    db.delete(image)
    db.commit()
    return True

