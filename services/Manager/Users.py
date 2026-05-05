from typing import Optional
from sqlalchemy.orm import Session

from models.database import User
from services.Database.UsersTable import create_user, get_user_by_auth0_id
from ..Adapters.Auth0ManagementAdapter import updateUserPermissions, getUser

"""
User-related business logic.
"""


def LoginSequence(db: Session, auth0Id: str) -> Optional[User]:
    """Verify if user is new, if so, generate new entry in DB and apply permissions."""
    user = get_user_by_auth0_id(db, auth0Id)

    if user is None:
        auth0User = getUser(auth0Id)
        user = create_user(
            db=db,
            auth0_id=auth0Id,
            email=auth0User.get("email"),
            name=auth0User.get("name"),
        )

        updateUserPermissions(auth0Id)

    return user
