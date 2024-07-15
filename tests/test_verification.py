from datetime import timedelta

from httpx import AsyncClient

from app.auth.database.services import Database
from app.auth.users.models import User
from app.auth.verification.models import Verification


async def test_confirm_signup(
    user_app: AsyncClient, verification_signup: Verification
) -> None:
    response = await user_app.post(
        f"/verification/confirm/{verification_signup.id}",
        json={"code": "123456"},
    )
    assert response.status_code == 200
    assert User(**response.json())


async def test_confirm_invalid_code(
    user_app: AsyncClient, verification_signup: Verification
) -> None:
    response = await user_app.post(
        f"/verification/confirm/{verification_signup.id}",
        json={"code": "654321"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect verification code."


async def test_confirm_expired_code(
    user_app: AsyncClient, verification_signup: Verification, db: Database
) -> None:
    verification_signup.exp_date = verification_signup.exp_date - timedelta(
        minutes=2
    )
    verification = await db.replace(verification_signup)

    response = await user_app.post(
        f"/verification/confirm/{verification.id}", json={"code": "123456"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Verification code expired."


async def test_confirm_email(
    user_app: AsyncClient, verification_email: Verification
) -> None:
    response = await user_app.post(
        f"/verification/confirm/{verification_email.id}",
        json={"code": "123456"},
    )
    assert response.status_code == 200
    assert User(**response.json())


async def test_confirm_password(
    user_app: AsyncClient, verification_password: Verification
) -> None:
    response = await user_app.post(
        f"/verification/confirm/{verification_password.id}",
        json={"code": "123456"},
    )
    assert response.status_code == 200
    assert User(**response.json())
