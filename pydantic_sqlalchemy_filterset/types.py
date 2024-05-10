import sys
from enum import Enum

from pydantic import AliasChoices, AliasPath
from pydantic_core import PydanticUndefined
from sqlalchemy.sql import operators as sa_op

if sys.version_info < (3, 10):
    from typing_extensions import Any, Callable, Dict, List, Literal, NotRequired, TypedDict, Union
else:
    from typing import Any, Callable, Dict, List, Literal, NotRequired, TypedDict, Union

_Unset: Any = PydanticUndefined  # type: ignore[misc]


class PydanticFieldType(TypedDict):
    default_factory: NotRequired[Union[Callable[[], Any], None]]
    alias: NotRequired[Union[str, None]]
    alias_priority: NotRequired[Union[int, None]]
    validation_alias: NotRequired[Union[str, AliasPath, AliasChoices, None]]
    serialization_alias: NotRequired[Union[str, None]]
    title: NotRequired[Union[str, None]]
    description: NotRequired[Union[str, None]]
    examples: NotRequired[Union[List[Any], None]]
    exclude: NotRequired[Union[bool, None]]
    discriminator: NotRequired[Union[str, None]]
    json_schema_extra: NotRequired[Union[Dict[str, Any], Callable[[Dict[str, Any]], None], None]]
    frozen: NotRequired[Union[bool, None]]
    validate_default: NotRequired[Union[bool, None]]
    repr: NotRequired[bool]
    init_var: NotRequired[Union[bool, None]]
    kw_only: NotRequired[Union[bool, None]]
    pattern: NotRequired[Union[str, None]]
    strict: NotRequired[Union[bool, None]]
    gt: NotRequired[Union[float, None]]
    ge: NotRequired[Union[float, None]]
    lt: NotRequired[Union[float, None]]
    le: NotRequired[Union[float, None]]
    multiple_of: NotRequired[Union[float, None]]
    allow_inf_nan: NotRequired[Union[bool, None]]
    max_digits: NotRequired[Union[int, None]]
    decimal_places: NotRequired[Union[int, None]]
    min_length: NotRequired[Union[int, None]]
    max_length: NotRequired[Union[int, None]]
    union_mode: NotRequired[Literal["smart", "left_to_right"]]


class MetadataFields(Enum):
    SQLALCHEMY_FILTER = "sqlalchemy_filter"
    FILTER_CLASS = "filter_class"
    FILTER_FIELDS = "filter_field"
    FIELD_STRATEGY = "field_strategy"
    VALUE_MAPPER = "value_mapper"


LookupExpr = sa_op.OperatorType
