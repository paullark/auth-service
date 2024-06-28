from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.auth.config import settings
from app.auth.database.exceptions import DocumentNotFound
from app.auth.models import SortDirection


class Database:
    def __init__(self, url: str, database_name: str) -> None:
        self.client = AsyncIOMotorClient(url)
        self.database: AsyncIOMotorDatabase = self.client[database_name]

    async def find[D](
            self, model: type[D], query: dict[str, any], exception: bool = False
    ) -> D | None:
        document = await self.database[model.collection()].find_one(query)
        if document is not None:
            return model(**document)
        if exception:
            raise DocumentNotFound(collection=model.collection(), query=query)
        return None

    async def find_many[D](
            self,
            model: type[D],
            query: dict[str, any],
            sort: dict[str, SortDirection] | None = None,
            skip: int | None = None,
            limit: int | None = None
    ) -> list[D]:
        documents = self.database[model.collection()].find(
            query, sort=sort, skip=skip, limit=limit
        )
        return [model(**document) async for document in documents]

    async def insert[D](self, document: D) -> D:
        document.created = datetime.now(timezone.utc)
        res = await self.database[document.collection()].insert_one(
            document.dict(by_alias=True)
        )
        return await self.find(
            type(document), {"_id": res.inserted_id}, exception=True
        )

    async def replace[D](self, document: D) -> D:
        document_dict = document.dict(by_alias=True)
        document_dict.update(
            {
                "_id": ObjectId(document_dict["_id"]),
                "updated": datetime.now(timezone.utc)
            }
        )
        res = await self.database[document.collection()].find_one_and_replace(
            {"_id": ObjectId(document.id)},
            document_dict,
            return_document=ReturnDocument.AFTER
        )

        return type(document)(**res)

    async def delete[D](self, document: D) -> None:
        res = await self.database[document.collection()].delete_one(
            {"_id": ObjectId(document.id)}
        )

        if res.deleted_count == 1:
            return None

        raise DocumentNotFound(
            collection=document.collection(), query={"_id": document.id}
        )


db = Database(settings.mongo.url, settings.mongo.database_name)
