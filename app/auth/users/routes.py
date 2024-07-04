from typing import Annotated

from fastapi import APIRouter, Depends, Security
from pydantic import EmailStr
from starlette import status

from app.auth.authentication.tokens.services import get_token_data
from app.auth.models import ListParams
from app.auth.users.models import User, UserCreate, UserUpdate
from app.auth.users.services import (
    get_user,
    create_user,
    get_user_by_name,
    get_user_list,
    update_user,
    delete_user,
    get_user_by_email
)

users = APIRouter(
    prefix="/users", tags=["Users"], dependencies=[Security(get_token_data, scopes=["admin"])]
)


@users.get("/{user_id}")
async def get_user_route(user: Annotated[User, Depends(get_user)]) -> User:
    return user


@users.get("/username/{username}")
async def get_user_by_name_route(user: Annotated[User, Depends(get_user_by_name)]) -> User:
    return user


@users.get("/email/{email}")
async def get_user_by_email_route(user: Annotated[User, Depends(get_user_by_email)]) -> User:
    return user


@users.get("/")
async def get_user_list_route(
        params: Annotated[ListParams, Depends()],
        username: str | None = None,
        email: EmailStr | None = None
) -> list[User]:
    return await get_user_list(username, email, params)


@users.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user_route(user: UserCreate) -> User:
    return await create_user(user)


@users.patch("/{user_id}")
async def update_user_route(
        user: Annotated[User, Depends(get_user)],
        user_update: UserUpdate
) -> User:
    return await update_user(user, user_update)


@users.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(user: Annotated[User, Depends(get_user)]) -> None:
    return await delete_user(user)
