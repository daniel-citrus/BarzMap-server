from uuid import UUID
from ...core.auth0Client import auth0
"""
User-related business logic.
"""


def LoginSequence(user_id: UUID) -> None:
    print('login sequence successful', user_id)
    # verify user with auth0
    # if new user
        # create new user account with basic access
    # return entry
