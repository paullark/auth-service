from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.auth.config import settings
from app.auth.models import BaseDocument


class Database:
    def __init__(self, url: str, database_name: str) -> None:
        # self.url = url
        # self.database_name = database_name
        self.client = AsyncIOMotorClient(url)
        self.database: AsyncIOMotorDatabase = self.client[database_name]

    async def find(
            self, model: type[BaseDocument], query: dict[str, Any]
    ) -> BaseDocument | None:
        document = await self.database[model.Config.collection].find_one(query)
        if document is not None:
            return model(**document)

        return None


db = Database(settings.mongo.url, settings.mongo.database_name)
