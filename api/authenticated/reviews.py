"""
Authenticated review endpoints - require user authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from services.Database import (
    get_db,
    get_review,
    get_review_by_park_and_user,
    get_reviews_by_park,
    get_reviews_by_user,
)
from models.responses.ReviewsResponses import ReviewResponse

router = APIRouter()


@router.get("/{review_id}", response_model=ReviewResponse, tags=["Reviews"])
def get_review_by_id(
    review_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a review by ID."""
    review = get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("/park/{park_id}", response_model=List[ReviewResponse], tags=["Reviews"])
def get_reviews_for_park(
    park_id: UUID,
    is_approved: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all reviews for a park."""
    return get_reviews_by_park(
        db=db,
        park_id=park_id,
        is_approved=is_approved,
        skip=skip,
        limit=limit,
    )


@router.get("/user/{user_id}", response_model=List[ReviewResponse], tags=["Reviews"])
def get_reviews_by_user_id(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all reviews by a user."""
    return get_reviews_by_user(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )


@router.get("/park/{park_id}/user/{user_id}", response_model=ReviewResponse, tags=["Reviews"])
def get_review_by_park_and_user_endpoint(
    park_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a review by park and user."""
    review = get_review_by_park_and_user(db, park_id, user_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

