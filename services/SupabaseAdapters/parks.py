from dotenv import load_dotenv
from supabase import create_client
from models.requests.parks import ParkCreate, ParkUpdate
import uuid
import os

load_dotenv(".env")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


def create_park(payload: ParkCreate):
    name = payload.name
    description = payload.description
    latitude = payload.latitude
    longitude = payload.longitude
    address = payload.address
    city = payload.city
    state = payload.state
    country = payload.country
    postal_code = payload.postal_code

    response = (
        supabase.table("parks")
        .insert(
            {
                "name": name,
                "description": description,
                "latitude": latitude,
                "longitude": longitude,
                "address": address,
                "city": city,
                "state": state,
                "country": country,
                "postal_code": postal_code,
                "status": "pending",
            }
        )
        .execute()
    )

    return response.data


def get_park(id: str | None = None):
    response = ""
    if id:
        id = uuid.UUID(id)
        response = supabase.table("parks").select("*").eq("id", str(id)).execute()
    else:
        response = supabase.table("parks").select("*").execute()

    return response.data


def update_park(payload: ParkUpdate):
    id = payload.id
    name = payload.name
    description = payload.description
    latitude = payload.latitude
    longitude = payload.longitude
    address = payload.address
    city = payload.city
    state = payload.state
    country = payload.country
    postal_code = payload.postal_code
    status = payload.status
    admin_notes = payload.admin_notes

    response = (
        supabase.table("parks")
        .update(
            {
                "name": name,
                "description": description,
                "latitude": latitude,
                "longitude": longitude,
                "address": address,
                "city": city,
                "state": state,
                "country": country,
                "postal_code": postal_code,
                "status": status,
                "admin_notes": admin_notes,
            }
        )
        .eq("id", str(id))
        .execute()
    )

    return response.data


def delete_park(id: str | None = None):
    id = uuid.UUID(id)
    response = supabase.table("parks").delete().eq("id", str(id)).execute()
    return response.data
