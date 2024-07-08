from datetime import datetime
from enum import StrEnum

from pydantic import ConfigDict, EmailStr

from app.auth.models import BaseDocument, Collection


class VerificationAction(StrEnum):
    signup = "signup"
    email = "email"
    password = "password"


class BaseVerification(BaseDocument):
    email: EmailStr
    exp_date: datetime
    resend_date: datetime
    # action: VerificationAction

    model_config = ConfigDict(extra="forbid")


class Verification(BaseVerification):
    code: str

    @classmethod
    def collection(cls):
        return Collection.verifications


class VerificationOut(BaseVerification):
    pass
