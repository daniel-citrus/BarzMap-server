from typing import Optional
from sqlalchemy.orm import Session

from models.database import User
from services.Database.UsersTable import create_user, get_user_by_auth0_id
from ..Adapters.Auth0ManagementAdapter import updateUserPermissions

"""
User-related business logic.
"""


def LoginSequence(db: Session, auth0Id: str) -> Optional[User]:
    user = get_user_by_auth0_id(db, auth0Id)

    if user is None:
        # TODO: fetch real email/name from Auth0 Management API response.
        user = create_user(
            db=db,
            auth0_id=auth0Id,
            email="TODO_EMAIL_FROM_AUTH0",
            name="TODO_NAME_FROM_AUTH0",
        )

        updateUserPermissions(auth0Id)
        return user

    return user
