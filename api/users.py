"""
User endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from models.responses.UsersResponses import UserResponse
from services.Manager.Users import LoginSequence

router = APIRouter()


@router.post("/{user_id}", response_model=UserResponse, tags=["Users"])
def user_login(user_id: UUID) -> UserResponse:
    user = LoginSequence(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Error with login sequence")
    return user
