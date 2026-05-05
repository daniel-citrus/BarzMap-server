"""
User endpoints.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.responses.UsersResponses import UserResponse
from services.Database import get_db
from services.Database.UsersTable import get_all_users
from services.Manager.Users import LoginSequence

router = APIRouter()


@router.get("/", response_model=List[UserResponse], tags=["Users"])
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=100, description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db),
) -> List[UserResponse]:
    """Return all users with pagination."""
    return get_all_users(db, skip=skip, limit=limit)


@router.post("/{auth0_id}", tags=["Users"])
def user_login(auth0_id: str, db: Session = Depends(get_db)):
    user = LoginSequence(db, auth0_id)
    if not user:
        raise HTTPException(status_code=404, detail="Error with login sequence")
    return user
