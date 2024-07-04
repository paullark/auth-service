from datetime import datetime

from pydantic import ConfigDict, EmailStr

from app.auth.models import BaseDocument, Collection


class BaseVerification(BaseDocument):
    email: EmailStr
    exp_date: datetime
    resend_date: datetime

    model_config = ConfigDict(extra="forbid")


class Verification(BaseVerification):
    code: str

    @classmethod
    def collection(cls):
        return Collection.verifications


class VerificationOut(BaseVerification):
    pass
