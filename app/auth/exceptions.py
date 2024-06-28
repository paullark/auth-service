from typing import TypeAlias, Callable

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from requests import Request
from starlette import status
from starlette.responses import JSONResponse


class BaseAuthException(Exception):
    def __init__(
            self, message: str, status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    ) -> None:
        self.message = message
        self.status_code = status_code


def exception_handler(
    _request: Request,
    exception: BaseAuthException,
) -> JSONResponse:
    return JSONResponse(
        content={"error": type(exception).__name__, "detail": exception.message},
        status_code=exception.status_code,
    )


def pydantic_validation_exception_handler(
    _request: Request, exception: ValidationError
) -> JSONResponse:
    errors = jsonable_encoder(exception.errors())
    return JSONResponse(
        content={"error": "validation_error", "detail": errors},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


ExceptionHandlersAlias: TypeAlias = dict[
    int | type[Exception], Callable[[Request, any], any]
]
