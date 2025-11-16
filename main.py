from fastapi import FastAPI
from api.AuthenticationRouter import router as authentication_router

app = FastAPI()

app.include_router(authentication_router, prefix="/auth")
