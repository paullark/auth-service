from pydantic import Extra, ConfigDict

from app.auth.models import BaseDocument


class VerificationData(BaseDocument):
    email: str
    exp_delta: int
    resend_delta: int
    code: int

    model_config = ConfigDict(extra=Extra.forbid)
