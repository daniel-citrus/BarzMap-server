from services.SupabaseAdapters import equipment as supabase_equipment_adapter
from services.SupabaseAdapters import users as supabase_user_adapter
from services.SupabaseAdapters import parks as supabase_parks_adapter
from fastapi import APIRouter
from models.requests.equipment import EquipmentCreate, EquipmentUpdate
from models.requests.users import UserCreate, UserUpdate
from models.requests.parks import ParkCreate, ParkUpdate

router = APIRouter()

# ============================================================
#  Parks
# ============================================================


@router.get("/parks/", tags=["Parks"])
def get_park(id: str | None = None):
    response = supabase_parks_adapter.get_park(id)
    return response


@router.post("/parks/create", tags=["Parks"])
def create_park(payload: ParkCreate):
    response = supabase_parks_adapter.create_park(payload)
    return response


@router.put("/parks/update", tags=["Parks"])
def update_park(payload: ParkUpdate):
    response = supabase_parks_adapter.update_park(payload)
    return response


@router.delete("/parks/delete", tags=["Parks"])
def delete_park(id: str):
    response = supabase_parks_adapter.delete_park(id)
    return response


# ============================================================
#  Equipment
# ============================================================


@router.get("/equipment/", tags=["Equipment"])
def get_equipment(id: str | None = None):
    response = supabase_equipment_adapter.get_equipment(id)
    return response


@router.post("/equipment/create", tags=["Equipment"])
def create_equipment(payload: EquipmentCreate):
    response = supabase_equipment_adapter.create_equipment(payload)
    return response


@router.put("/equipment/update", tags=["Equipment"])
def update_equipment(payload: EquipmentUpdate):
    response = supabase_equipment_adapter.update_equipment(payload)
    return response


@router.delete("/equipment/delete", tags=["Equipment"])
def delete_equipment(id: str | None = None):
    response = supabase_equipment_adapter.delete_equipment(id)
    return response


# ============================================================
#  User
# ============================================================


@router.get("/user/", tags=["Users"])
def get_user(id: str | None = None):
    response = supabase_user_adapter.get_user(id)
    return response


@router.post("/user/create", tags=["Users"])
def create_user(payload: UserCreate):
    response = supabase_user_adapter.create_user(payload)
    return response


@router.put("/user/update", tags=["Users"])
def update_user(payload: UserUpdate):
    response = supabase_user_adapter.update_user(payload)
    return response


@router.delete("/user/delete", tags=["Users"])
def delete_user(id: str):
    response = supabase_user_adapter.delete_user(id)
    return response
