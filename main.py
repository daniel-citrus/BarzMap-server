from fastapi import FastAPI
from api.authenticated import (
    parks_router,
    submissions_router,
    images_router,
    equipment_router,
    reviews_router,
    events_router,
    park_equipment_router,
)
from api.admin import (
    admin_router,
    parks_router as admin_parks_router,
    equipment_router as admin_equipment_router,
    images_router as admin_images_router,
    reviews_router as admin_reviews_router,
    park_equipment_router as admin_park_equipment_router,
    events_router as admin_events_router,
    users_router,
)

# Tag metadata for better Swagger UI organization
tags_metadata = [
    {
        "name": "Parks",
        "description": "Park-related endpoints. Includes viewing parks and park submissions.",
    },
    {
        "name": "Submissions",
        "description": "Park submission endpoints for submitting new parks.",
    },
    {
        "name": "Equipment",
        "description": "Equipment type management endpoints.",
    },
    {
        "name": "Park Equipment",
        "description": "Park-equipment relationship endpoints.",
    },
    {
        "name": "Reviews",
        "description": "Park review and rating endpoints.",
    },
    {
        "name": "Events",
        "description": "Event feed and location-based event queries.",
    },
    {
        "name": "Images",
        "description": "Park image management endpoints.",
    },
    {
        "name": "Users",
        "description": "User management endpoints (Admin only).",
    },
    {
        "name": "Admin",
        "description": "Admin moderation and management endpoints.",
    },
]

app = FastAPI(
    title="BarzMap API",
    description="API for finding and sharing outdoor gyms and workout parks",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# Authenticated routes (require user authentication)
app.include_router(parks_router, prefix="/api/authenticated/parks", tags=["Parks"])
app.include_router(submissions_router, prefix="/api/authenticated/submissions", tags=["Submissions"])
app.include_router(images_router, prefix="/api/authenticated/images", tags=["Images"])
app.include_router(equipment_router, prefix="/api/authenticated/equipment", tags=["Equipment"])
app.include_router(reviews_router, prefix="/api/authenticated/reviews", tags=["Reviews"])
app.include_router(events_router, prefix="/api/authenticated/events", tags=["Events"])
app.include_router(park_equipment_router, prefix="/api/authenticated/park-equipment", tags=["Park Equipment"])

# Admin routes (require admin authentication)
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(admin_parks_router, prefix="/api/admin/parks", tags=["Parks"])
app.include_router(admin_equipment_router, prefix="/api/admin/equipment", tags=["Equipment"])
app.include_router(admin_images_router, prefix="/api/admin/images", tags=["Images"])
app.include_router(admin_reviews_router, prefix="/api/admin/reviews", tags=["Reviews"])
app.include_router(admin_park_equipment_router, prefix="/api/admin/park-equipment", tags=["Park Equipment"])
app.include_router(admin_events_router, prefix="/api/admin/events", tags=["Events"])
app.include_router(users_router, prefix="/api/admin/users", tags=["Users"])
