import random
from datetime import datetime, timezone, timedelta

from bson import ObjectId
from starlette import status

from app.auth.authentication.services import authenticate_user
from app.auth.config import settings
from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, MessageSchema, MessageType, FastMail
from pydantic import EmailStr

from app.auth.database.services import db
from app.auth.database.types import PyObjectId
from app.auth.users.services import get_user_by_email
from app.auth.verification.exceptions import VerificationError
from app.auth.verification.models import VerificationOut, Verification, BaseVerification

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail.username,
    MAIL_PASSWORD=settings.mail.password,
    MAIL_FROM=settings.mail.mail_from,
    MAIL_PORT=settings.mail.port,
    MAIL_SERVER=settings.mail.server,
    MAIL_STARTTLS=settings.mail.starttls,
    MAIL_SSL_TLS=settings.mail.ssl_tls,
    USE_CREDENTIALS=settings.mail.use_credentials,
    VALIDATE_CERTS=settings.mail.validate_certs
)


def send_email(
        background_tasks: BackgroundTasks, email: EmailStr, code: str
) -> None:
    message = MessageSchema(
        subject="Pau App Verification Code",
        recipients=[email],
        body=code,
        subtype=MessageType.html
    )

    fast_mail = FastMail(conf)
    background_tasks.add_task(fast_mail.send_message, message, None)


def generate_verification_code() -> str:
    return "".join(random.sample("0123456789", settings.auth.verification_code_length))


async def create_verification(background_tasks, email: EmailStr) -> VerificationOut:
    verification_data = BaseVerification(
        email=email,
        exp_date=datetime.now(timezone.utc) + timedelta(
            minutes=settings.auth.verification_exp_minutes
        ),
        resend_date=datetime.now(timezone.utc) + timedelta(
            minutes=settings.auth.verification_resend_minutes
        ),
        created=datetime.now(timezone.utc)
    )

    verification = Verification(**verification_data.dict(), code=generate_verification_code())
    await db.insert(verification)
    send_email(background_tasks, verification.email, verification.code)

    return VerificationOut(**verification_data.dict())


async def confirm_verification(verification_id: PyObjectId, code: str):
    verification = db.find(Verification, {"_id": ObjectId(verification_id)}, exception=True)

    if verification.code != code:
        raise VerificationError(
            "Incorrect verification code.", status.HTTP_401_UNAUTHORIZED
        )

    if datetime.now(timezone.utc) > verification.exp_date:
        raise VerificationError(
            "Verification code expired.", status.HTTP_401_UNAUTHORIZED
        )

    if verification.updated and datetime.now(timezone.utc) < verification.updated:
        raise VerificationError(
            "Resend time is not expired.", status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    elif datetime.now(timezone.utc) < verification.created:
        raise VerificationError(
            "Resend time is not expired.", status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    user = await get_user_by_email(verification.email)
    user.is_active = True

    return await authenticate_user(await db.replace(user))
