import asyncio
from datetime import datetime, UTC, timedelta
from typing import AsyncGenerator

import jwt
import pytest
from asgi_lifespan import LifespanManager
from bson import ObjectId
from httpx import AsyncClient, Headers

from app.auth.authentication.models import LoginData, TokenPair, TokenData, BaseTokenData
from app.auth.authentication.tokens.services import authenticate_user
from app.auth.authentication.utils import pwd_context, get_password_hash
from app.auth.database.services import Database
from app.auth.database.services import db as database
from app.auth import app as main_app
from app.auth.database.types import PyObjectId
from app.auth.users.models import User, UserCreate, UserUpdate
from app.auth.users.services import create_user


@pytest.fixture
async def db() -> Database:
    db_name = str(ObjectId())
    database.database = database.client[db_name]

    yield database

    await database.client.drop_database(db_name)


@pytest.fixture
async def password() -> str:
    return get_password_hash("27.:^:.Cl")


@pytest.fixture
async def secret_key() -> str:
    return "60768709b48691e3222d8e3100cb7bd83e208919958302f3ec01d3eedb39c398"


@pytest.fixture
async def user(password: str, db: Database) -> User:
    user = await db.insert(
        User(
            id=ObjectId(),
            username="user",
            password=password,
            email="test@test.com",
            roles=["user"],
            is_active=True
        )
    )
    return user


@pytest.fixture
async def user_token_pair(user: User, secret_key: str) -> TokenPair:
    # t = TokenPair(
    #     access_token=jwt.encode(
    #         TokenData(
    #             user_id=PyObjectId(user.id),
    #             scopes=user.roles,
    #             token_type="access",
    #             exp=datetime.now(UTC) + timedelta(minutes=1)
    #         ).dict(),
    #         secret_key,
    #         algorithm="HS256"
    #     ),
    #     refresh_token=jwt.encode(
    #         TokenData(
    #             user_id=PyObjectId(user.id),
    #             scopes=user.roles,
    #             token_type="refresh",
    #             exp=datetime.now(UTC) + timedelta(minutes=5)
    #         ).dict(),
    #         secret_key,
    #         algorithm="HS256"
    #     ),
    # )
    # print(t)
    # return t
    return await authenticate_user(user)


@pytest.fixture
async def admin(password: str, db: Database) -> User:
    admin = await db.insert(
        User(
            id=ObjectId(),
            username="admin",
            password=password,
            email="test@test.com",
            roles=["user", "admin"],
            is_active=True
        )
    )
    return admin


@pytest.fixture
async def admin_token_pair(admin: User, secret_key: str) -> TokenPair:
    # t = TokenPair(
    #     access_token=jwt.encode(
    #         TokenData(
    #             user_id=PyObjectId(admin.id),
    #             scopes=admin.roles,
    #             token_type="access",
    #             exp=datetime.now(UTC) + timedelta(minutes=1)
    #         ).dict(),
    #         secret_key,
    #         algorithm="HS256"
    #     ),
    #     refresh_token=jwt.encode(
    #         TokenData(
    #             user_id=PyObjectId(admin.id),
    #             scopes=admin.roles,
    #             token_type="refresh",
    #             exp=datetime.now(UTC) + timedelta(minutes=5)
    #         ).dict(),
    #         secret_key,
    #         algorithm="HS256"
    #     ),
    # )
    # print(t)
    # return t
    return await authenticate_user(admin)

@pytest.fixture
async def app(db: Database) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=main_app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def admin_app(
        db: Database, admin_token_pair: TokenPair
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=main_app, base_url="http://test") as client:
        client.headers = Headers({"Authorization": f"Bearer {admin_token_pair.access_token}"})
        yield client


# @pytest.fixture
# def event_loop():
#     policy = asyncio.get_event_loop_policy()
#     loop = policy.new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture
async def user_create(password: str) -> UserCreate:
    return UserCreate(
        username="admin",
        password=password,
        email="test@test.com",
        roles=["user"]
    )


@pytest.fixture
async def user_update_roles() -> UserUpdate:
    return UserUpdate(roles=["admin"])
