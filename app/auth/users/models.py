from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.auth.config import settings
from app.auth.models import BaseDocument, Collection


class RoleType(StrEnum):
    user = "user"
    admin = "admin"


class BaseUser(BaseModel):
    username: str
    password: str = Field(min_length=settings.auth.password_min_length)
    email: EmailStr
    roles: list[RoleType]

    model_config = ConfigDict(extra="forbid")


class User(BaseUser, BaseDocument):
    is_active: bool = False

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
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid")
