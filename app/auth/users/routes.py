from fastapi import APIRouter

from app.auth.users.models import User
from app.auth.users.services import get_user

users = APIRouter()


@users.get("/find_user")
async def get_user_route(name: str) -> User | None:
    return await get_user(name)
