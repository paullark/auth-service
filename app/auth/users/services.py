from app.auth.database.services import db
from app.auth.users.models import User


async def get_user(name: str) -> User | None:
    return await db.find(User, {"username": name})
