import asyncio
import random
from datetime import UTC, datetime, timedelta

from bson import ObjectId
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from starlette import status

from app.auth.config import settings
from app.auth.database.services import db
from app.auth.database.types import PyObjectId
from app.auth.users.models import User
from app.auth.users.services import update_user
from app.auth.verification.exceptions import VerificationError
from app.auth.verification.models import (
    BaseVerification,
    Verification,
    VerificationAction,
    VerificationOut,
)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail.username,
    MAIL_PASSWORD=settings.mail.password,
    MAIL_FROM=settings.mail.mail_from,
    MAIL_PORT=settings.mail.port,
    MAIL_SERVER=settings.mail.server,
    MAIL_STARTTLS=settings.mail.starttls,
    MAIL_SSL_TLS=settings.mail.ssl_tls,
    USE_CREDENTIALS=settings.mail.use_credentials,
    VALIDATE_CERTS=settings.mail.validate_certs,
)


async def send_email(email: EmailStr, code: str) -> None:
    message = MessageSchema(
        subject="Pau App Verification Code",
        recipients=[email],
        body=code,
        subtype=MessageType.html,
    )

    fast_mail = FastMail(conf)
    await fast_mail.send_message(message)


def generate_verification_code() -> str:
    return "".join(
        random.sample("0123456789", settings.auth.verification_code_length)
    )


async def create_or_update_verification(
    user: User, action: VerificationAction, email: EmailStr | None = None
) -> VerificationOut:
    exp_date = datetime.now(UTC) + timedelta(
        minutes=settings.auth.verification_exp_minutes
    )
    resend_date = datetime.now(UTC) + timedelta(
        minutes=settings.auth.verification_resend_minutes
    )

    if verification := await db.find(
        Verification,
        {"user._id": user.id, "action.action_type": action.action_type},
    ):

        if datetime.utcnow() < verification.resend_date:
            raise VerificationError(
                "Resend time is not expired.",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        verification.code = generate_verification_code()
        verification.exp_date = exp_date
        verification.resend_date = resend_date
        verification.action.data = action.data
        verification = await db.replace(verification)

        await asyncio.create_task(
            send_email(email or verification.user.email, verification.code)
        )

        return VerificationOut(**verification.model_dump(exclude={"code"}))

    verification_data = BaseVerification(
        user=user,
        exp_date=exp_date,
        resend_date=resend_date,
        created=datetime.now(UTC),
        action=action,
    )

    verification = Verification(
        **verification_data.model_dump(), code=generate_verification_code()
    )
    await db.insert(verification)
    await asyncio.create_task(
        send_email(email or verification.user.email, verification.code)
    )

    return VerificationOut(**verification_data.model_dump())


async def confirm_verification(verification_id: PyObjectId, code: str) -> User:
    verification = await db.find(
        Verification, {"_id": ObjectId(verification_id)}, True
    )

    if datetime.utcnow() > verification.exp_date:
        raise VerificationError(
            "Verification code expired.", status.HTTP_401_UNAUTHORIZED
        )

    if verification.code != code:
        raise VerificationError(
            "Incorrect verification code.", status.HTTP_401_UNAUTHORIZED
        )

    return await update_user(verification.user, verification.action.data)
