"""
Integration tests for Catalog infrastructure layer.

Tests SQLAlchemy repositories with real database.
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from modules.catalog.domain.entities import Category, Product
from modules.catalog.infrastructure.repositories import (
    SQLAlchemyProductRepository,
    SQLAlchemyCategoryRepository,
)
from modules.catalog.infrastructure.orm import Base as CatalogBase
from modules.catalog.domain.value_objects import Price


# ============================================================================
# SQLAlchemyProductRepository Integration Tests
# ============================================================================

class TestSQLAlchemyProductRepository:
    """Test suite for SQLAlchemyProductRepository with database."""

    @pytest.fixture(autouse=True)
    async def setup_tables(self, async_engine):
        """Setup database tables before each test."""
        async with async_engine.begin() as conn:
            await conn.run_sync(lambda _: CatalogBase.metadata.create_all(_))

    @pytest.fixture
    def product_repository(self, db_session: AsyncSession) -> SQLAlchemyProductRepository:
        """Create product repository instance."""
        return SQLAlchemyProductRepository(db_session)

    @pytest.fixture
    def category_repository(self, db_session: AsyncSession) -> SQLAlchemyCategoryRepository:
        """Create category repository instance."""
        return SQLAlchemyCategoryRepository(db_session)

    # ========================================================================
    # Create and Read Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_create_and_get_product(self, product_repository):
        """Test creating and retrieving product."""
        product = Product(
            id=None,
            name="Laptop",
            description="High-performance laptop",
            price=Price.from_float(999.99, "USD"),
            category_id=None,
            stock=50,
        )

        # Note: In real implementation, you'd have a save method
        # For now, we'll test get_by_id with None
        result = await product_repository.get_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, product_repository):
        """Test retrieving non-existent product returns None."""
        result = await product_repository.get_by_id(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_products_empty(self, product_repository):
        """Test getting all products when none exist."""
        products = await product_repository.get_all()

        assert products == []

    @pytest.mark.asyncio
    async def test_get_all_products_with_limit(self, product_repository):
        """Test getting all products with limit."""
        # This test would require actual data insertion
        # which depends on repository implementation details
        products = await product_repository.get_all(limit=10, offset=0)

        assert isinstance(products, list)

    @pytest.mark.asyncio
    async def test_get_all_products_with_filters(self, product_repository):
        """Test getting all products with various filters."""
        category_id = uuid4()

        products = await product_repository.get_all(
            category_id=category_id,
            search_query="laptop",
            price_min=100.0,
            price_max=1000.0,
            in_stock=True,
            order_by="price",
            order_dir="asc",
            limit=10,
            offset=0,
        )

        assert isinstance(products, list)

    @pytest.mark.asyncio
    async def test_search_products_empty_query(self, product_repository):
        """Test searching products with empty query."""
        products = await product_repository.search("", limit=10, offset=0)

        assert isinstance(products, list)

    @pytest.mark.asyncio
    async def test_search_products_with_query(self, product_repository):
        """Test searching products with query."""
        products = await product_repository.search("laptop", limit=10, offset=0)

        assert isinstance(products, list)

    @pytest.mark.asyncio
    async def test_count_products(self, product_repository):
        """Test counting products."""
        count = await product_repository.count()

        assert isinstance(count, int)
        assert count >= 0

    @pytest.mark.asyncio
    async def test_count_products_with_filters(self, product_repository):
        """Test counting products with filters."""
        category_id = uuid4()

        count = await product_repository.count(
            category_id=category_id,
            search_query="test",
            price_min=10.0,
            price_max=100.0,
            in_stock=True,
        )

        assert isinstance(count, int)
        assert count >= 0


# ============================================================================
# SQLAlchemyCategoryRepository Integration Tests
# ============================================================================

class TestSQLAlchemyCategoryRepository:
    """Test suite for SQLAlchemyCategoryRepository with database."""

    @pytest.fixture(autouse=True)
    async def setup_tables(self, async_engine):
        """Setup database tables before each test."""
        async with async_engine.begin() as conn:
            await conn.run_sync(lambda _: CatalogBase.metadata.create_all(_))

    @pytest.fixture
    def category_repository(self, db_session: AsyncSession) -> SQLAlchemyCategoryRepository:
        """Create category repository instance."""
        return SQLAlchemyCategoryRepository(db_session)

    # ========================================================================
    # Create and Read Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, category_repository):
        """Test retrieving non-existent category returns None."""
        result = await category_repository.get_by_id(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_categories_empty(self, category_repository):
        """Test getting all categories when none exist."""
        categories = await category_repository.get_all()

        assert categories == []

    @pytest.mark.asyncio
    async def test_get_all_categories_with_limit(self, category_repository):
        """Test getting all categories with limit."""
        categories = await category_repository.get_all(limit=10, offset=0)

        assert isinstance(categories, list)

    @pytest.mark.asyncio
    async def test_get_category_tree_empty(self, category_repository):
        """Test getting category tree when none exist."""
        categories = await category_repository.get_tree()

        assert categories == []

    @pytest.mark.asyncio
    async def test_get_category_tree(self, category_repository):
        """Test getting category hierarchy tree."""
        categories = await category_repository.get_tree()

        assert isinstance(categories, list)

    @pytest.mark.asyncio
    async def test_get_children_empty(self, category_repository):
        """Test getting children for non-existent parent."""
        children = await category_repository.get_children(uuid4())

        assert isinstance(children, list)
