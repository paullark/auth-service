from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from app.auth.database.services import Database
from app.auth.users.models import User, UserCreate, UserUpdate


async def test_retrieve(admin_app: AsyncClient, user: User) -> None:
    response = await admin_app.get(f"/users/{user.id}")
    assert response.status_code == 200, response.json()


async def test_retrieve_username(admin_app: AsyncClient, user: User) -> None:
    response = await admin_app.get(f"/users/username/{user.username}")
    assert response.status_code == 200, response.json()


async def test_retrieve_email(admin_app: AsyncClient, user: User) -> None:
    response = await admin_app.get(f"/users/email/{user.email}")
    assert response.status_code == 200, response.json()


async def test_list(admin_app: AsyncClient, user: User) -> None:
    response = await admin_app.get("/users/")
    assert response.status_code == 200, response.json()
    assert len(response.json()) == 2


async def test_list_by_name(admin_app: AsyncClient, user: User) -> None:
    response = await admin_app.get(
        "/users/", params={"username": user.username}
    )
    assert response.status_code == 200, response.json()
    assert len(response.json()) == 1

    response = await admin_app.get(
        "/users/", params={"username": "incorrect_username"}
    )
    assert not len(response.json())


async def test_user_create(
    admin_app: AsyncClient, user_create: UserCreate
) -> None:
    response = await admin_app.post(
        "/users/create", json=jsonable_encoder(user_create)
    )
    assert response.status_code == 201, response.json()
    assert User(**response.json())


async def test_user_update_roles(
    admin_app: AsyncClient, user: User, user_update_roles: UserUpdate
) -> None:
    assert user.roles[0] == "user"
    response = await admin_app.patch(
        f"/users/{user.id}", json=jsonable_encoder(user_update_roles)
    )
    assert response.status_code == 200, response.json()
    user = User(**response.json())
    assert user.roles[0] == "admin"


async def test_user_delete(
    admin_app: AsyncClient, user: User, db: Database
) -> None:
    response = await admin_app.delete(f"/users/{user.id}")
    assert response.status_code == 204
    assert not response.content
    deleted_user = await db.find(User, {"username": user.username})
    assert deleted_user is None
