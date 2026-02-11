from fastapi import FastAPI
from api import (
    parks_router,
    submissions_router,
    images_router,
    equipment_router,
    events_router,
    park_equipment_router,
    admin_router,
)

# Tag metadata for better Swagger UI organization
tags_metadata = [
    {
        "name": "Parks",
        "description": "Park-related endpoints. List parks and parks by location.",
    },
    {
        "name": "Submissions",
        "description": "Park submission: submit a new park.",
    },
    {
        "name": "Equipment",
        "description": "List equipment types.",
    },
    {
        "name": "Park Equipment",
        "description": "List equipment for a park.",
    },
    {
        "name": "Events",
        "description": "Event feed.",
    },
    {
        "name": "Images",
        "description": "Images for a park.",
    },
    {
        "name": "Admin",
        "description": "Moderate park submissions (PATCH/DELETE).",
    },
]

app = FastAPI(
    title="BarzMap API",
    description="API for finding and sharing outdoor gyms and workout parks",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# Routes used by the frontend
app.include_router(parks_router, prefix="/api/parks", tags=["Parks"])
app.include_router(submissions_router, prefix="/api/submissions", tags=["Submissions"])
app.include_router(images_router, prefix="/api/images", tags=["Images"])
app.include_router(equipment_router, prefix="/api/equipment", tags=["Equipment"])
app.include_router(events_router, prefix="/api/events", tags=["Events"])
app.include_router(park_equipment_router, prefix="/api/park-equipment", tags=["Park Equipment"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])
