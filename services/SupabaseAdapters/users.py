from dotenv import load_dotenv
from supabase import create_client
from models.requests.users import UserCreate, UserUpdate
import uuid
import os

load_dotenv(".env")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def create_user(payload: UserCreate):
    auth0 = payload.auth0_id
    email = payload.email
    name = payload.name
    role = payload.role

    response = (
        supabase.table("users")
        .insert({"auth0_id": auth0, "email": email, "name": name, "role": role})
        .execute()
    )

    return response.data


def get_user(id: str | None = None):
    id = uuid.UUID(id)
    response = supabase.table("users").select("*").eq("id", str(id)).execute()
    return response.data


def update_user(payload: UserUpdate):
    id = payload.id
    email = payload.email
    name = payload.name

    response = (
        supabase.table("users")
        .update({"email": email, "name": name})
        .eq("id", str(id))
        .execute()
    )

    return response.data


def delete_user(id: str | None = None):
    id = uuid.UUID(id)
    response = supabase.table("users").delete().eq("id", str(id)).execute()

    return response.data
