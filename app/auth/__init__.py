from fastapi import FastAPI
from fastapi.exceptions import ResponseValidationError
from pydantic import ValidationError
from starlette import status

from app.auth.authentication.exceptions import (
    AuthenticationError,
    NotEnoughPermissionError,
    PasswordError,
    TokenDataError,
)
from app.auth.authentication.routes import auth
from app.auth.config import settings
from app.auth.database.exceptions import (
    DocumentNotFound,
    document_not_found_exception_handler,
)
from app.auth.exceptions import (
    ExceptionHandlersAlias,
    exception_handler,
    pydantic_validation_exception_handler,
)
from app.auth.users.profiles.routes import profiles
from app.auth.users.routes import users
from app.auth.verification.exceptions import VerificationError
from app.auth.verification.routes import verification

exception_handlers: ExceptionHandlersAlias = {
    AuthenticationError: exception_handler,
    VerificationError: exception_handler,
    ValidationError: pydantic_validation_exception_handler,
    ResponseValidationError: pydantic_validation_exception_handler,
    PasswordError: exception_handler,
    TokenDataError: exception_handler,
    NotEnoughPermissionError: exception_handler,
    DocumentNotFound: document_not_found_exception_handler,
}

app = FastAPI(
    exception_handlers=exception_handlers,
    openapi_url="/openapi.json" if settings.debug else "",
)

app.include_router(users)
app.include_router(auth)
app.include_router(verification)
app.include_router(profiles)


@app.get("/health-check", status_code=status.HTTP_204_NO_CONTENT)
async def health_check() -> None:
    return None
