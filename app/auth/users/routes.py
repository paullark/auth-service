from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from starlette import status

from app.auth.authentication.models import TokenData
from app.auth.authentication.services import get_token_data
from app.auth.config import settings
from app.auth.models import ListParams
from app.auth.users.models import User, UserCreate, UserUpdate
from app.auth.users.services import get_user, create_user, get_user_by_name, get_user_list, update_user, delete_user

users = APIRouter(
    prefix="/users", tags=["Users"], dependencies=[Security(get_token_data, scopes=["admin"])]
)


@users.get("/{user_id}")
async def get_user_route(user: Annotated[User, Depends(get_user)]) -> User | None:
    return user


@users.get("/username/{username}")
async def get_user_by_name_route(user: Annotated[User, Depends(get_user_by_name)]) -> User | None:
    return user


@users.get("/")
async def get_user_list_route(
        params: Annotated[ListParams, Depends()],
        username: str | None = None,
        email: str | None = None
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


@users.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(user: Annotated[User, Depends(get_user)]) -> None:
    return await delete_user(user)
