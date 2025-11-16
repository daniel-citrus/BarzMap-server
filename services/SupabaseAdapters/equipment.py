from dotenv import load_dotenv
from supabase import create_client
from models.requests.equipment import EquipmentCreate, EquipmentUpdate
import uuid
import os

load_dotenv(".env")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def create_equipment(payload: EquipmentCreate):
    name = payload.name
    description = payload.description
    icon_name = payload.icon_name

    response = (
        supabase.table("equipment")
        .insert({"name": name, "description": description, "icon_name": icon_name})
        .execute()
    )

    return response.data


def get_equipment(id: str | None = None):
    response = ""

    if id:
        id = uuid.UUID(id)
        response = supabase.table("equipment").select("*").eq("id", str(id)).execute()
    else:
        response = supabase.table("equipment").select("*").execute()
    return response.data


def update_equipment(payload: EquipmentUpdate):
    id = payload.id
    name = payload.name
    icon_name = payload.icon_name
    description = payload.description

    response = (
        supabase.table("equipment")
        .update({"name": name, "description": description, "icon_name": icon_name})
        .eq("id", str(id))
        .execute()
    )

    return response.data


def delete_equipment(id: str | None = None):
    id = uuid.UUID(id)
    response = supabase.table("equipment").delete().eq("id", str(id)).execute()

    return response.data
