from datetime import UTC, datetime
from typing import Any, Literal, TypeVar, overload

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.auth.authentication.models import Authorization
from app.auth.config import settings
from app.auth.database.exceptions import (
    DatabaseInsertionError,
    DocumentNotFound,
)
from app.auth.models import SortDirection
from app.auth.users.models import User
from app.auth.verification.models import Verification

Document = TypeVar("Document", User, Authorization, Verification)


class Database:
    def __init__(self, url: str, database_name: str) -> None:
        self.client: AsyncIOMotorClient[Any] = AsyncIOMotorClient(url)
        self.database: AsyncIOMotorDatabase[Any] = self.client[database_name]

    @overload
    async def find(
        self,
        model: type[Document],
        query: dict[str, any],
        exception: Literal[True],
    ) -> Document:
        pass

    @overload
    async def find(
        self,
        model: type[Document],
        query: dict[str, any],
        exception: Literal[False],
    ) -> Document | None:
        pass

    @overload
    async def find(
        self,
        model: type[Document],
        query: dict[str, any],
        exception: bool = False,
    ) -> Document | None:
        pass

    async def find(
        self,
        model: type[Document],
        query: dict[str, any],
        exception: bool = False,
    ) -> Document | None:
        document = await self.database[model.collection()].find_one(query)
        if document is not None:
            return model(**document)

        if exception:
            raise DocumentNotFound(collection=model.collection(), query=query)

        return None

    async def find_many(
        self,
        model: type[Document],
        query: dict[str, Any],
        sort: dict[str, SortDirection] | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> list[Document]:
        documents = self.database[model.collection()].find(
            query, sort=sort, skip=skip, limit=limit
        )
        return [model(**document) async for document in documents]

    async def insert(self, document: Document) -> Document:
        document.created = datetime.now(UTC)
        if not isinstance(document.id, ObjectId):
            document.id = ObjectId(document.id)
        res = await self.database[document.collection()].insert_one(
            document.dict(by_alias=True)
        )
        new_document = await self.find(
            type(document), {"_id": res.inserted_id}
        )
        if new_document:
            return new_document

        raise DatabaseInsertionError(
            document.collection(), {"_id": res.inserted_id}
        )

    async def replace(self, document: Document) -> Document:
        document_dict = document.dict(by_alias=True)
        document_dict.update(
            {
                "_id": ObjectId(document_dict["_id"]),
                "updated": datetime.now(UTC),
            }
        )
        query: dict[str, ObjectId] = {"_id": ObjectId(document.id)}
        if res := await self.database[
            document.collection()
        ].find_one_and_replace(
            query, document_dict, return_document=ReturnDocument.AFTER
        ):
            return type(document)(**res)

        raise DocumentNotFound(collection=document.collection(), query=query)

    async def delete(self, document: Document) -> None:
        res = await self.database[document.collection()].delete_one(
            {"_id": ObjectId(document.id)}
        )

        if res.deleted_count == 1:
            return None

        raise DocumentNotFound(
            collection=document.collection(), query={"_id": document.id}
        )


db = Database(settings.mongo.url, settings.mongo.database_name)
