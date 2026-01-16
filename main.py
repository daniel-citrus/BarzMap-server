from fastapi import FastAPI
from api import main_router

app = FastAPI()

# Main submission routes
app.include_router(main_router, prefix="/api", tags=["Submissions"])
