"""
Admin API routers - require admin authentication.
"""
from .admin import router as admin_router
from .parks import router as parks_router
from .equipment import router as equipment_router
from .images import router as images_router
from .reviews import router as reviews_router
from .park_equipment import router as park_equipment_router
from .events import router as events_router
from .users import router as users_router

__all__ = [
    "admin_router",
    "parks_router",
    "equipment_router",
    "images_router",
    "reviews_router",
    "park_equipment_router",
    "events_router",
    "users_router",
]

