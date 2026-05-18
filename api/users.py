"""
User endpoints.
"""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from requests.exceptions import HTTPError
from sqlalchemy.orm import Session

from models.requests.users import UpdateUserPermissionsRequest
from models.responses.UsersResponses import UserLoginResponse, UserResponse
from services.Database import get_db
from services.Database.UsersTable import get_all_users
from services.Manager.Users import delete_user_by_auth0, loginSequence
from services.Adapters.Auth0ManagementAdapter import updateUserPermissions

router = APIRouter()

_INVALID_AUTH0_PATH = frozenset({"undefined", "null"})


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


@router.post("/{auth0_id}", response_model=UserLoginResponse, tags=["Users"])
def user_login(auth0_id: str, db: Session = Depends(get_db)) -> UserLoginResponse:
    normalized = auth0_id.strip()
    if not normalized or normalized.lower() in _INVALID_AUTH0_PATH:
        raise HTTPException(
            status_code=400,
            detail="Missing Auth0 user id (expected the Auth0 `sub`).",
        )
    payload = loginSequence(db, normalized)
    if not payload:
        raise HTTPException(status_code=404, detail="Error with login sequence")
    return payload


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


@router.get("/{auth0_id}/permissions", response_model=List, tags=["Users"])
def get_user_permissions(auth0_id: str):
    """
    Return all permission objects for a given Auth0 user.
    """
    normalized = auth0_id.strip()
    if not normalized or normalized.lower() in _INVALID_AUTH0_PATH:
        raise HTTPException(
            status_code=400,
            detail="Missing Auth0 user id (expected the Auth0 `sub`).",
        )
    from services.Adapters.Auth0ManagementAdapter import getUserPermissions

    permissions = getUserPermissions(normalized)
    if permissions is None:
        raise HTTPException(status_code=404, detail="User permissions not found.")
    return permissions


@router.delete("/{auth0_id}", status_code=204, tags=["Users"])
def delete_auth0_user(auth0_id: str, db: Session = Depends(get_db)) -> None:
    normalized = auth0_id.strip()
    if not normalized or normalized.lower() in _INVALID_AUTH0_PATH:
        raise HTTPException(
            status_code=400,
            detail="Missing Auth0 user id (expected the Auth0 `sub`).",
        )
    try:
        delete_user_by_auth0(db, normalized)
    except HTTPError as exc:
        response = exc.response
        if response is None:
            raise HTTPException(
                status_code=502, detail="Auth0 delete request failed."
            ) from exc
        try:
            detail: Any = response.json()
        except ValueError:
            detail = response.text or "Auth0 delete failed."
        raise HTTPException(status_code=response.status_code, detail=detail) from exc
