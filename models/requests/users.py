from enum import Enum
from pydantic import BaseModel, Field


class Role(str, Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"


class UserCreate(BaseModel):
    auth0_id: str
    email: str
    name: str
    role: Role = Field(
        default=Role.user, description="User role: user, moderator, admin"
    )

class UserUpdate(BaseModel): 
    id: str
    email: str
    name: str