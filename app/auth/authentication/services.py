from passlib.context import CryptContext
from starlette import status

from app.auth.authentication.exceptions import PasswordError
from app.auth.database.services import db
from app.auth.users.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str):
    user = await db.find(User, {"username": username}, exception=True)
    if not verify_password(password, user.password):
        raise PasswordError(
            "Incorrect password.", status_code=status.HTTP_401_UNAUTHORIZED
        )
    return user
