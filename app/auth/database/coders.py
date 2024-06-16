from typing import Any, Callable

from bson.objectid import ObjectId

JSON_ENCODERS: dict[type[Any], Callable[[Any], Any]] = {ObjectId: str}
