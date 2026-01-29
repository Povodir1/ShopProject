"""
Fixtures for Cart module tests.

Provides reusable test data and mock objects.
"""

from uuid import UUID, uuid4
from decimal import Decimal

from modules.cart.domain.entities import Cart, CartItem
from modules.cart.domain.value_objects import Quantity, SessionId
from modules.catalog.domain.value_objects import Price


# ============================================================================
# Test Data Generators
# ============================================================================

def generate_cart_id() -> UUID:
    """Generate random cart ID."""
    return uuid4()


def generate_session_id() -> str:
    """Generate random session ID."""
    return str(uuid4())


def generate_product_id() -> UUID:
    """Generate random product ID."""
    return uuid4()


def generate_item_id() -> UUID:
    """Generate random item ID."""
    return uuid4()


# ============================================================================
# Test Data Factories
# ============================================================================

def create_test_price(amount: float = 29.99, currency: str = "USD") -> Price:
    """Create test price."""
    return Price.from_float(amount, currency)


def create_test_quantity(value: int = 5) -> Quantity:
    """Create test quantity."""
    return Quantity(value)


def create_test_session_id() -> SessionId:
    """Create test session ID."""
    return SessionId(generate_session_id())


def create_empty_cart(session_id: str | None = None) -> Cart:
    """Create empty cart for testing."""
    if session_id is None:
        session_id = generate_session_id()
    return Cart(id=None, session_id=session_id)


def create_cart_with_items(
    session_id: str | None = None,
    num_items: int = 2,
) -> Cart:
    """Create cart with sample items for testing."""
    if session_id is None:
        session_id = generate_session_id()

    cart = Cart(id=None, session_id=session_id)

    # Add sample items
    for i in range(num_items):
        product_id = generate_product_id()
        price = create_test_price(10.0 + i * 5.0)
        cart.add_item(product_id=product_id, quantity=i + 1, price=price)

    return cart


def create_test_cart_item(
    cart_id: UUID | None = None,
    product_id: UUID | None = None,
    quantity: int = 3,
    price: float = 29.99,
) -> CartItem:
    """Create test cart item."""
    if cart_id is None:
        cart_id = generate_cart_id()
    if product_id is None:
        product_id = generate_product_id()

    price_obj = create_test_price(price)

    return CartItem(
        id=None,
        cart_id=cart_id,
        product_id=product_id,
        quantity=quantity,
        price_at_add=int(price_obj.amount * 100),
        currency=price_obj.currency,
    )


# ============================================================================
# Test Data Constants
# ============================================================================

VALID_PRICES = [9.99, 19.99, 29.99, 99.99, 999.99]
VALID_QUANTITIES = [1, 5, 10, 50, 100]
INVALID_QUANTITIES = [0, -1, 101, 1000]
INVALID_PRICES = [0, -1.99, -100]
INVALID_CURRENCIES = ["", "US", "USDOLLAR", "AB", "XX"]

CART_TEST_DATA = {
    "empty_cart": {"session_id": "test-session-1"},
    "cart_with_one_item": {
        "session_id": "test-session-2",
        "product_id": uuid4(),
        "quantity": 2,
        "price": 19.99,
    },
    "cart_with_multiple_items": {
        "session_id": "test-session-3",
        "items": [
            {"product_id": uuid4(), "quantity": 1, "price": 10.0},
            {"product_id": uuid4(), "quantity": 3, "price": 20.0},
            {"product_id": uuid4(), "quantity": 2, "price": 15.0},
        ],
    },
}

CART_ITEM_TEST_DATA = {
    "valid_item": {"quantity": 5, "price": 29.99, "currency": "USD"},
    "min_quantity": {"quantity": 1, "price": 9.99},
    "max_quantity": {"quantity": 100, "price": 99.99},
    "zero_quantity": {"quantity": 0, "price": 19.99},
    "negative_quantity": {"quantity": -1, "price": 19.99},
    "exceeds_max": {"quantity": 101, "price": 19.99},
}

MERGE_TEST_DATA = {
    "source_cart": {
        "session_id": "source-session",
        "items": [
            {"product_id": uuid4(), "quantity": 2, "price": 10.0},
            {"product_id": uuid4(), "quantity": 3, "price": 20.0},
        ],
    },
    "target_cart": {
        "session_id": "target-session",
        "items": [
            {"product_id": uuid4(), "quantity": 1, "price": 15.0},
        ],
    },
}
