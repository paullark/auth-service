from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from app.auth.database.types import PyObjectId
from app.auth.models import BaseDocument


class TokenType(StrEnum):
    access = "access"
    refresh = "refresh"


class RoleType(StrEnum):
    admin = "admin"
    user = "user"


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


class SignupData(BaseAuthData):
    email: str


class LoginData(BaseAuthData):
    pass


class AuthorizationData(BaseDocument):
    user_id: PyObjectId
    refresh_token: str

    @classmethod
    def collection(cls) -> str:
        return "authorization"
