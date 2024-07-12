from requests import Request
from starlette import status
from starlette.responses import JSONResponse


class DatabaseException(Exception):
    pass


class DocumentNotFound(DatabaseException):
    def __init__(self, collection: str, query: dict[str, any]) -> None:
        self.collection = collection
        self.query = query


def document_not_found_exception_handler(
    _request: Request, exception: DocumentNotFound
) -> JSONResponse:
    content = {
        "error": "document_not_found",
        "detail": {
            "collection": exception.collection,
            "query": str(exception.query),
        },
    }

    return JSONResponse(content, status.HTTP_404_NOT_FOUND)
