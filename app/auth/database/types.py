from typing import Annotated

from pydantic import BeforeValidator

"""Reformatting ObjectId to str after docs getting from the database"""
PyObjectId = Annotated[str, BeforeValidator(str)]
