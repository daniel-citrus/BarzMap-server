"""
User endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.responses.UsersResponses import UserResponse
from services.Database import get_db
from services.Manager.Users import LoginSequence

router = APIRouter()


@router.post("/{auth0_id}", response_model=UserResponse, tags=["Users"])
def user_login(auth0_id: str, db: Session = Depends(get_db)) -> UserResponse:
    user = LoginSequence(db, auth0_id)
    if not user:
        raise HTTPException(status_code=404, detail="Error with login sequence")
    return user
