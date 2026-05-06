"""
User endpoints.
"""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models.responses.UsersResponses import UserResponse
from services.Database import get_db
from services.Database.UsersTable import get_all_users
from services.Manager.Users import LoginSequence
from services.Adapters.Auth0ManagementAdapter import (
    getUserRoles,
    updateUserPermissions,
)

router = APIRouter()

_INVALID_AUTH0_PATH = frozenset({"undefined", "null"})


class UpdateUserPermissionsRequest(BaseModel):
    roles: List[str] = Field(
        default_factory=list, description="Auth0 role IDs to assign to the user."
    )


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
    normalized = auth0_id.strip()
    if not normalized or normalized.lower() in _INVALID_AUTH0_PATH:
        raise HTTPException(
            status_code=400,
            detail="Missing Auth0 user id (expected the Auth0 `sub`).",
        )
    user = LoginSequence(db, normalized)
    if not user:
        raise HTTPException(status_code=404, detail="Error with login sequence")
    return user


@router.post("/{auth0_id}/permissions", tags=["Users"])
def set_user_permissions(auth0_id: str, body: UpdateUserPermissionsRequest):
    normalized = auth0_id.strip()
    if not normalized or normalized.lower() in _INVALID_AUTH0_PATH:
        raise HTTPException(
            status_code=400,
            detail="Missing Auth0 user id (expected the Auth0 `sub`).",
        )

    # If roles is empty, adapter falls back to AUTH0_ROLE_USER (if configured).
    result = updateUserPermissions(normalized, roles=body.roles or None)
    if 200 <= int(result.get("status_code", 500)) < 300:
        return result
    raise HTTPException(
        status_code=int(result.get("status_code", 500)), detail=result.get("error")
    )


@router.get("/{auth0_id}/roles", tags=["Users"])
def get_user_roles(auth0_id: str) -> Optional[list[dict[str, Any]]]:
    """
    Auth0 roles for this user id (`sub`). Returns JSON ``null`` if Auth0 has no such user (404),
    or a list of role objects (possibly empty if the user has no roles).
    """
    normalized = auth0_id.strip()
    if not normalized or normalized.lower() in _INVALID_AUTH0_PATH:
        raise HTTPException(
            status_code=400,
            detail="Missing Auth0 user id (expected the Auth0 `sub`).",
        )
    return getUserRoles(normalized)
