"""
API routers for BarzMap.
Consolidates all API routers for easy import.
"""
from .UsersRouter import router as users_router
from .ParksRouter import router as parks_router
from .EquipmentRouter import router as equipment_router
from .ImagesRouter import router as images_router
from .ReviewsRouter import router as reviews_router
from .ParkEquipmentRouter import router as park_equipment_router
from .EventsRouter import router as events_router
from .AdminRouter import router as admin_router

__all__ = [
    "users_router",
    "parks_router",
    "equipment_router",
    "images_router",
    "reviews_router",
    "park_equipment_router",
    "events_router",
    "admin_router",
]

