from __future__ import annotations

import functools
import sys

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from sqlalchemy import Select
from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute
from sqlalchemy.sql import operators as sa_op

from pydantic_sqlalchemy_filterset.strategies import BaseStrategy, StrategyType
from pydantic_sqlalchemy_filterset.types import LookupExpr, MetadataFields

if sys.version_info < (3, 10):
    from typing_extensions import Any, ParamSpec, Tuple, Type, TypeVar
else:
    from typing import Any, ParamSpec, Tuple, Type, TypeVar

P = ParamSpec("P")
T = TypeVar("T", bound=FieldInfo)
_T = TypeVar("_T")
Model = TypeVar("Model", bound=DeclarativeBase)


class _Filter:
    """
    Base filters (starting with an underscore) are used to define the strategy and lookup expression for a filter.
    Default lookup expression is equality (where <field> = <value>).
    Default strategy is BaseStrategy, to apply the filter to the query directly (no joins or subqueries).
    To define your own filter, subclass this class and override the `lookup_expr` and optionally the
    `filter` method (rarely needed).
    """

    strategy: StrategyType
    field: InstrumentedAttribute[Any]  # type: ignore[misc]

    @property
    def lookup_expr(self) -> LookupExpr:
        return sa_op.eq

    def __init__(
        self,
        field: InstrumentedAttribute[_T],
        strategy: StrategyType | None = None,
    ) -> None:
        self.field = field
        if strategy is None or strategy is PydanticUndefined:
            self.strategy = BaseStrategy()
        else:
            self.strategy = strategy

    def filter(self, query: Select[Tuple[Model]], value: Any) -> Select[Tuple[Model]]:  # type: ignore[misc]
        return self.strategy.filter(query, self.lookup_expr(self.field, value))


class _MultiFieldFilter:
    """
    Generalized version of _Filter that allows filtering on multiple fields.
    """

    strategy: StrategyType
    fields: List[InstrumentedAttribute[Any]]  # type: ignore[misc]

    @property
    def lookup_expr(self) -> LookupExpr:
        return sa_op.eq

    def __init__(  # type: ignore[misc]
        self,
        fields: List[InstrumentedAttribute[Any]],
        strategy: StrategyType | None = None,
    ) -> None:
        self.fields = fields
        if strategy is None or strategy is PydanticUndefined:
            self.strategy = BaseStrategy()
        else:
            self.strategy = strategy

    def filter(self, query: Select[Tuple[Model]], value: Any) -> Select[Tuple[Model]]:  # type: ignore[misc]
        expr = functools.reduce(sa_op.or_, (self.lookup_expr(field, value) for field in self.fields))
        return self.strategy.filter(query, expr)


class BaseFilterSet(BaseModel):
    """
    Pydantic model subclass that acts as a base class for filter sets.
    """

    def filter(self, query: Select[Tuple[Model]], exclude_none: bool = True) -> Select[Tuple[Model]]:
        """
        Applies all the filters defined as attributes to the provided query.
        Works by extracting the 'filtering' metadata from each field and applying the filters to the query.
        """
        # Use pydantic model dump to exclude none values properly
        model_fields = self.model_dump(exclude_unset=True)

        # Loop over each filter and apply to query
        for field_name, field_info in self.model_fields.items():
            q = self.parse_field_and_apply_filters(field_name, field_info, model_fields, query, exclude_none)
            if q is not None:
                query = q

        return query

    def parse_field_and_apply_filters(  # type: ignore[misc]
        self,
        field_name: str,
        field_info: FieldInfo,
        model_fields: dict[str, Any],
        query: Select[Tuple[Model]],
        exclude_none: bool,
    ) -> Select[Tuple[Model]] | None:
        """
        Applies the filters for a single field to the query in-place.
        """

        # Get the field value from the fields dict while allowing
        # filtering by None values.
        # If field value not present, set to PydanticUndefined so we know to skip it
        # This is needed to distinguish between None and not present
        field_value = model_fields.get(field_name, PydanticUndefined)
        if field_value is PydanticUndefined or (exclude_none and field_value is None):
            return None

        if len(field_info.metadata) == 0:
            return None

        last_metadata = field_info.metadata[-1]

        # Support Pydantic Field by ignoring non-filter fields
        # Check if field metadata is present and if the field is a filter
        # If not, return to proceed to the next field
        if not isinstance(last_metadata, dict) or not last_metadata.get(MetadataFields.SQLALCHEMY_FILTER):
            return None

        return self.validate_and_instantiate_filters(field_name, last_metadata, field_value, query)

    def validate_and_instantiate_filters(  # type: ignore[misc]
        self, field_name: str, metadata: dict[MetadataFields, Any], field_value: Any, query: Select[Tuple[Model]]
    ) -> Select[Tuple[Model]]:
        # Get the filter class from the field's metadata
        filter_class: Type[_Filter] | Type[_MultiFieldFilter] | None = metadata.get(MetadataFields.FILTER_CLASS)
        filter_fields = metadata.get(MetadataFields.FILTER_FIELDS, [])
        strategy = metadata.get(MetadataFields.FIELD_STRATEGY)
        mapper = metadata.get(MetadataFields.VALUE_MAPPER)

        # If the field has no filter_class or filter_fields, raise error
        if filter_class is None:
            raise ValueError(f"Field {field_name} has no filter class")
        if not filter_fields:
            raise ValueError(f"Field {field_name} has no filter field(s)")

        # Apply value mapper if present
        if mapper is not None:
            field_value = mapper(field_value)

        # Apply the filter to the query
        f: _Filter | _MultiFieldFilter

        # If the filter class is a subclass of _Filter, create a filter with a single field
        if issubclass(filter_class, _Filter):
            f = filter_class(field=filter_fields[0], strategy=strategy)
        elif issubclass(filter_class, _MultiFieldFilter):
            f = filter_class(fields=filter_fields, strategy=strategy)
        else:
            raise ValueError(
                f"Field {field_name} has an unknown filter class - please inherit from _Filter or _MultiFieldFilter"
            )

        return f.filter(query, value=field_value)
