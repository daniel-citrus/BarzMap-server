from typing import Optional
from sqlalchemy.orm import Session

from models.database import User
from services.Database.UsersTable import get_user, get_user_by_auth0_id
from ..Adapters.Auth0ManagementAdapter import updateUserPermissions

"""
User-related business logic.
"""


def LoginSequence(db: Session, auth0Id: str) -> Optional[User]:
    user = get_user_by_auth0_id(db, auth0Id)

    if user is None:
        return None

    # if user does not exist: generate new entry, grant basic access (TODO)

    return get_user(db, user.id)
