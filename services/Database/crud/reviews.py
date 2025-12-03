"""
CRUD operations for Reviews table.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from models.database import Review


def create_review(
    db: Session,
    park_id: UUID,
    user_id: UUID,
    rating: int,
    comment: Optional[str] = None,
    is_approved: bool = True,
) -> Review:
    """Create a new review."""
    review = Review(
        park_id=park_id,
        user_id=user_id,
        rating=rating,
        comment=comment,
        is_approved=is_approved,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_review(db: Session, review_id: UUID) -> Optional[Review]:
    """Get a review by ID."""
    return db.query(Review).filter(Review.id == review_id).first()


def get_review_by_park_and_user(
    db: Session,
    park_id: UUID,
    user_id: UUID,
) -> Optional[Review]:
    """Get a review by park and user (unique constraint)."""
    return db.query(Review).filter(
        Review.park_id == park_id,
        Review.user_id == user_id
    ).first()


def get_reviews_by_park(
    db: Session,
    park_id: UUID,
    is_approved: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Review]:
    """Get all reviews for a park."""
    query = db.query(Review).filter(Review.park_id == park_id)
    if is_approved is not None:
        query = query.filter(Review.is_approved == is_approved)
    return query.offset(skip).limit(limit).all()


def get_reviews_by_user(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> List[Review]:
    """Get all reviews by a user."""
    return db.query(Review).filter(
        Review.user_id == user_id
    ).offset(skip).limit(limit).all()


def update_review(
    db: Session,
    review_id: UUID,
    rating: Optional[int] = None,
    comment: Optional[str] = None,
    is_approved: Optional[bool] = None,
) -> Optional[Review]:
    """Update a review."""
    review = get_review(db, review_id)
    if not review:
        return None
    
    if rating is not None:
        review.rating = rating
    if comment is not None:
        review.comment = comment
    if is_approved is not None:
        review.is_approved = is_approved
    
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review_id: UUID) -> bool:
    """Delete a review."""
    review = get_review(db, review_id)
    if not review:
        return False
    
    db.delete(review)
    db.commit()
    return True

