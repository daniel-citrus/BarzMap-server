from fastapi import FastAPI
from api.authenticated import parks_router, submissions_router, images_router
from api.admin import (
    admin_router,
    parks_router as admin_parks_router,
    equipment_router,
    images_router as admin_images_router,
    reviews_router,
    park_equipment_router,
    events_router,
    users_router,
)

app = FastAPI()

# Authenticated routes (require user authentication)
app.include_router(parks_router, prefix="/api/authenticated/parks", tags=["Parks"])
app.include_router(submissions_router, prefix="/api/authenticated/submissions", tags=["Submissions"])
app.include_router(images_router, prefix="/api/authenticated/images", tags=["Images"])

# Admin routes (require admin authentication)
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(admin_parks_router, prefix="/api/admin/parks", tags=["Admin - Parks"])
app.include_router(equipment_router, prefix="/api/admin/equipment", tags=["Admin - Equipment"])
app.include_router(admin_images_router, prefix="/api/admin/images", tags=["Admin - Images"])
app.include_router(reviews_router, prefix="/api/admin/reviews", tags=["Admin - Reviews"])
app.include_router(park_equipment_router, prefix="/api/admin/park-equipment", tags=["Admin - Park Equipment"])
app.include_router(events_router, prefix="/api/admin/events", tags=["Admin - Events"])
app.include_router(users_router, prefix="/api/admin/users", tags=["Admin - Users"])
