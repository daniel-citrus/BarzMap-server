from fastapi import FastAPI
from api.SupabaseRouter import router as supabase_router
from api.AuthenticationRouter import router as authentication_router

app = FastAPI()

app.include_router(authentication_router, prefix="/auth")
app.include_router(supabase_router, prefix="")
