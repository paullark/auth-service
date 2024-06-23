from enum import StrEnum

from pydantic import BaseModel

from app.auth.database.types import PyObjectId


class TokenType(StrEnum):
    access = "access"
    refresh = "refresh"


class Token(BaseModel):
    access_token: str
    token_type: TokenType


class TokenData(BaseModel):
    user_id: PyObjectId
