from enum import StrEnum

from pydantic import BaseModel

from app.auth.database.types import PyObjectId


class TokenType(StrEnum):
    access = "access"
    refresh = "refresh"


class RoleType(StrEnum):
    admin = "admin"
    user = "user"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    user_id: PyObjectId
    token_type: TokenType
    role: RoleType


class BaseAuthData(BaseModel):
    username: str
    password: str


class SignupData(BaseAuthData):
    email: str


class LoginData(BaseAuthData):
    pass
