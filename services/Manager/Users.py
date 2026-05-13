from typing import Optional
from sqlalchemy.orm import Session

from models.database import User
from services.Database.UsersTable import (
    create_user,
    delete_user_by_auth0_id,
    get_user_by_auth0_id,
)
from ..Adapters.Auth0ManagementAdapter import (
    updateUserPermissions,
    getUser,
    getUserRoles,
)

"""
User-related business logic.
"""


def LoginSequence(db: Session, auth0Id: str) -> Optional[User]:
    """Load existing user or create from Auth0 and assign default Auth0 role."""
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

        permissions_result = updateUserPermissions(auth0Id)
        status_code = int(permissions_result.get("status_code", 500))
        if status_code >= 300:
            print(
                "Auth0 role assignment failed",
                {"auth0_id": auth0Id, **permissions_result},
            )

    userRoles = getUserRoles(auth0Id)

    if userRoles == []:
        updateUserPermissions(auth0Id)

    return user


def delete_user_by_auth0(db: Session, auth0_id: str) -> bool:
    """
    Delete a user by Auth0 ID.
    Deletes the user from Auth0 (via Auth0ManagementAdapter) and from the local database.
    Returns True if user was deleted in DB, False if not found.
    """
    from services.Adapters.Auth0ManagementAdapter import deleteUser

    # Delete from Auth0 (raises exception on HTTP error)
    deleteUser(auth0_id)
    # Delete from local DB
    return delete_user_by_auth0_id(db, auth0_id)
