import functools
from typing import Optional, Tuple, TypeVar, Union

from sqlalchemy import ColumnElement, ColumnExpressionArgument, Select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql._typing import _JoinTargetArgument

Model = TypeVar("Model", bound=DeclarativeBase)


class BaseStrategy:
    """
    Base filtering strategy that applies a simple where clause to the expressions provided.
    """

    def filter(self, query: Select[Tuple[Model]], *expression: ColumnExpressionArgument[bool]) -> Select[Tuple[Model]]:
        return query.where(*expression)


class InnerJoinStrategy(BaseStrategy):
    """
    Filtering strategy that applies a join to the query before applying the where clause.
    Note that there is currently no smart logic to handle multiple joins, so joins can be
    applied multiple times. Support for this can be added in the future as needed.
    """

    def __init__(self, target: _JoinTargetArgument, onclause: Optional[ColumnElement[bool]] = None) -> None:
        """
        :param target: The target of the join, which will form the right side of the join. The left side
        in this case will be inferred from the query.
        :param onclause: The condition that will be used to join the two tables. If this is not provided,
        it will be inferred from the relationship between the two tables.
        """
        self.target = target
        self.onclause = onclause

    def apply_join(self, query: Select[Tuple[Model]]) -> Select[Tuple[Model]]:
        return query.join(target=self.target, onclause=self.onclause)

    def filter(self, query: Select[Tuple[Model]], *expression: ColumnExpressionArgument[bool]) -> Select[Tuple[Model]]:
        return self.apply_join(query).where(*expression)


class OuterJoinStrategy(InnerJoinStrategy):
    """
    Filtering strategy that applies an outer join.
    """

    def apply_join(self, query: Select[Tuple[Model]]) -> Select[Tuple[Model]]:
        return query.outerjoin(target=self.target, onclause=self.onclause)


JoinStrategy = Union[InnerJoinStrategy, OuterJoinStrategy]


class MultiJoinStrategy(BaseStrategy):
    """
    Filtering strategy that applies a join to the query before applying the where clause.
    Note that there is currently no smart logic to handle multiple joins, so joins can be
    applied multiple times. Support for this can be added in the future as needed.
    """

    def __init__(self, *joins: JoinStrategy) -> None:
        if not joins:
            raise ValueError("At least one join must be provided.")
        self.joins = joins

    @classmethod
    def apply_join(cls, query: Select[Tuple[Model]], join_strategy: JoinStrategy) -> Select[Tuple[Model]]:
        return join_strategy.apply_join(query)

    def filter(self, query: Select[Tuple[Model]], *expression: ColumnExpressionArgument[bool]) -> Select[Tuple[Model]]:
        join_query = functools.reduce(self.apply_join, self.joins, query)
        return join_query.where(*expression)


# Add any new strategies here for type checking
StrategyType = Union[BaseStrategy, InnerJoinStrategy, OuterJoinStrategy, MultiJoinStrategy]
