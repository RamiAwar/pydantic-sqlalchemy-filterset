import uuid
from typing import List

from sqlalchemy import UUID, Float, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class AlchemyBase(DeclarativeBase):
    __abstract__ = True


class Product(AlchemyBase):
    __tablename__ = "_product_"
    id: Mapped[uuid.UUID] = mapped_column("id", UUID, primary_key=True)
    name: Mapped[str] = mapped_column("name", String, nullable=False)
    price: Mapped[float] = mapped_column("price", Float, nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        "category_id", UUID, ForeignKey("_productcategory_.id"), nullable=False
    )


class Category(AlchemyBase):
    __tablename__ = "_productcategory_"
    id: Mapped[uuid.UUID] = mapped_column("id", UUID, primary_key=True)
    name: Mapped[str] = mapped_column("name", String, nullable=False)


class ProductCountry(AlchemyBase):
    __tablename__ = "_productcountry_"
    product_id: Mapped[uuid.UUID] = mapped_column("product_id", UUID, ForeignKey("_product_.id"), primary_key=True)
    country_id: Mapped[uuid.UUID] = mapped_column("country_id", UUID, ForeignKey("_country_.id"), primary_key=True)


class Country(AlchemyBase):
    __tablename__ = "_country_"
    id: Mapped[uuid.UUID] = mapped_column("id", UUID, primary_key=True)
    name: Mapped[str] = mapped_column("name", String, nullable=False)

    products: Mapped[List[Product]] = relationship("Product", secondary="_productcountry_")
