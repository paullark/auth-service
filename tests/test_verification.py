from datetime import timedelta

from httpx import AsyncClient

from app.auth.authentication.tokens.models import TokenPair
from app.auth.database.services import Database
from app.auth.verification.models import Verification


async def test_confirm(user_app: AsyncClient, verification: Verification) -> None:
    response = await user_app.post(
        f"/verification/confirm/{verification.id}",
        json={"code": "123456"}
    )
    assert response.status_code == 200
    assert TokenPair(**response.json())


async def test_confirm_invalid_code(
        user_app: AsyncClient, verification: Verification
) -> None:
    response = await user_app.post(
        f"/verification/confirm/{verification.id}",
        json={"code": "654321"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect verification code."


async def test_confirm_expired_code(
        user_app: AsyncClient, verification: Verification, db: Database
) -> None:
    verification.exp_date = verification.exp_date - timedelta(minutes=2)
    verification = await db.replace(verification)

    response = await user_app.post(
        f"/verification/confirm/{verification.id}",
        json={"code": "123456"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Verification code expired."
