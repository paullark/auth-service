from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, Annotated

from bson import objectid
from bson.errors import InvalidId
from pydantic import BeforeValidator


class ObjectId(objectid.ObjectId):
    # @classmethod
    # def __get_validators__(cls) -> Iterable[Callable[[Any], ObjectId]]:
    #     yield cls.validate
    #
    # @classmethod
    # def validate(cls, value: Any) -> ObjectId:
    #     try:
    #         return cls(value)
    #     except InvalidId as error:
    #         raise ValueError(str(error))

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: dict[Any, Any]) -> None:
        field_schema.update(type="string")  # pragma: no cover


PyObjectId = Annotated[str, BeforeValidator(str)]
