from bson import ObjectId
from pydantic import Field

from app.auth.models import BaseDocument


class User(BaseDocument):
    username: str
    password: str
    email: str

    class Config(BaseDocument.Config):
        collection = "users"


class UserCreate(User):
    pass


class UserUpdate(User):
    pass
