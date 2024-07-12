from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from app.auth.database.types import PyObjectId
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
