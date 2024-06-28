from bson import ObjectId

from app.auth.authentication.services import get_password_hash
from app.auth.database.types import PyObjectId
from app.auth.database.services import db

from app.auth.models import ListParams
from app.auth.users.models import User, UserCreate, UserUpdate


async def get_user(user_id: PyObjectId) -> User:
    return await db.find(User, {"_id": ObjectId(user_id)}, exception=True)


async def get_user_by_name(username: str) -> User | None:
    return await db.find(
        User, {"username": {"$regex": username, "$options": "i"}}, exception=True
    )


async def get_user_list(
        username: str | None, email: str | None, params: ListParams
) -> list[User]:
    query = (
        {"username": {"$regex": username, "$options": "i"}} if username else {} |
        {"email": {"$regex": email, "$options": "i"}} if email else {}
    )
    return await db.find_many(User, query, **params.to_query())


async def create_user(user: UserCreate) -> User:
    user = User(**user.dict())
    return await db.insert(user.copy(update={"password": get_password_hash(user.password)}))


async def update_user(user: User, update: UserUpdate) -> User:
    update_dict = update.dict(exclude_unset=True)
    updated_user = user.copy(update=update_dict)
    user = await db.replace(updated_user)
    return user


async def delete_user(user: User) -> None:
    await db.delete(user)
