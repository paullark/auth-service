from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from bson import ObjectId
from fastapi import Depends
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError
from pydantic import ValidationError
from starlette import status

from app.auth.authentication.models import Authorization
from app.auth.config import settings
from app.auth.authentication.exceptions import TokenDataError, NotEnoughPermissionError
from app.auth.authentication.tokens.models import (
    TokenPair, BaseTokenData, TokenData, TokenType
)
from app.auth.database.services import db
from app.auth.users.models import User

status_401 = status.HTTP_401_UNAUTHORIZED


def create_token(data: BaseTokenData, token_type: TokenType, expires_in: int) -> str:
    token_data = TokenData(
        **data.dict(),
        token_type=token_type,
        exp=datetime.now(timezone.utc) + timedelta(minutes=expires_in)
    )
    print("****")
    print("*", settings.secret_key)
    return jwt.encode(
        token_data.dict(), settings.secret_key, algorithm=settings.auth.signing_algorithm
    )


def create_token_pair(data: BaseTokenData) -> TokenPair:
    access_token = create_token(
        data, TokenType.access, settings.auth.access_token_exp_minutes
    )
    refresh_token = create_token(
        data, TokenType.refresh, settings.auth.refresh_token_exp_minutes
    )

    return TokenPair(access_token=access_token, refresh_token=refresh_token)


def decode_token(token: str) -> TokenData:
    try:
        token_data = TokenData(
            **jwt.decode(
                token, settings.secret_key, algorithms=[settings.auth.signing_algorithm]
            )
        )
    except ExpiredSignatureError:
        raise TokenDataError("Signature has expired.", status_401)
    except ValidationError as error:
        raise TokenDataError(str(error), status_401)
    except Exception as error:
        raise TokenDataError(str(error), status_401)

    return token_data


def get_token_data(
    security_scopes: SecurityScopes,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]
) -> TokenData:
    token_data = decode_token(credentials.credentials)

    if token_data.token_type != TokenType.access:
        raise TokenDataError("Invalid token type.", status_401)

    for scope in security_scopes.scopes:
        if scope in token_data.scopes:
            return token_data

    raise NotEnoughPermissionError("Not enough permissions.", status_401)


async def refresh_token_pair(token: str) -> TokenPair:
    token_data = decode_token(token)
    if token_data.token_type != TokenType.refresh:
        raise TokenDataError("Invalid token type.", status_401)

    user = await db.find(User, {"_id": ObjectId(token_data.user_id)}, exception=True)
    authorization = await db.find(Authorization, {"refresh_token": token}, exception=True)
    token_pair = create_token_pair(
        BaseTokenData(user_id=user.id, scopes=user.roles)
    )
    authorization.refresh_token = token_pair.refresh_token
    await db.replace(authorization)

    return token_pair


async def authenticate_user(user: User) -> TokenPair:
    token_data = BaseTokenData(user_id=user.id, scopes=user.roles)
    token_pair = create_token_pair(token_data)

    await db.insert(
        Authorization(
            user_id=ObjectId(user.id), refresh_token=token_pair.refresh_token
        )
    )
    return token_pair


async def delete_authorization(token: str) -> None:
    authorization = await db.find(Authorization, {"refresh_token": token}, exception=True)
    await db.delete(authorization)
