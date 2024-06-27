from enum import StrEnum

from pydantic import BaseModel, Extra, ConfigDict

from app.auth.models import BaseDocument


class RoleType(StrEnum):
    user = "user"
    admin = "admin"


class BaseUser(BaseModel):
    username: str
    password: str
    email: str
    roles: list[RoleType]

    model_config = ConfigDict(
        extra=Extra.forbid
    )


class User(BaseUser, BaseDocument):

    @classmethod
    def collection(cls):
        return "users"


class UserCreate(BaseUser):
    pass


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    email: str | None = None
    roles: list[RoleType] | None = None

    model_config = ConfigDict(
        extra=Extra.forbid
    )
