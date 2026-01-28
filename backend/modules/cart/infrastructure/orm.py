"""
SQLAlchemy ORM models for Cart module.

Maps domain entities to database tables.
"""

from datetime import datetime
from typing import Final, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class CartORM(Base):
    """
    Cart ORM model.

    Represents carts table in database.
    """

    __tablename__ = "carts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
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
    items: Mapped[list["CartItemORM"]] = relationship(
        "CartItemORM",
        back_populates="cart",
        cascade="all, delete-orphan",
        order_by="CartItemORM.created_at",
    )

    TABLE_NAME: Final = "carts"


class CartItemORM(Base):
    """
    CartItem ORM model.

    Represents cart_items table in database.
    """

    __tablename__ = "cart_items"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    cart_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    price_at_add: Mapped[int] = mapped_column(Integer, nullable=False)  # Stored as cents
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    cart: Mapped["CartORM"] = relationship(
        "CartORM",
        back_populates="items",
    )
    # Note: Product relationship removed to avoid circular imports
    # Use product_id for queries instead

    TABLE_NAME: Final = "cart_items"
