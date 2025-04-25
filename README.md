<h1 align="center">
    <strong>pydantic-sqlalchemy-filterset</strong>
</h1>
<p align="center">
    <a href="https://github.com/RamiAwar/pydantic-sqlalchemy-filterset" target="_blank">
        <img src="https://img.shields.io/github/last-commit/RamiAwar/pydantic-sqlalchemy-filterset" alt="Latest Commit">
    </a>
        <img src="https://img.shields.io/github/workflow/status/RamiAwar/pydantic-sqlalchemy-filterset/CI">
        <a href="https://github.com/RamiAwar/pydantic-sqlalchemy-filterset/actions?workflow=CI" target="_blank">
            <img src="https://img.shields.io/badge/Coverage-100%25-success">
        </a>
    <br />
    <a href="https://pypi.org/project/pydantic-sqlalchemy-filterset" target="_blank">
        <img src="https://img.shields.io/pypi/v/pydantic-sqlalchemy-filterset" alt="Package version">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/pydantic-sqlalchemy-filterset">
    <img src="https://img.shields.io/github/license/RamiAwar/pydantic-sqlalchemy-filterset">
</p>

Pydantic SQLAlchemy filterset library to turn pydantic models into sqlalchemy filters with advanced filtering support.

### Sponsored by
<a href="sendcloud.com"><image width="240" height="100" src="assets/sendcloud.png"></a>

## Motivation

In every web app, there's a need for a client-facing filtering API. You need to filter some results by a search query, date range, category, number range, etc. Nearly impossible to find an API that doesn't do any filtering.

Traditionally, we'd extract these filters out of the request, parse them, and translate them into a database queries (or several).

This quickly gets repetitive, applying the same logic due to shared filters and shared functionality.


## Solution

Pydantic SQLAlchemy filtersets solve this problem by making it as easy as possible to build a filtering structure that's generic and that plugs right into python web frameworks.

By building a simple model like the following, we define a complex filterset that supports input validation (with Pydantic) and knows how to translate the filter inputs into a DB query with SQLAlchemy.

This also supports many to many relations, inner and outer joins and more but I'm keeping the first few examples simple intentionally.

## UPDATE: 
The concepts from this repository were proposed and successfully merged into [SQLAlchemy Filtersets](https://sqlalchemy-filterset.github.io). Here's a comparison of that library to this:

#### Upsides:
- Simple to define a filterset
- Supports all the main features in this library
- Is supported by more than one person (i.e. me), although just copy pasting this is fine, it's simple code.

#### Downsides:
- Requires defining an additional schema first, and then the filtersets. That means the classes are detached, and both need to always be updated to match.
- Is more verbose in the filterset definitions

## Usage

```python
class ProductFilterSet(BaseFilterSet):
    # Simple SQL where statement
    # Optional: the Query(None) is a FastAPI detail for proper swagger doc rendering
    product_id: Optional[uuid.UUID] = WhereFilter(Product.id, default=Query(None))
    
    # Simple ILike on name
    name: Optional[str] = ILikeFilter(Product.name, default=Query(None))
    
    # Needs a join to filter on linked category name
    # Notice how this mirrors SQLAlchemy, will figure out
    # the join onclause by itself!
    category_name: Optional[str] = WhereFilter(
        Category.name,
        strategy=InnerJoinStrategy(Category),
        default=Query(None),
    )
```

`BaseFilterSet` is actually a Pydantic `BaseModel`. This means you can pass this in as an input to a FastAPI route! The models used below are specified in more detail later, but I'll show example usage of the FilterSet quickly:

```python
from sqlalchemy import select
from fastapi import APIRouter, Depends
from tests.conftest import Product

router = APIRouter()

# get_session is from the FastAPI SQLAlchemy guide
# ProductOut is a pure pydantic model specifying output fields wanted
# ProductModel is the sqlalchemy model

@router.get("/search")
async def search_apps(
    filters: ProductFilterSet = Depends(), 
    session: AsyncSession = Depends(get_session),
) -> list[ProductOut]:
    query = select(Product)  # Can be any SQLAlchemy query

    query = filters.filter(query)  # Apply all the filters

    # Pure SQLAlchemy from here on:
    results = await session.execute(query)
    products = results.scalars().unique().all()

    # Serialize and return
    return [ProductOut.model_validate(prod) for prod in products]
```

## Philosophy: Be like SQLAlchemy

The general philosophy behind the design of these FilterSets is to try and mirror sqlalchemy as much as possible. This becomes especially important in joins, where building queries gets complicated pretty quickly. SQLAlchemy is very mature and has a pretty good design around that which is why we try and follow their signatures as closely as possible.

There are two main ways of doing a join in sqlalchemy: `join` and `join_from`. The difference is detailed pretty well in [this section of the docs](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#explicit-from-clauses-and-joins). I'll revisit their examples below, translated into our FilterSets.

## Simple Joins

`InnerJoinStrategy` attempts to mirror the sqlalchemy `Select.join()` method. There are two ways to construct an `InnerJoinStrategy`.(There will also be a mirror of `Select.join_from()` in the near future)

### First method: Automatic
For the first, you need one argument: the join target. This will form the right side of the join, leaving the left side to be inferred automatically from the input query based on the existing relationships.
TODO:

### Second method: Manual
If no relationship exists, or multiple relationships exist, then the join cannot be automatically inferred. In that case, we need to use the `ON` clause. This is provided through the `onclause` argument on the `InnerJoinStrategy` constructor.

TODO:

## More complex joins

Let's talk about many to many relationships and others where we might have multiple secondary tables we need to jump across to reach the data we need.

To do this we can add multiple joins, just like we would in SQLAlchemy if we were using the core api.

Here we want to filter on country names. Products are linked to countries through the ProductCountry model (jump table or secondary table). So we'll use multiple outer joins to get the data we need, as if we were writing SQL. This is what I like the most about SQLAlchemy - it can act as a powerful query builder.

```python

class ProductFilterSet(BaseFilterSet):
    country_name: str | None = WhereFilter(
        strategy=MultiJoinStrategy(
            OuterJoinStrategy(ProductCountry),
            OuterJoinStrategy(Country),
        )
    )
```


## Implementation Details for above examples:

You can find the models used above inside `conftest.py`, such as:
```python

class Product(AlchemyBase):
    __tablename__ = "_product_"
    id: Mapped[uuid.UUID] = mapped_column("id", UUID, primary_key=True)
    name: Mapped[str] = mapped_column("name", String, nullable=False)
    price: Mapped[float] = mapped_column("price", Float, nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        "category_id", UUID, ForeignKey("_productcategory_.id"), nullable=False
    )
```

This is an example of ProductOut:

```python
from pydantic import BaseModel, ConfigDict

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: ID_TYPE
    title: str

## License

This project is licensed under the terms of the MIT license.
