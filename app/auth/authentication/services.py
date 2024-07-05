from starlette import status

from app.auth.authentication.tokens.models import TokenPair
from app.auth.authentication.tokens.services import authenticate_user
from app.auth.authentication.utils import verify_password
from app.auth.authentication.exceptions import PasswordError, AuthenticationError
from app.auth.authentication.models import SignupData
from app.auth.database.services import db
from app.auth.users.models import User, UserCreate, RoleType
from app.auth.users.services import create_user
from app.auth.verification.models import VerificationOut
from app.auth.verification.services import create_or_update_verification


async def signup_user(
        background_tasks, signup_data: SignupData
) -> VerificationOut:
    if user := await db.find(
            User,
            {
                "$or": [
                    {"username": signup_data.username}, {"email": signup_data.email}
                ]
            }
    ):
        if user.is_active:
            raise AuthenticationError(f"User {user.username} already exists.")

    else:
        await create_user(UserCreate(**signup_data.dict(), roles=[RoleType.user]))

    return await create_or_update_verification(background_tasks, signup_data.email)


async def login_user(username: str, password: str) -> TokenPair:
    user = await db.find(User, {"username": username}, exception=True)
    if not user.is_active:
        raise AuthenticationError("User is not verified.", status.HTTP_401_UNAUTHORIZED)

    if not verify_password(password, user.password):
        raise PasswordError("Incorrect password.", status.HTTP_401_UNAUTHORIZED)

    return await authenticate_user(user)
