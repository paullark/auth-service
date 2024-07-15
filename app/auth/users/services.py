from typing import Annotated

from bson import ObjectId
from fastapi import Security
from pydantic import EmailStr

from app.auth.authentication.tokens.models import TokenData
from app.auth.authentication.tokens.services import get_token_data
from app.auth.authentication.utils import get_password_hash
from app.auth.database.services import db
from app.auth.database.types import PyObjectId
from app.auth.models import ListParams
from app.auth.users.models import User, UserCreate, UserUpdate


async def get_user(user_id: PyObjectId) -> User:
    return await db.find(User, {"_id": ObjectId(user_id)}, True)


async def get_user_by_name(username: str) -> User:
    return await db.find(
        User, {"username": {"$regex": username, "$options": "i"}}, True
    )


async def get_user_by_email(email: EmailStr) -> User:
    return await db.find(User, {"email": email}, True)


async def get_user_list(
    username: str | None, email: EmailStr | None, params: ListParams
) -> list[User]:
    query = (
        {"username": {"$regex": username, "$options": "i"}}
        if username
        else (
            {} | {"email": {"$regex": email, "$options": "i"}} if email else {}
        )
    )
    return await db.find_many(User, query, **params.to_query())


async def create_user(user_create: UserCreate) -> User:
    user = User(**user_create.model_dump())
    return await db.insert(
        user.model_copy(update={"password": get_password_hash(user.password)})
    )


async def update_user(user: User, update: UserUpdate) -> User:
    update_dict = update.model_dump(exclude_none=True)
    updated_user = user.model_copy(update=update_dict)
    user = await db.replace(updated_user)
    return user


async def delete_user(user: User) -> None:
    await db.delete(user)


CurrentUser = Annotated[TokenData, Security(get_token_data, scopes=["user"])]
