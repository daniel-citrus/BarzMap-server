from pydantic import BaseModel, EmailStr
from typing import Optional


class UserAuthenticationRequest(BaseModel):
    userToken: str
    firstName: str
    lastName: str
    profile_picture_url: Optional[str] = None
    email: EmailStr
