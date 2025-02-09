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
    """ODM for connecting to MongoDB and general methods to use it"""

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
        """
        @overload to specify for mypy,
        if the exception arg is true, return value never be None.
        """
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
        """
        The method to find a document.
        Params:
            model (type[Document]) : The model to get a collection
            and validate result;
            exception (bool) : Raise exception if document is not found,
            return None if false
        Return the instance of model
        """
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
        """
        The method to insert a document.
        If the document id is str then
        it will be replaced with the ObjectId
        Params:
            document (Document): the instance of
            User, Authorization or Verification
        Return the inserted document or raise DatabaseInsertionError
        """
        document.created = datetime.now(UTC)

        # Check if an inserting document id is ObjectId
        if not isinstance(document.id, ObjectId):
            document.id = ObjectId(document.id)
        res = await self.database[document.collection()].insert_one(
            document.model_dump(by_alias=True)
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
        """
        The method to update a document.
        Params:
            document (Document): the instance that should be updated
        Return the updated document of raise DocumentNotFound
        """
        document_dict = document.model_dump(by_alias=True)
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
