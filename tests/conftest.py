from datetime import datetime, UTC, timedelta
from typing import AsyncGenerator

import jwt
import pytest
from bson import ObjectId
from httpx import AsyncClient, Headers

from app.auth.authentication.models import SignupData, LoginData, Authorization
from app.auth.authentication.tokens.models import TokenPair, TokenData
from app.auth.authentication.utils import get_password_hash
from app.auth.database.services import Database
from app.auth.database.services import db as database
from app.auth import app as main_app
from app.auth.config import settings
from app.auth.database.types import PyObjectId
from app.auth.users.models import User, UserCreate, UserUpdate
from app.auth.verification.models import Verification


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
    return settings.secret_key


@pytest.fixture
async def algorithm() -> str:
    return "HS256"


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
async def user_token_pair(user: User, secret_key: str, db: Database) -> TokenPair:
    token_pair = TokenPair(
        access_token=jwt.encode(
            TokenData(
                user_id=PyObjectId(user.id),
                scopes=user.roles,
                token_type="access",
                exp=datetime.now(UTC) + timedelta(minutes=1)
            ).dict(),
            secret_key,
            algorithm="HS256"
        ),
        refresh_token=jwt.encode(
            TokenData(
                user_id=PyObjectId(user.id),
                scopes=user.roles,
                token_type="refresh",
                exp=datetime.now(UTC) + timedelta(minutes=5)
            ).dict(),
            secret_key,
            algorithm="HS256"
        ),
    )
    await db.insert(
        Authorization(
            user_id=ObjectId(user.id), refresh_token=token_pair.refresh_token
        )
    )
    return token_pair


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
async def admin_token_pair(admin: User, secret_key: str, db: Database) -> TokenPair:
    token_pair = TokenPair(
        access_token=jwt.encode(
            TokenData(
                user_id=PyObjectId(admin.id),
                scopes=admin.roles,
                token_type="access",
                exp=datetime.now(UTC) + timedelta(minutes=1)
            ).dict(),
            secret_key,
            algorithm="HS256"
        ),
        refresh_token=jwt.encode(
            TokenData(
                user_id=PyObjectId(admin.id),
                scopes=admin.roles,
                token_type="refresh",
                exp=datetime.now(UTC) + timedelta(minutes=5)
            ).dict(),
            secret_key,
            algorithm="HS256"
        ),
    )
    await db.insert(
        Authorization(
            user_id=ObjectId(admin.id), refresh_token=token_pair.refresh_token
        )
    )
    return token_pair


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


@pytest.fixture
async def user_app(
        db: Database, user_token_pair: TokenPair
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=main_app, base_url="http://test") as client:
        client.headers = Headers({"Authorization": f"Bearer {user_token_pair.access_token}"})
        yield client


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


@pytest.fixture
async def signup_data(password: str) -> SignupData:
    return SignupData(
        username="user_in",
        password=password,
        email="test@test.com"
    )


@pytest.fixture
async def login_data(user: User) -> LoginData:
    return LoginData(username=user.username, password="27.:^:.Cl")


@pytest.fixture
async def verification(db: Database, user: User) -> Verification:
    verification = Verification(
        email=user.email,
        exp_date=datetime.now(UTC) + timedelta(minutes=1),
        resend_date=datetime.now(UTC) + timedelta(minutes=1),
        created=datetime.now(UTC),
        code="123456"
    )
    await db.insert(verification)
    return verification
