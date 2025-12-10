"""
CRUD operations for Users table.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from models.database import User


def create_user(
    db: Session,
    auth0_id: str,
    email: str,
    name: str,
    profile_picture_url: Optional[str] = None,
    role: str = "user",
    is_active: bool = True,
) -> User:
    """Create a new user."""
    user = User(
        auth0_id=auth0_id,
        email=email,
        name=name,
        profile_picture_url=profile_picture_url,
        role=role,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: UUID) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_auth0_id(db: Session, auth0_id: str) -> Optional[User]:
    """Get a user by Auth0 ID."""
    return db.query(User).filter(User.auth0_id == auth0_id).first()


def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
) -> List[User]:
    """Get all users with optional filtering."""
    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.offset(skip).limit(limit).all()


def update_user(
    db: Session,
    user_id: UUID,
    email: Optional[str] = None,
    name: Optional[str] = None,
    profile_picture_url: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Optional[User]:
    """Update a user."""
    user = get_user(db, user_id)
    if not user:
        return None
    
    if email is not None:
        user.email = email
    if name is not None:
        user.name = name
    if profile_picture_url is not None:
        user.profile_picture_url = profile_picture_url
    if role is not None:
        user.role = role
    if is_active is not None:
        user.is_active = is_active
    
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: UUID) -> bool:
    """Delete a user."""
    user = get_user(db, user_id)
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True

