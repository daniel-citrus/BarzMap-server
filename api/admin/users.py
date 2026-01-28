"""
API routes for Users.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from services.Database import (
    get_db,
    create_user,
    get_user,
    get_user_by_email,
    get_user_by_auth0_id,
    get_all_users,
    update_user,
    delete_user,
)
from models.requests.users import UserCreate, UserUpdate
from models.responses.UsersResponses import UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse, tags=["Users"])
def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user."""
    # Check if user with email already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Check if user with auth0_id already exists
    existing_auth0_user = get_user_by_auth0_id(db, user_data.auth0_id)
    if existing_auth0_user:
        raise HTTPException(status_code=400, detail="User with this Auth0 ID already exists")
    
    return create_user(
        db=db,
        auth0_id=user_data.auth0_id,
        email=user_data.email,
        name=user_data.name,
        role=user_data.role.value,
    )


@router.get("/", response_model=List[UserResponse], tags=["Users"])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all users with optional filtering."""
    return get_all_users(db, skip=skip, limit=limit, is_active=is_active)


@router.get("/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a user by ID."""
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/email/{email}", response_model=UserResponse, tags=["Users"])
def get_user_by_email_address(
    email: str,
    db: Session = Depends(get_db)
):
    """Get a user by email."""
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/auth0/{auth0_id}", response_model=UserResponse, tags=["Users"])
def get_user_by_auth0(
    auth0_id: str,
    db: Session = Depends(get_db)
):
    """Get a user by Auth0 ID."""
    user = get_user_by_auth0_id(db, auth0_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user_by_id(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update a user."""
    user = update_user(
        db=db,
        user_id=user_id,
        email=user_data.email,
        name=user_data.name,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", tags=["Users"])
def delete_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a user."""
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

