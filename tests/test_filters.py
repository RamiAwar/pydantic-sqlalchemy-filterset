import uuid
from typing import List, Optional

from sqlalchemy import select

from pydantic_sqlalchemy_filterset.core import BaseFilterSet
from pydantic_sqlalchemy_filterset.filters import ILikeFilter, InFilter, IsFilter, WhereFilter
from pydantic_sqlalchemy_filterset.strategies import InnerJoinStrategy, MultiJoinStrategy
from tests.conftest import Category, Country, Product, ProductCountry


class ProductFilterSet(BaseFilterSet):
    product_id: Optional[uuid.UUID] = WhereFilter(Product.id, default=None)
    price: Optional[float] = IsFilter(Product.price, default=None)
    name: Optional[str] = ILikeFilter(Product.name, default=None)
    category_name: Optional[str] = WhereFilter(
        Category.name,
        strategy=InnerJoinStrategy(
            Category,
            onclause=Category.id == Product.category_id,
        ),
        default=None,
    )
    categories: Optional[List[uuid.UUID]] = InFilter(Product.category_id, default=None)
    category_names: Optional[List[str]] = InFilter(Category.name, strategy=InnerJoinStrategy(Category), default=None)
    countries: Optional[List[str]] = InFilter(
        Country.name,
        strategy=MultiJoinStrategy(
            InnerJoinStrategy(ProductCountry),
            InnerJoinStrategy(Country),
        ),
        default=None,
    )


class MinimalProductFilterSet(BaseFilterSet):
    category_name: Optional[str] = WhereFilter(Category.name, strategy=InnerJoinStrategy(Category), default=None)


def test_base_filterset() -> None:
    random_uuid = uuid.uuid4()
    filters = ProductFilterSet(product_id=random_uuid)

    got_query = filters.filter(select(Product))
    want_query = select(Product).where(Product.id == random_uuid)

    # Check that compiled query is the same as the expected query
    assert str(got_query) == str(want_query)


def test_base_filterset_with_inner_join() -> None:
    filters = ProductFilterSet(category_name="test")

    got_query = filters.filter(select(Product))
    want_query = select(Product).join(Category, Category.id == Product.category_id).where(Category.name == "test")

    assert str(got_query) == str(want_query)


def test_filterset_with_no_onclause() -> None:
    filters = MinimalProductFilterSet(category_name="test")

    got_query = filters.filter(select(Product))
    want_query = select(Product).join(Category).where(Category.name == "test")

    assert str(got_query) == str(want_query)


def test_filterset_with_in_filter_on_many_to_one() -> None:
    category_names = ["one", "two"]
    filters = ProductFilterSet(category_names=category_names)

    got_query = filters.filter(select(Product))
    want_query = select(Product).join(Category).where(Category.name.in_(category_names))
    assert str(got_query) == str(want_query)


def test_filterset_with_multi_inner_joins() -> None:
    countries = ["test"]
    filters = ProductFilterSet(countries=countries)

    got_query = filters.filter(select(Product))
    want_query = select(Product).join(ProductCountry).join(Country).where(Country.name.in_(countries))

    assert str(got_query) == str(want_query)


def test_base_filterset_with_in_filter() -> None:
    # Generate List of uuids
    # uuids = uuid.uuid4()
    uuids = [uuid.uuid4() for _ in range(3)]
    filters = ProductFilterSet(categories=uuids)

    got_query = filters.filter(select(Product))
    want_query = select(Product).where(Product.category_id.in_(uuids))

    assert str(got_query) == str(want_query)


def test_base_filterset_with_like_filter() -> None:
    filters = ProductFilterSet(name="test")

    got_query = filters.filter(select(Product))
    want_query = select(Product).where(Product.name.ilike("%test%"))

    assert str(got_query) == str(want_query)


def test_filter_with_exclude_none_true() -> None:
    filters = ProductFilterSet(name=None)

    got_query = filters.filter(select(Product))
    want_query = select(Product)

    assert str(got_query) == str(want_query)


def test_filter_with_exclude_none_false() -> None:
    filters = ProductFilterSet(price=None)

    got_query = filters.filter(select(Product), exclude_none=False)
    want_query = select(Product).where(Product.price.is_(None))

    assert str(got_query) == str(want_query)
