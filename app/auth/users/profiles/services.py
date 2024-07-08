from app.auth.database.services import db
from app.auth.users.models import User
from app.auth.users.services import get_user, CurrentUser


async def get_current_user(claims: CurrentUser) -> User:
    return await get_user(claims.user_id)


async def update_username(user: User, username: str) -> User:
    return await db.replace(user.model_copy(update={'username': username}))


async def update_email(user: User, email: str) -> User:
    pass
