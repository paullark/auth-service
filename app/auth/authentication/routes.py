from typing import Annotated

from fastapi import APIRouter, Body, Security

from app.auth.authentication.models import SignupData, LoginData, TokenData, TokenPair
from app.auth.authentication.services import authenticate_user, get_token_data
from app.auth.users.models import User
from app.auth.users.services import get_user

auth = APIRouter(prefix="/auth", tags=["Authentication"])


@auth.get("/me")
async def get_me(
        claims: Annotated[TokenData, Security(get_token_data, scopes=["user"])]
) -> User:
    return await get_user(claims.user_id)


@auth.post("/signup")
async def signup(signin: SignupData):
    pass


@auth.post("/login")
async def login(login_data: LoginData) -> TokenPair:
    return await authenticate_user(**login_data.dict())


@auth.post("/logout")
async def logout() -> None:
    pass


@auth.patch("/refresh")
async def refresh(refresh_token: str = Body(embed=True)) -> TokenPair:
    pass
