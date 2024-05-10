import sys

from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from sqlalchemy import Select
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import operators as sa_op

from pydantic_sqlalchemy_filterset.core import Model, _Filter, _MultiFieldFilter
from pydantic_sqlalchemy_filterset.types import LookupExpr, MetadataFields, PydanticFieldType

if sys.version_info < (3, 10):
    from typing_extensions import Any, Callable, List, Tuple, Type, Unpack
else:
    from typing import Any, Callable, List, Tuple, Type, Unpack


def _populate_field_info(  # type: ignore[misc]
    filter_class: Type[_Filter],
    field: InstrumentedAttribute[Any],
    strategy: Any = PydanticUndefined,
    default: Any = PydanticUndefined,
    **kwargs: Unpack[PydanticFieldType],
) -> Any:  # Do not change return type
    """Utility function to populate a `FieldInfo` with filtering metadata."""
    field_info: FieldInfo = Field(default=default, **kwargs)  # type: ignore[pydantic-field]
    field_info.metadata.append(
        {
            MetadataFields.SQLALCHEMY_FILTER: True,
            MetadataFields.FILTER_FIELDS: [field],
            MetadataFields.FILTER_CLASS: filter_class,
            MetadataFields.FIELD_STRATEGY: strategy,
        }
    )
    return field_info


def _populate_multifield_info(  # type: ignore[misc]
    filter_class: Type[_MultiFieldFilter],
    fields: List[InstrumentedAttribute[Any]],
    strategy: Any = PydanticUndefined,
    default: Any = PydanticUndefined,
    **kwargs: Unpack[PydanticFieldType],
) -> Any:  # Do not change return type
    """Utility function to populate a `FieldInfo` with filtering metadata."""
    field_info: FieldInfo = Field(default=default, **kwargs)  # type: ignore[pydantic-field]
    field_info.metadata.append(
        {
            MetadataFields.SQLALCHEMY_FILTER: True,
            MetadataFields.FILTER_FIELDS: fields,
            MetadataFields.FILTER_CLASS: filter_class,
            MetadataFields.FIELD_STRATEGY: strategy,
        }
    )
    return field_info


def WhereFilter(  # type: ignore[misc]
    field: InstrumentedAttribute[Any],
    strategy: Any = PydanticUndefined,
    default: Any = PydanticUndefined,
    **kwargs: Unpack[PydanticFieldType],
) -> Any:  # Do not change return type
    """
    Translates to an equality filter in SQL.
    :returns: A new [`FieldInfo`][pydantic.fields.FieldInfo], the return annotation is `Any` so `Field` can be used on
        type annotated fields without causing a typing error.
    """
    filter_class = _Filter
    return _populate_field_info(filter_class=filter_class, field=field, strategy=strategy, default=default, **kwargs)


class _IsFilter(_Filter):
    @property
    def lookup_expr(self) -> LookupExpr:
        return sa_op.is_


def IsFilter(  # type: ignore[misc]
    field: InstrumentedAttribute[Any],
    strategy: Any = PydanticUndefined,
    default: Any = PydanticUndefined,
    **kwargs: Unpack[PydanticFieldType],
) -> Any:  # Do not change return type
    """
    Translates to an `IS` filter in SQL.
    :returns: A new [`FieldInfo`][pydantic.fields.FieldInfo], the return annotation is `Any` so `Field` can be used on
        type annotated fields without causing a typing error.
    """
    filter_class = _IsFilter
    return _populate_field_info(filter_class=filter_class, field=field, strategy=strategy, default=default, **kwargs)


class _InFilter(_Filter):
    @property
    def lookup_expr(self) -> LookupExpr:
        return sa_op.in_op


def InFilter(  # type: ignore[misc]
    field: InstrumentedAttribute[Any],
    strategy: Any = PydanticUndefined,
    default: Any = PydanticUndefined,
    **kwargs: Unpack[PydanticFieldType],
) -> Any:  # Do not change return type
    """
    Translates to an `IN` filter in SQL.
    :returns: A new [`FieldInfo`][pydantic.fields.FieldInfo], the return annotation is `Any` so `Field` can be used on
        type annotated fields without causing a typing error.
    """
    filter_class = _InFilter
    return _populate_field_info(filter_class=filter_class, field=field, strategy=strategy, default=default, **kwargs)


