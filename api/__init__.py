"""
API routers for BarzMap.
Organized by access level: authenticated and admin.
"""
from .authenticated import parks_router, submissions_router
from .admin import (
    admin_router,
    parks_router as admin_parks_router,
    equipment_router,
    images_router,
    reviews_router,
    park_equipment_router,
    events_router,
    users_router,
)

__all__ = [
    # Authenticated routers
    "parks_router",
    "submissions_router",
    # Admin routers
    "admin_router",
    "admin_parks_router",
    "equipment_router",
    "images_router",
    "reviews_router",
    "park_equipment_router",
    "events_router",
    "users_router",
]

