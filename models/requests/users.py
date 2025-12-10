from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


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

class UserResponse(BaseModel):
    id: UUID
    auth0_id: str
    email: str
    name: str
    profile_picture_url: Optional[str] = None
    role: str
    join_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
