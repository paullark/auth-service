from typing import Annotated

from fastapi import APIRouter, Body, Depends

from app.auth.users.models import User
from app.auth.users.profiles.models import PasswordUpdate
from app.auth.users.profiles.services import (
    change_email,
    change_password,
    change_username,
    get_current_user,
)
from app.auth.verification.models import VerificationOut

profiles = APIRouter(prefix="/profiles", tags=["Profiles"])


@profiles.get("/me")
async def get_me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


@profiles.put("/username")
async def change_username_route(
    user: Annotated[User, Depends(get_current_user)],
    username: str = Body(embed=True),
) -> User:
    return await change_username(user, username)


@profiles.put("/email")
async def change_email_route(
    user: Annotated[User, Depends(get_current_user)],
    email: str = Body(embed=True),
) -> VerificationOut:
    return await change_email(user, email)


@profiles.put("/password")
async def change_password_route(
    passwords: PasswordUpdate, user: Annotated[User, Depends(get_current_user)]
) -> VerificationOut:
    return await change_password(passwords, user)
