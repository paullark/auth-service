from typing import Annotated

from pydantic import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]




# from bson import ObjectId
# from pydantic_core import core_schema
#
#
# class PyObjectId(str):
#     @classmethod
#     def __get_pydantic_core_schema__(
#             cls, _source_type: any, _handler: any
#     ) -> core_schema.CoreSchema:
#         return core_schema.json_or_python_schema(
#             json_schema=core_schema.str_schema(),
#             python_schema=core_schema.union_schema(
#                 [
#                     core_schema.is_instance_schema(ObjectId),
#                     core_schema.chain_schema(
#                         [
#                             core_schema.str_schema(),
#                             core_schema.no_info_plain_validator_function(cls.validate),
#                         ]
#                     )
#                 ]
#             ),
#             serialization=core_schema.plain_serializer_function_ser_schema(
#                 lambda x: str(x)
#             ),
#         )
#
#     @classmethod
#     def validate(cls, value) -> None:
#         if not ObjectId.is_valid(value):
#             raise ValueError("Invalid ObjectId")
#
#
#
# import json
# from typing import Any
#
# # from pydantic_core import core_schema as cs
# # from bson.objectid import ObjectId
# # from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, TypeAdapter
# # from pydantic.json_schema import JsonSchemaValue
#
#
# # class PyObjectId(objectid.ObjectId):
# #     @classmethod
# #     def __get_validators__(cls) -> Iterable[Callable[[Any], PyObjectId]]:
# #         yield cls.validate
# #
# #     @classmethod
# #     def validate(cls, value: Any) -> PyObjectId:
# #         try:
# #             return cls(value)
# #         except InvalidId as error:
# #             raise ValueError(str(error))
# #
# #     @classmethod
# #     def __get_pydantic_json_schema__(cls, field_schema: dict[Any, Any]) -> None:
# #         field_schema.update(type="string")  # pragma: no cover
#
# #
# # class PyObjectId(ObjectId):
# #     # @classmethod
# #     # def __get_pydantic_core_schema__(
# #     #     cls, source_type: Any, handler: GetCoreSchemaHandler
# #     # ) -> cs.CoreSchema:
# #     #     return cs.typed_dict_schema(
# #     #         {
# #     #             'name': cs.typed_dict_field(cs.str_schema()),
# #     #             'age': cs.typed_dict_field(cs.int_schema()),
# #     #         },
# #     #     )
# #
# #     @classmethod
# #     def __get_pydantic_json_schema__(
# #         cls, core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
# #     ) -> JsonSchemaValue:
# #         json_schema = handler(core_schema)
# #         json_schema.update(type="string")
# #         json_schema = handler.resolve_ref_schema(json_schema)
# #
# #         return json_schema
