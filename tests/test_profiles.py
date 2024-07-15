from httpx import AsyncClient
from pydantic import EmailStr

from app.auth.authentication.utils import verify_password
from app.auth.users.models import User, UserUpdate
from app.auth.verification.models import VerificationOut


async def test_retrieve_me(user_app: AsyncClient, user: User) -> None:
    response = await user_app.get("/profiles/me")
    assert response.status_code == 200, response.json()


async def test_retrieve_not_me(app: AsyncClient, user: User) -> None:
    response = await app.get("/profiles/me")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


async def test_change_username(user_app: AsyncClient, user: User) -> None:
    response = await user_app.put(
        "/profiles/username", json={"username": "another_user"}
    )
    assert response.status_code == 200, response.json()
    assert response.json()["username"] == "another_user"


async def test_change_username_exists(
    user_app: AsyncClient, user: User
) -> None:
    response = await user_app.put(
        "/profiles/username", json={"username": "user"}
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "User user already exists."


async def test_change_email(
    user_app: AsyncClient, user: User, new_email: EmailStr
) -> None:
    response = await user_app.put("/profiles/email", json={"email": new_email})
    assert response.status_code == 200, response.json()
    verification = VerificationOut(**response.json())
    assert verification.action.data == UserUpdate(email=new_email)


async def test_change_password(
    user_app: AsyncClient,
    user: User,
    plain_password: str,
    new_plain_password: str,
) -> None:
    response = await user_app.put(
        "/profiles/password",
        json={
            "old_password": plain_password,
            "new_password": new_plain_password,
        },
    )
    assert response.status_code == 200, response.json()
    verification = VerificationOut(**response.json())
    assert verification.action.data.password
    assert verify_password(
        new_plain_password, verification.action.data.password
    )


async def test_change_password_incorrect_old(
    user_app: AsyncClient, user: User, new_plain_password: str
) -> None:
    response = await user_app.put(
        "/profiles/password",
        json={"old_password": "password", "new_password": new_plain_password},
    )
    assert response.status_code == 422, response.json()
    assert response.json()["detail"] == "Incorrect password."
