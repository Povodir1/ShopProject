"""
Pytest configuration and fixtures for Cart module tests.
"""

import pytest
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, Mock

from modules.cart.domain.entities import Cart, CartItem
from modules.cart.domain.repositories import ICartRepository
from modules.cart.domain.value_objects import Quantity, SessionId
from modules.catalog.domain.entities import Product
from modules.catalog.domain.value_objects import Price
from modules.cart.tests.fixtures import (
    generate_cart_id,
    generate_session_id,
    generate_product_id,
    create_test_price,
    create_test_quantity,
    create_empty_cart,
    create_cart_with_items,
    create_test_cart_item,
)


# ============================================================================
# Basic ID Fixtures
# ============================================================================

@pytest.fixture
def cart_id() -> UUID:
    """Generate cart ID."""
    return generate_cart_id()


@pytest.fixture
def session_id() -> str:
    """Generate session ID."""
    return generate_session_id()


@pytest.fixture
def product_id() -> UUID:
    """Generate product ID."""
    return generate_product_id()


@pytest.fixture
def item_id() -> UUID:
    """Generate item ID."""
    return uuid4()


# ============================================================================
# Value Object Fixtures
# ============================================================================

@pytest.fixture
def test_price() -> Price:
    """Create test price."""
    return create_test_price(29.99, "USD")


@pytest.fixture
def test_quantity() -> Quantity:
    """Create test quantity."""
    return create_test_quantity(5)


@pytest.fixture
def test_session_id() -> SessionId:
    """Create test session ID value object."""
    return SessionId(generate_session_id())


# ============================================================================
# Entity Fixtures
# ============================================================================

@pytest.fixture
def empty_cart(session_id: str) -> Cart:
    """Create empty cart."""
    return create_empty_cart(session_id)


@pytest.fixture
def sample_cart(session_id: str, product_id: UUID, test_price: Price) -> Cart:
    """Create cart with sample item."""
    cart = Cart(id=None, session_id=session_id)
    cart.add_item(product_id=product_id, quantity=2, price=test_price)
    return cart


@pytest.fixture
def cart_with_multiple_items(session_id: str) -> Cart:
    """Create cart with multiple items."""
    return create_cart_with_items(session_id, num_items=3)


@pytest.fixture
def sample_cart_item(cart_id: UUID, product_id: UUID, test_price: Price) -> CartItem:
    """Create sample cart item."""
    return create_test_cart_item(
        cart_id=cart_id,
        product_id=product_id,
        quantity=3,
        price=29.99,
    )


# ============================================================================
# Mock Repository Fixtures
# ============================================================================

@pytest.fixture
def mock_cart_repository():
    """Create mock cart repository."""
    mock = Mock(spec=ICartRepository)

    # Configure async methods
    mock.get_by_session_id = AsyncMock()
    mock.save = AsyncMock()
    mock.delete = AsyncMock()
    mock.get_item_by_id = AsyncMock()
    mock.delete_item = AsyncMock()

    return mock


@pytest.fixture
def mock_product_repository():
    """Create mock product repository."""
    from modules.catalog.domain.repositories import IProductRepository

    mock = Mock(spec=IProductRepository)

    # Configure async methods
    mock.get_by_id = AsyncMock()
    mock.get_all = AsyncMock()
    mock.search = AsyncMock()
    mock.count = AsyncMock()

    return mock


@pytest.fixture
def mock_product(product_id: UUID, test_price: Price) -> Product:
    """Create mock product for testing."""
    product = Mock(spec=Product)
    product.id = product_id
    product.name = "Test Product"
    product.description = "Test Description"
    product.price = test_price
    product.stock = 50
    product.category_id = None

    # Configure is_available method
    product.is_available = Mock(return_value=True)

    return product
