from fastapi import FastAPI
from api import (
    parks_router,
    images_router,
    equipment_router,
    events_router,
    park_equipment_router,
)

# Tag metadata for better Swagger UI organization
tags_metadata = [
    {
        "name": "Parks",
        "description": "Park-related endpoints. List parks, parks by location, and submit a new park.",
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
]

app = FastAPI(
    title="BarzMap API",
    description="API for finding and sharing outdoor gyms and workout parks",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# Routes used by the frontend
app.include_router(parks_router, prefix="/api/park", tags=["Parks"])
app.include_router(images_router, prefix="/api/images", tags=["Images"])
app.include_router(equipment_router, prefix="/api/equipment", tags=["Equipment"])
app.include_router(events_router, prefix="/api/events", tags=["Events"])
app.include_router(park_equipment_router, prefix="/api/park-equipment", tags=["Park Equipment"])
