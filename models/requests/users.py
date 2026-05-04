from pydantic import BaseModel


class UserCreate(BaseModel):
    auth0_id: str
    email: str
    name: str


class UserUpdate(BaseModel):
    id: str
    email: str
    name: str
