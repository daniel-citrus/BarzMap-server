from fastapi import FastAPI
from services.Authentication import router as authentication_router
from api import (
    users_router,
    parks_router,
    equipment_router,
    images_router,
    reviews_router,
    park_equipment_router,
)

app = FastAPI()

# Authentication routes
app.include_router(authentication_router, prefix="/auth")

# Database API routes
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(parks_router, prefix="/api/parks", tags=["Parks"])
app.include_router(equipment_router, prefix="/api/equipment", tags=["Equipment"])
app.include_router(images_router, prefix="/api/images", tags=["Images"])
app.include_router(reviews_router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(park_equipment_router, prefix="/api/park-equipment", tags=["Park Equipment"])
