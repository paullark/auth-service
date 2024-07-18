from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from bson import ObjectId
from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    SecurityScopes,
)
from jwt import ExpiredSignatureError
from starlette import status

from app.auth.authentication.exceptions import (
    NotEnoughPermissionError,
    TokenDataError,
)
from app.auth.authentication.models import Authorization
from app.auth.authentication.tokens.models import (
    BaseTokenData,
    TokenData,
    TokenPair,
    TokenType,
)
from app.auth.config import settings
from app.auth.database.services import db
from app.auth.users.models import User

status_401 = status.HTTP_401_UNAUTHORIZED


def create_token(
    data: BaseTokenData, token_type: TokenType, expires_in: int
) -> str:
    """
    Create token includes "user_id", "scopes", "token_type", and "expires_in"
    Encode and return token as a string
    """
    token_data = TokenData(
        **data.model_dump(),
        token_type=token_type,
        exp=datetime.now(timezone.utc) + timedelta(minutes=expires_in),
    )
    token: str = jwt.encode(
        token_data.model_dump(),
        settings.secret_key,
        algorithm=settings.auth.signing_algorithm,
    )
    return token


def create_token_pair(data: BaseTokenData) -> TokenPair:
    """
    Create access and refresh tokens.
    Return TokenPair instance.
    """
    access_token = create_token(
        data, TokenType.access, settings.auth.access_token_exp_minutes
    )
    refresh_token = create_token(
        data, TokenType.refresh, settings.auth.refresh_token_exp_minutes
    )

    return TokenPair(access_token=access_token, refresh_token=refresh_token)


def decode_token(token: str) -> TokenData:
    """
    Decode token and return TokenData instance includes
    "user_id", "scopes", "token_type", and "expires_in"
    """
    try:
        token_data = TokenData(
            **jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.auth.signing_algorithm],
            )
        )
    except ExpiredSignatureError:
        raise TokenDataError("Signature has expired.", status_401)
    except Exception as error:
        raise TokenDataError(str(error), status_401)

    return token_data


def get_token_data(
    security_scopes: SecurityScopes,
    credentials: Annotated[
        HTTPAuthorizationCredentials, Depends(HTTPBearer())
    ],
) -> TokenData:
    """
    Get token from header and call decode func.
    Check credentials against security scopes and verify token type.
    Return the token data instance if valid.
    """
    token_data = decode_token(credentials.credentials)

    if token_data.token_type != TokenType.access:
        raise TokenDataError("Invalid token type.", status_401)

    for scope in security_scopes.scopes:
        if scope in token_data.scopes:
            return token_data

    raise NotEnoughPermissionError("Not enough permissions.", status_401)


async def refresh_token_pair(token: str) -> TokenPair:
    """
    Check the token is valid and its type is refresh.
    Create and return a new token pair.
    """
    token_data = decode_token(token)
    if token_data.token_type != TokenType.refresh:
        raise TokenDataError("Invalid token type.", status_401)

    user = await db.find(User, {"_id": ObjectId(token_data.user_id)}, True)

    authorization = await db.find(
        Authorization, {"refresh_token": token}, True
    )

    token_pair = create_token_pair(
        BaseTokenData(user_id=user.id, scopes=user.roles)
    )
    authorization.refresh_token = token_pair.refresh_token
    await db.replace(authorization)

    return token_pair


async def authenticate_user(user: User) -> TokenPair:
    """
    Create token data.
    Insert authorization instance with refresh token into the database.
    Return new token pair
    """
    token_data = BaseTokenData(user_id=user.id, scopes=user.roles)
    token_pair = create_token_pair(token_data)

    await db.insert(
        Authorization(
            user_id=ObjectId(user.id), refresh_token=token_pair.refresh_token
        )
    )
    return token_pair


async def delete_authorization(token: str) -> None:
    """Find and delete authorization from database by refresh token"""
    authorization = await db.find(
        Authorization, {"refresh_token": token}, True
    )
    await db.delete(authorization)
