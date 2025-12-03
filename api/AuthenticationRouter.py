from fastapi import APIRouter, Header
from models.requests.authentication import UserAuthenticationRequest

router = APIRouter()


@router.post("/validate/", tags=["Authentication"])
def valid_user(payload: UserAuthenticationRequest, authorization: str = Header(None)):
    pass
