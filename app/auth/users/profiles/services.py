from pydantic import EmailStr
from starlette import status

from app.auth.authentication.exceptions import (
    AuthenticationError,
    PasswordError,
)
from app.auth.authentication.utils import get_password_hash, verify_password
from app.auth.database.services import db
from app.auth.users.models import User, UserUpdate
from app.auth.users.profiles.models import PasswordUpdate
from app.auth.users.services import CurrentUser, get_user
from app.auth.verification.models import (
    ActionType,
    VerificationAction,
    VerificationOut,
)
from app.auth.verification.services import create_or_update_verification


async def get_current_user(claims: CurrentUser) -> User:
    return await get_user(claims.user_id)


async def change_username(user: User, username: str) -> User:
    if exist_user := await db.find(User, {"username": username}):
        raise AuthenticationError(
            f"User {exist_user.username} already exists."
        )

    return await db.replace(user.model_copy(update={"username": username}))


async def change_email(user: User, email: EmailStr) -> VerificationOut:
    if exist_user := await db.find(User, {"email": email}):
        raise AuthenticationError(f"User {exist_user.email} already exists.")

    action = VerificationAction(
        action_type=ActionType.email, data=UserUpdate(email=email)
    )
    return await create_or_update_verification(user, action, email)


async def change_password(
    passwords: PasswordUpdate, user: User
) -> VerificationOut:
    if not verify_password(passwords.old_password, user.password):
        raise PasswordError(
            "Incorrect password.", status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    action = VerificationAction(
        action_type=ActionType.password,
        data=UserUpdate(password=get_password_hash(passwords.new_password)),
    )

    return await create_or_update_verification(user, action)
