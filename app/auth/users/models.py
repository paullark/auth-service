from enum import StrEnum

from pydantic import BaseModel, Extra, ConfigDict, EmailStr

from app.auth.models import BaseDocument, Collection


class RoleType(StrEnum):
    user = "user"
    admin = "admin"


class BaseUser(BaseModel):
    username: str
    password: str
    email: EmailStr
    roles: list[RoleType]

    model_config = ConfigDict(extra=Extra.forbid)


class User(BaseUser, BaseDocument):

    @classmethod
    def collection(cls):
        return Collection.users


class UserCreate(BaseUser):
    pass


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    email: EmailStr | None = None
    roles: list[RoleType] | None = None

    model_config = ConfigDict(extra=Extra.forbid)
