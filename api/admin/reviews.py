"""
API routes for Reviews.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from services.Database import (
    get_db,
    create_review,
    update_review,
    delete_review,
)
from models.requests.reviews import ReviewCreate, ReviewUpdate
from models.responses.ReviewsResponses import ReviewResponse

router = APIRouter()


@router.post("/", response_model=ReviewResponse, tags=["Reviews"])
def create_new_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db)
):
    """Create a new review."""
    # Check if review already exists for this park and user
    existing = get_review_by_park_and_user(db, review_data.park_id, review_data.user_id)
    if existing:
        raise HTTPException(status_code=400, detail="Review already exists for this park and user")
    
    return create_review(
        db=db,
        park_id=review_data.park_id,
        user_id=review_data.user_id,
        rating=review_data.rating,
        comment=review_data.comment,
        is_approved=review_data.is_approved,
    )


@router.put("/{review_id}", response_model=ReviewResponse, tags=["Reviews"])
def update_review_by_id(
    review_id: UUID,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db)
):
    """Update a review."""
    review = update_review(
        db=db,
        review_id=review_id,
        rating=review_data.rating,
        comment=review_data.comment,
        is_approved=review_data.is_approved,
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.delete("/{review_id}", tags=["Reviews"])
def delete_review_by_id(
    review_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a review."""
    success = delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted successfully"}

