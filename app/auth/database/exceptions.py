from typing import Any

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse


class DatabaseException(Exception):
    def __init__(self, collection: str, query: dict[str, Any]) -> None:
        self.collection = collection
        self.query = query


class DatabaseInsertionError(DatabaseException):
    pass


class DocumentNotFound(DatabaseException):
    pass


async def db_exception_handler(
    _request: Request, exception: DatabaseException
) -> JSONResponse:
    content = {
        "error": exception.__class__.__name__,
        "detail": {
            "collection": exception.collection,
            "query": str(exception.query),
        },
    }

    return JSONResponse(content=content, status_code=status.HTTP_404_NOT_FOUND)
