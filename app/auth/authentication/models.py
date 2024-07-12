from pydantic import BaseModel, ConfigDict, EmailStr

from app.auth.database.types import PyObjectId
from app.auth.models import BaseDocument, Collection


class BaseAuthData(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(extra="forbid")


class SignupData(BaseAuthData):
    email: EmailStr


class LoginData(BaseAuthData):
    pass


class Authorization(BaseDocument):
    user_id: PyObjectId
    refresh_token: str

    @classmethod
    def collection(cls) -> str:
        return Collection.authorizations
