from httpx import AsyncClient

from app.auth.users.models import User


async def test_retrieve_me(user_app: AsyncClient, user: User) -> None:
    response = await user_app.get("/profiles/me")
    assert response.status_code == 200, response.json()


async def test_retrieve_not_me(app: AsyncClient, user: User) -> None:
    response = await app.get("/profiles/me")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"
