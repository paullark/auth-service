from typing import Annotated

from fastapi import APIRouter, Body, Depends

from app.auth.users.models import User
from app.auth.users.profiles.models import PasswordUpdate
from app.auth.users.profiles.services import update_username, get_current_user
from app.auth.users.services import CurrentUser, get_user

profiles = APIRouter(prefix="/profiles", tags=["Profiles"])


@profiles.get("/me")
async def get_me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


@profiles.put("/username")
async def update_username_route(
        user: Annotated[User, Depends(get_current_user)], username: str = Body(embed=True)
) -> User:
    return await update_username(user, username)


@profiles.put("/email")
async def update_email_route(
        user: Annotated[User, Depends(get_current_user)], email: str = Body(embed=True)
) -> User:
    pass


@profiles.put("/password")
async def update_password_route(
        passwords: PasswordUpdate, user: Annotated[User, Depends(get_current_user)]
) -> User:
    pass
