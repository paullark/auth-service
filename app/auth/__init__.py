from fastapi import FastAPI
from starlette import status

from app.auth.config import settings
from app.auth.users.routes import users

exception_handlers = {}

app = FastAPI(exception_handlers=exception_handlers, openapi_url="/openapi.json" if settings.debug else "")

app.include_router(users)


@app.get("/health-check", status_code=status.HTTP_204_NO_CONTENT)
async def health_check() -> None:
    return None
