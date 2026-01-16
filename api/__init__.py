"""
API routers for BarzMap.
Consolidates all API routers for easy import.
"""
from .databaseRouters import (
    users_router,
    parks_router,
    equipment_router,
    images_router,
    reviews_router,
    park_equipment_router,
    events_router,
    admin_router,
)

from .MainRouter import router as main_router

__all__ = [
    "users_router",
    "parks_router",
    "equipment_router",
    "images_router",
    "reviews_router",
    "park_equipment_router",
    "events_router",
    "admin_router",
    "main_router",
]

