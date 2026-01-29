"""
Pytest configuration and fixtures for Catalog module tests.
"""

import pytest
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, Mock

from modules.catalog.domain.entities import Category, Product
from modules.catalog.domain.repositories import IProductRepository, ICategoryRepository
from modules.catalog.domain.value_objects import Price, ProductName, Description, Quantity
from modules.catalog.tests.fixtures import (
    generate_category_id,
    generate_product_id,
    create_test_price,
    create_test_product_name,
    create_test_description,
    create_test_quantity,
    create_test_category,
    create_test_product,
    create_category_with_children,
)


# ============================================================================
# Basic ID Fixtures
# ============================================================================

@pytest.fixture
def category_id() -> UUID:
    """Generate category ID."""
    return generate_category_id()


@pytest.fixture
def product_id() -> UUID:
    """Generate product ID."""
    return generate_product_id()


@pytest.fixture
def parent_category_id() -> UUID:
    """Generate parent category ID."""
    return uuid4()


# ============================================================================
# Value Object Fixtures
# ============================================================================

@pytest.fixture
def test_price() -> Price:
    """Create test price."""
    return create_test_price(29.99, "USD")


@pytest.fixture
def test_product_name() -> ProductName:
    """Create test product name."""
    return create_test_product_name("Test Product")


@pytest.fixture
def test_description() -> Description:
    """Create test description."""
    return create_test_description("Test product description")


@pytest.fixture
def test_quantity() -> Quantity:
    """Create test quantity."""
    return create_test_quantity(50)


# ============================================================================
# Entity Fixtures
# ============================================================================

@pytest.fixture
def sample_category() -> Category:
    """Create sample category."""
    return create_test_category("Electronics")


@pytest.fixture
def sample_category_with_children() -> Category:
    """Create category with children."""
    return create_category_with_children(num_children=3)


@pytest.fixture
def sample_product(
    test_product_name: ProductName,
    test_price: Price,
    test_description: Description,
    category_id: UUID,
) -> Product:
    """Create sample product."""
    return Product(
        id=None,
        name=str(test_product_name),
        description=str(test_description),
        price=test_price,
        category_id=category_id,
        stock=50,
    )


@pytest.fixture
def out_of_stock_product(
    test_product_name: ProductName,
    test_price: Price,
    test_description: Description,
    category_id: UUID,
) -> Product:
    """Create out of stock product."""
    return Product(
        id=None,
        name=str(test_product_name),
        description=str(test_description),
        price=test_price,
        category_id=category_id,
        stock=0,
    )


@pytest.fixture
def low_stock_product(
    test_product_name: ProductName,
    test_price: Price,
    test_description: Description,
    category_id: UUID,
) -> Product:
    """Create low stock product."""
    return Product(
        id=None,
        name=str(test_product_name),
        description=str(test_description),
        price=test_price,
        category_id=category_id,
        stock=2,
    )


@pytest.fixture
def products_list(category_id: UUID, test_price: Price) -> list[Product]:
    """Create list of sample products."""
    products = [
        Product(
            id=uuid4(),
            name=f"Product {i}",
            description=f"Description {i}",
            price=Price.from_float(10.0 * (i + 1), "USD"),
            category_id=category_id,
            stock=10 * (i + 1),
        )
        for i in range(5)
    ]
    return products


# ============================================================================
# Mock Repository Fixtures
# ============================================================================

@pytest.fixture
def mock_product_repository():
    """Create mock product repository."""
    mock = Mock(spec=IProductRepository)

    # Configure async methods
    mock.get_by_id = AsyncMock()
    mock.get_all = AsyncMock()
    mock.search = AsyncMock()
    mock.count = AsyncMock()

    return mock


@pytest.fixture
def mock_category_repository():
    """Create mock category repository."""
    mock = Mock(spec=ICategoryRepository)

    # Configure async methods
    mock.get_by_id = AsyncMock()
    mock.get_all = AsyncMock()
    mock.get_tree = AsyncMock()
    mock.get_children = AsyncMock()

    return mock
