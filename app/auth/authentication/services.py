from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from bson import ObjectId
from fastapi import Depends
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError
from passlib.context import CryptContext
from pydantic import ValidationError
from starlette import status
from app.auth.config import settings
from app.auth.authentication.exceptions import PasswordError, TokenDataError, NotEnoughPermissionError
from app.auth.authentication.models import TokenPair, BaseTokenData, RoleType, TokenData, TokenType, AuthorizationData
from app.auth.database.services import db
from app.auth.users.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str) -> TokenPair:
    user = await db.find(User, {"username": username}, exception=True)
    if not verify_password(password, user.password):
        raise PasswordError(
            "Incorrect password.", status_code=status.HTTP_401_UNAUTHORIZED
        )
    token_data = BaseTokenData(user_id=user.id, scopes=[RoleType.user])
    return await create_token_pair(token_data)


def create_token(data: BaseTokenData, token_type: TokenType, expires_in: int) -> str:
    token_data = TokenData(
        **data.dict(),
        token_type=token_type,
        exp=datetime.now(timezone.utc) + timedelta(minutes=expires_in)
    )

    return jwt.encode(
        token_data.dict(), settings.secret_key, algorithm=settings.signing_algorithm
    )


async def create_token_pair(data: BaseTokenData) -> TokenPair:
    access_token = create_token(
        data, TokenType.access, settings.access_token_exp_minutes
    )
    refresh_token = create_token(
        data, TokenType.refresh, settings.refresh_token_exp_minutes
    )

    await db.insert(
        AuthorizationData(
            user_id=ObjectId(data.user_id), refresh_token=refresh_token
        )
    )

    return TokenPair(access_token=access_token, refresh_token=refresh_token)


def get_token_data(
    security_scopes: SecurityScopes,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]
) -> TokenData:
    status_401 = status.HTTP_401_UNAUTHORIZED
    try:
        token_data = TokenData(
            **jwt.decode(
                credentials.credentials, settings.secret_key, algorithms=["HS256"]
            )
        )
    except ExpiredSignatureError:
        raise TokenDataError("Signature has expired.", status_401)
    except ValidationError as error:
        raise TokenDataError(str(error), status_401)

    if token_data.token_type != TokenType.access:
        raise TokenDataError("Invalid token type.", status_401)

    for scope in security_scopes.scopes:
        if scope in token_data.scopes:
            return token_data

    raise NotEnoughPermissionError("Not enough permissions.", status_401)
