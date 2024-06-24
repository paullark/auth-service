from fastapi import APIRouter, Body

from app.auth.authentication.models import SignupData, TokenPair, LoginData
from app.auth.authentication.services import authenticate_user

auth = APIRouter(prefix="/auth", tags=["Authentication"])


@auth.post("/signup")
async def signup(signin: SignupData):
    pass


@auth.post("/login")
async def login(login_data: LoginData):
    return await authenticate_user(**login_data.dict())


@auth.post("/logout")
async def logout() -> None:
    pass


@auth.patch("/refresh")
async def refresh(refresh_token: str = Body(embed=True)) -> TokenPair:
    pass
