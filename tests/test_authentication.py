from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from app.auth.authentication.models import LoginData, SignupData
from app.auth.authentication.tokens.models import TokenPair
from app.auth.database.services import Database
from app.auth.users.models import User
from app.auth.verification.models import Verification, VerificationOut


async def test_signup(
        app: AsyncClient, signup_data: SignupData, db: Database
) -> None:
    response = await app.post(
        "/auth/signup", json=jsonable_encoder(signup_data)
    )
    assert response.status_code == 200
    assert VerificationOut(**response.json())
    await db.find(
        Verification,
        {"_id": ObjectId(response.json().get("_id"))}, exception=True
    )


async def test_signup_already_exists(
    app: AsyncClient, signup_data: SignupData, db: Database, user: User
) -> None:
    response = await app.post(
        "/auth/signup", json=jsonable_encoder(signup_data)
    )
    assert response.status_code == 422


async def test_login(app: AsyncClient, login_data: LoginData) -> None:
    response = await app.post(
        "/auth/login", json=jsonable_encoder(login_data)
    )
    assert response.status_code == 200
    assert TokenPair(**response.json())


async def test_login_invalid_user(
    app: AsyncClient, login_data: LoginData, user: User, db: Database
) -> None:
    await db.replace(user.model_copy(update={"is_active": False}))
    response = await app.post(
        "/auth/login", json=jsonable_encoder(login_data)
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "User is not verified."


async def test_login_incorrect_password(
    app: AsyncClient, login_data: LoginData
) -> None:
    login_data.password = "password"
    response = await app.post(
        "/auth/login", json=jsonable_encoder(login_data)
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password."


async def test_logout(
        user_app: AsyncClient, user_token_pair: TokenPair
) -> None:
    response = await user_app.post(
        "/auth/logout",
        json={"refresh_token": user_token_pair.refresh_token}
    )
    assert response.status_code == 401
    assert response.json() is None


async def test_refresh(
        user_app: AsyncClient, user_token_pair: TokenPair
) -> None:
    response = await user_app.post(
        "/auth/refresh", json={"refresh_token": user_token_pair.refresh_token}
    )
    assert response.status_code == 200
    assert TokenPair(**response.json())
