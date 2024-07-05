from typing import Annotated

from fastapi import APIRouter, Body, Security, BackgroundTasks
from starlette import status

from app.auth.authentication.models import SignupData, LoginData
from app.auth.authentication.tokens.models import TokenData, TokenPair
from app.auth.authentication.services import signup_user, login_user
from app.auth.authentication.tokens.services import (
    get_token_data, refresh_token_pair, delete_authorization
)
from app.auth.users.models import User
from app.auth.users.services import get_user
from app.auth.verification.models import VerificationOut

auth = APIRouter(prefix="/auth", tags=["Authentication"])


@auth.get("/me")
async def get_me(
        claims: Annotated[TokenData, Security(get_token_data, scopes=["user"])]
) -> User:
    return await get_user(claims.user_id)


@auth.post("/signup")
async def signup(background_tasks: BackgroundTasks, signin: SignupData) -> VerificationOut:
    return await signup_user(background_tasks, signin)


@auth.post("/login")
async def login(login_data: LoginData) -> TokenPair:
    return await login_user(**login_data.dict())


@auth.post("/logout", status_code=status.HTTP_401_UNAUTHORIZED)
async def logout(refresh_token: Annotated[str, Body(embed=True)]) -> None:
    await delete_authorization(refresh_token)


@auth.post("/refresh")
async def refresh(refresh_token: Annotated[str, Body(embed=True)]) -> TokenPair:
    return await refresh_token_pair(refresh_token)
