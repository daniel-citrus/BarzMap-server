"""
Authenticated API routers - require user authentication.
"""
from .parks import router as parks_router
from .submissions import router as submissions_router
from .images import router as images_router
from .equipment import router as equipment_router
from .reviews import router as reviews_router
from .events import router as events_router
from .park_equipment import router as park_equipment_router

__all__ = [
    "parks_router",
    "submissions_router",
    "images_router",
    "equipment_router",
    "reviews_router",
    "events_router",
    "park_equipment_router",
]

