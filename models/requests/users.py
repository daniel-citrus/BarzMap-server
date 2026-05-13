from typing import List

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    auth0_id: str
    email: str
    name: str


class UserUpdate(BaseModel):
    id: str
    email: str
    name: str


class UpdateUserPermissionsRequest(BaseModel):
    roles: List[str] = Field(
        default_factory=list, description="Auth0 role IDs to assign to the user."
    )
