from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from app.auth.models import BaseDocument, Collection
from app.auth.users.models import User, UserUpdate


class ActionType(StrEnum):
    signup = "signup"
    email = "email"
    password = "password"


class VerificationAction(BaseModel):
    action_type: ActionType
    data: UserUpdate


class BaseVerification(BaseDocument):
    user: User
    exp_date: datetime
    resend_date: datetime
    action: VerificationAction

    model_config = ConfigDict(extra="forbid")


class Verification(BaseVerification):
    code: str

    @classmethod
    def collection(cls):
        return Collection.verifications


class VerificationOut(BaseVerification):
    pass
