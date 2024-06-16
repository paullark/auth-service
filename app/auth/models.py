from datetime import datetime
from typing import Callable

from bson.objectid import ObjectId
from pydantic import BaseModel, Field

from app.auth.database.types import PyObjectId


# from app.auth.database.coders import JSON_ENCODERS
# from app.auth.database.types import ObjectId


class BaseDocument(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")

    class Config:
        collection: str
        arbitrary_types_allowed = True
        # json_encoders: dict[type[any], Callable[[any], any]] = {ObjectId: str}


