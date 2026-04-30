from uuid import UUID
"""
User-related business logic.
"""


def LoginSequence(user_id: UUID) -> None:
    print('login sequence successful', user_id)
    # verify user with auth0
    # use user_id to check if user exists in db
    # if user exists, return entry
    # else, create new user entry, then return entry
