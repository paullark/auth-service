from typing import Any, Callable, Coroutine, TypeAlias

from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class BaseAuthException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
    ) -> None:
        self.message = message
        self.status_code = status_code


async def exception_handler(
    _request: Request,
    exception: BaseAuthException,
) -> JSONResponse:
    return JSONResponse(
        content={
            "error": type(exception).__name__,
            "detail": exception.message,
        },
        status_code=exception.status_code,
    )


async def pydantic_validation_exception_handler(
    _request: Request, exception: ValidationError
) -> JSONResponse:
    errors = jsonable_encoder(exception.errors())
    return JSONResponse(
        content={"error": "validation_error", "detail": errors},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


ExceptionHandlersAlias: TypeAlias = (
    dict[
        int | type[Exception],
        Callable[[Request, Any], Coroutine[Any, Any, Response]],
    ]
    | None
)