class _LikeFilter(_Filter):
    @property
    def lookup_expr(self) -> LookupExpr:
        return sa_op.like_op


def LikeFilter(  # type: ignore[misc]
    field: InstrumentedAttribute[Any],
    strategy: Any = PydanticUndefined,
    default: Any = PydanticUndefined,
    **kwargs: Unpack[PydanticFieldType],
) -> Any:  # Do not change return type
    """
    Translates to a `LIKE` filter in SQL.
    :returns: A new [`FieldInfo`][pydantic.fields.FieldInfo], the return annotation is `Any` so `Field` can be used on
        type annotated fields without causing a typing error.
    """
    filter_class = _LikeFilter
    return _populate_field_info(filter_class=filter_class, field=field, strategy=strategy, default=default, **kwargs)


class _ILikeFilter(_Filter):
    @property
    def lookup_expr(self) -> LookupExpr:
        return sa_op.ilike_op


def ILikeFilter(  # type: ignore[misc]
    field: InstrumentedAttribute[Any],
    strategy: Any = PydanticUndefined,
    default: Any = PydanticUndefined,
    **kwargs: Unpack[PydanticFieldType],
) -> Any:  # Do not change return type
    """
    Translates to an insensitive ILIKE filter in SQL.
    :returns: A new [`FieldInfo`][pydantic.fields.FieldInfo], the return annotation is `Any` so `Field` can be used
        on type annotated fields without causing a typing error.
    """
    filter_class = _ILikeFilter
    return _populate_field_info(filter_class=filter_class, field=field, strategy=strategy, default=default, **kwargs)


class _SubstringFilter(_ILikeFilter):
    def filter(self, query: Select[Tuple[Model]], value: Any) -> Select[Tuple[Model]]:  # type: ignore[misc]
        value = f"%{value}%"
        return super().filter(query, value)


def SubstringFilter(  # type: ignore[misc]
    field: InstrumentedAttribute[Any],
    strategy: Any = PydanticUndefined,
    default: Any = PydanticUndefined,
    **kwargs: Unpack[PydanticFieldType],
) -> Any:  # Do not change return type
    """
    Translates to an ILike filter surrounding the value with '%' in SQL.
    :returns: A new [`FieldInfo`][pydantic.fields.FieldInfo], the return annotation is `Any` so `Field` can be used on
        type annotated fields without causing a typing error.
    """
    filter_class = _SubstringFilter
    return _populate_field_info(filter_class=filter_class, field=field, strategy=strategy, default=default, **kwargs)


class _LTEFilter(_Filter):
    @property
    def lookup_expr(self) -> LookupExpr:
        return sa_op.le


def LTEFilter(  # type: ignore[misc]
    field: InstrumentedAttribute[Any],
    strategy: Any = PydanticUndefined,
    default: Any = PydanticUndefined,
    **kwargs: Unpack[PydanticFieldType],
) -> Any:
    filter_class = _LTEFilter
    return _populate_field_info(filter_class=filter_class, field=field, strategy=strategy, default=default, **kwargs)


# FilterValue transformer type - how to type this?
def FilterValueMapper(callable: Callable[..., Any], field_info: FieldInfo) -> Any:  # type: ignore[misc]
    """
    A simple mapper that allows the value of a filter to be a user-supplied subquery.
    """
    field_info.metadata[-1][MetadataFields.VALUE_MAPPER] = callable
    return field_info


class _MultiFieldSubstringFilter(_MultiFieldFilter):
    @property
    def lookup_expr(self) -> LookupExpr:
        return sa_op.ilike_op

    def filter(self, query: Select[Tuple[Model]], value: Any) -> Select[Tuple[Model]]:  # type: ignore[misc]
        value = f"%{value}%"
        return super().filter(query, value)


def MultiFieldSubstringFilter(  # type: ignore[misc]
    fields: List[InstrumentedAttribute[Any]],
    strategy: Any = PydanticUndefined,
    default: Any = PydanticUndefined,
    **kwargs: Unpack[PydanticFieldType],
) -> Any:  # Do not change return type
    """
    Translates to an ilike with %_% on multiple fields.
    """
    filter_class = _MultiFieldSubstringFilter
    return _populate_multifield_info(
        filter_class=filter_class, fields=fields, strategy=strategy, default=default, **kwargs
    )
