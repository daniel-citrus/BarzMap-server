from typing import Any, Optional
from sqlalchemy.orm import Session

from models.responses.UsersResponses import UserLoginResponse
from services.Database.UsersTable import (
    create_user,
    delete_user_by_auth0_id,
    get_user_by_auth0_id,
)

from services.Adapters.Auth0ManagementAdapter import (
    deleteUser,
    updateUserPermissions,
    getUser,
    getUserRoles,
)

"""
User-related business logic.
"""


def loginSequence(db: Session, auth0Id: str) -> Optional[UserLoginResponse]:
    """Load or create user in DB; attach Auth0 role ids for the login payload only."""
    user = get_user_by_auth0_id(db, auth0Id)

    if user is None:
        auth0User = getUser(auth0Id)

        if auth0User is None:
            return None
        user = create_user(
            db=db,
            auth0_id=auth0Id,
            email=auth0User.get("email"),
            name=auth0User.get("name"),
        )

    user_roles: list[dict[str, Any]] = getUserRoles(auth0Id) or []

    if not user_roles:
        permissions_result = updateUserPermissions(auth0Id)

        status_code = int(permissions_result.get("status_code", 500))
        if status_code >= 300:
            print(
                "Auth0 role assignment failed",
                {"auth0_id": auth0Id, **permissions_result},
            )

        user_roles = getUserRoles(auth0Id) or []

    role_ids: list[str] = []
    for role in user_roles:
        if not isinstance(role, dict):
            continue
        role_id = role.get("id")
        if role_id is None:
            continue
        role_ids.append(str(role_id))

    return UserLoginResponse(
        id=user.id,
        auth0_id=user.auth0_id,
        email=user.email,
        name=user.name,
        profile_picture_url=user.profile_picture_url,
        roles=role_ids,
    )


def delete_user_by_auth0(db: Session, auth0_id: str) -> bool:
    """
    Delete a user by Auth0 ID.
    Deletes the user from Auth0 (via Auth0ManagementAdapter) and from the local database.
    Returns True if user was deleted in DB, False if not found.
    """

    # Delete from Auth0 (raises exception on HTTP error)
    deleteUser(auth0_id)
    # Delete from local DB
    return delete_user_by_auth0_id(db, auth0_id)
