"""
Authenticated API routers - require user authentication.
"""
from .parks import router as parks_router
from .submissions import router as submissions_router
from .images import router as images_router

__all__ = [
    "parks_router",
    "submissions_router",
    "images_router",
]

