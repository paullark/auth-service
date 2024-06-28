from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr, ConfigDict, Extra

from app.auth.database.types import PyObjectId
from app.auth.models import BaseDocument, Collection
from app.auth.users.models import RoleType


class TokenType(StrEnum):
    access = "access"
    refresh = "refresh"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class BaseTokenData(BaseModel):
    user_id: PyObjectId
    scopes: list[RoleType]


class TokenData(BaseTokenData):
    token_type: TokenType
    exp: datetime


class BaseAuthData(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(extra=Extra.forbid)


class SignupData(BaseAuthData):
    email: EmailStr


class LoginData(BaseAuthData):
    pass


class Authorization(BaseDocument):
    user_id: PyObjectId
    refresh_token: str

    @classmethod
    def collection(cls) -> str:
        return Collection.authorizations
