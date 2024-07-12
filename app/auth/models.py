from datetime import datetime
from enum import IntEnum, StrEnum

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.auth.database.types import PyObjectId


class BaseDocument(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    created: datetime | None = None
    updated: datetime | None = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True,
        extra="allow",
    )


class SortDirection(IntEnum):
    ascending = 1
    descending = -1


class ListParams(BaseModel):
    sort_key: str = "_id"
    sort_direction: SortDirection = SortDirection.descending
    skip: int = Field(0, ge=0)
    limit: int = Field(0, ge=0)

    model_config = ConfigDict(extra="forbid", frozen=True)

    def to_query(self) -> dict[str, any]:
        return {
            "sort": {self.sort_key: self.sort_direction},
            "skip": self.skip,
            "limit": self.limit,
        }


class Collection(StrEnum):
    users = "users"
    authorizations = "authorizations"
    verifications = "verifications"
