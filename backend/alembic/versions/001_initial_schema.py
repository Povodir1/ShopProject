"""Initial schema creation

Revision ID: 001
Revises:
Create Date: 2026-01-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema - create all tables."""

    # Create categories table
    op.create_table(
        "categories",
        sa.Column(
            "id",
            sa.String(36),
            primary_key=True,
            comment="Category identifier (UUID)",
        ),
        sa.Column(
            "name",
            sa.String(100),
            nullable=False,
            comment="Category name",
        ),
        sa.Column(
            "parent_id",
            sa.String(36),
            sa.ForeignKey("categories.id", ondelete="CASCADE"),
            nullable=True,
            comment="Parent category ID for hierarchy",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            comment="Creation timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
            comment="Last update timestamp",
        ),
        comment="Product categories",
    )

    # Create index on categories.name
    op.create_index(
        "ix_categories_name",
        "categories",
        ["name"],
    )

    # Create index on categories.parent_id
    op.create_index(
        "ix_categories_parent_id",
        "categories",
        ["parent_id"],
    )

    # Create products table
    op.create_table(
        "products",
        sa.Column(
            "id",
            sa.String(36),
            primary_key=True,
            comment="Product identifier (UUID)",
        ),
        sa.Column(
            "name",
            sa.String(255),
            nullable=False,
            comment="Product name",
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
            comment="Product description",
        ),
        sa.Column(
            "price",
            sa.Integer(),
            nullable=False,
            comment="Price in cents",
        ),
        sa.Column(
            "currency",
            sa.String(3),
            nullable=False,
            default="USD",
            comment="Currency code",
        ),
        sa.Column(
            "category_id",
            sa.String(36),
            sa.ForeignKey("categories.id", ondelete="SET NULL"),
            nullable=True,
            comment="Category identifier",
        ),
        sa.Column(
            "stock",
            sa.Integer(),
            nullable=False,
            default=0,
            comment="Available stock quantity",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            comment="Creation timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
            comment="Last update timestamp",
        ),
        comment="Products catalog",
    )

    # Create index on products.name
    op.create_index(
        "ix_products_name",
        "products",
        ["name"],
    )

    # Create index on products.category_id
    op.create_index(
        "ix_products_category_id",
        "products",
        ["category_id"],
    )

    # Create carts table
    op.create_table(
        "carts",
        sa.Column(
            "id",
            sa.String(36),
            primary_key=True,
            comment="Cart identifier (UUID)",
        ),
        sa.Column(
            "session_id",
            sa.String(255),
            nullable=False,
            unique=True,
            comment="Session identifier for guest carts",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            comment="Creation timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
            comment="Last update timestamp",
        ),
        comment="Shopping carts",
    )

    # Create index on carts.session_id
    op.create_index(
        "ix_carts_session_id",
        "carts",
        ["session_id"],
        unique=True,
    )

    # Create cart_items table
    op.create_table(
        "cart_items",
        sa.Column(
            "id",
            sa.String(36),
            primary_key=True,
            comment="Cart item identifier (UUID)",
        ),
        sa.Column(
            "cart_id",
            sa.String(36),
            sa.ForeignKey("carts.id", ondelete="CASCADE"),
            nullable=False,
            comment="Cart identifier",
        ),
        sa.Column(
            "product_id",
            sa.String(36),
            nullable=False,
            comment="Product identifier",
        ),
        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
            default=1,
            comment="Item quantity",
        ),
        sa.Column(
            "price_at_add",
            sa.Integer(),
            nullable=False,
            comment="Price at add time (in cents)",
        ),
        sa.Column(
            "currency",
            sa.String(3),
            nullable=False,
            default="USD",
            comment="Currency code",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            comment="Creation timestamp",
        ),
        comment="Items in shopping carts",
    )

    # Create index on cart_items.cart_id
    op.create_index(
        "ix_cart_items_cart_id",
        "cart_items",
        ["cart_id"],
    )

    # Create index on cart_items.product_id
    op.create_index(
        "ix_cart_items_product_id",
        "cart_items",
        ["product_id"],
    )


def downgrade() -> None:
    """Downgrade database schema - drop all tables."""

    # Drop indexes
    op.drop_index("ix_cart_items_product_id", table_name="cart_items")
    op.drop_index("ix_cart_items_cart_id", table_name="cart_items")
    op.drop_index("ix_carts_session_id", table_name="carts")
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_index("ix_categories_parent_id", table_name="categories")
    op.drop_index("ix_categories_name", table_name="categories")

    # Drop tables
    op.drop_table("cart_items")
    op.drop_table("carts")
    op.drop_table("products")
    op.drop_table("categories")
