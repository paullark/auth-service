from typing import Annotated

from fastapi import APIRouter, Body
from starlette import status

from app.auth.authentication.models import LoginData, SignupData
from app.auth.authentication.services import login_user, signup_user
from app.auth.authentication.tokens.models import TokenPair
from app.auth.authentication.tokens.services import (
    delete_authorization,
    refresh_token_pair,
)
from app.auth.verification.models import VerificationOut

auth = APIRouter(prefix="/auth", tags=["Authentication"])


@auth.post("/signup")
async def signup(signin: SignupData) -> VerificationOut:
    return await signup_user(signin)


@auth.post("/login")
async def login(login_data: LoginData) -> TokenPair:
    return await login_user(**login_data.dict())


@auth.post("/logout", status_code=status.HTTP_401_UNAUTHORIZED)
async def logout(refresh_token: Annotated[str, Body(embed=True)]) -> None:
    await delete_authorization(refresh_token)


@auth.post("/refresh")
async def refresh(
    refresh_token: Annotated[str, Body(embed=True)]
) -> TokenPair:
    return await refresh_token_pair(refresh_token)
