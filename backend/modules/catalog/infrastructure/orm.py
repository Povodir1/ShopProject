"""
SQLAlchemy ORM models for Catalog module.

Maps domain entities to database tables.
"""

from datetime import datetime
from typing import Final, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class CategoryORM(Base):
    """
    Category ORM model.

    Represents categories table in database.
    """

    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # Self-referential relationship for category hierarchy
    # parent: many-to-one side (has foreign key parent_id)
    # children: one-to-many side (references parent's id via remote_side)
    parent: Mapped[Optional["CategoryORM"]] = relationship(
        "CategoryORM",
        back_populates="children",
        foreign_keys=[parent_id],
        remote_side=[id],
    )
    children: Mapped[list["CategoryORM"]] = relationship(
        "CategoryORM",
        back_populates="parent",
        foreign_keys=[parent_id],
        order_by="CategoryORM.name",
    )
    products: Mapped[list["ProductORM"]] = relationship(
        "ProductORM",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    TABLE_NAME: Final = "categories"


class ProductORM(Base):
    """
    Product ORM model.

    Represents products table in database.
    """

    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # Stored as cents
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    category_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    category: Mapped[Optional["CategoryORM"]] = relationship(
        "CategoryORM",
        back_populates="products",
    )
    # Note: cart_items relationship defined in cart.infrastructure.orm
    # to avoid circular import issues

    TABLE_NAME: Final = "products"

    # Indexes for search
    __table_args__ = (
        # GIN index for full-text search on name and description
        # Requires gin extension in PostgreSQL
        # Index('ix_products_name_tsv', name_tsv, postgresql_using='gin'),
    )
