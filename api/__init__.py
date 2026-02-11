"""
API routers for BarzMap (trimmed to endpoints used by the frontend).
"""
from .parks import router as parks_router
from .equipment import router as equipment_router
from .events import router as events_router
from .images import router as images_router
from .park_equipment import router as park_equipment_router

__all__ = [
    "parks_router",
    "equipment_router",
    "events_router",
    "images_router",
    "park_equipment_router",
]