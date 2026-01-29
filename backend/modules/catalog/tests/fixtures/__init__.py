"""
Fixtures for Catalog module tests.

Provides reusable test data and mock objects.
"""

from uuid import UUID, uuid4
from decimal import Decimal

from modules.catalog.domain.entities import Category, Product
from modules.catalog.domain.value_objects import Price, ProductName, Description, Quantity


# ============================================================================
# Test Data Generators
# ============================================================================

def generate_category_id() -> UUID:
    """Generate random category ID."""
    return uuid4()


def generate_product_id() -> UUID:
    """Generate random product ID."""
    return uuid4()


# ============================================================================
# Test Data Factories
# ============================================================================

def create_test_price(amount: float = 29.99, currency: str = "USD") -> Price:
    """Create test price."""
    return Price.from_float(amount, currency)


def create_test_product_name(name: str = "Test Product") -> ProductName:
    """Create test product name."""
    return ProductName(name)


def create_test_description(text: str = "Test product description") -> Description:
    """Create test description."""
    return Description(text)


def create_test_quantity(value: int = 50) -> Quantity:
    """Create test quantity."""
    return Quantity(value)


def create_test_category(name: str = "Test Category") -> Category:
    """Create test category."""
    return Category(id=None, name=name)


def create_test_product(
    name: str = "Test Product",
    description: str = "Test description",
    price: float = 29.99,
    stock: int = 50,
    category_id: UUID | None = None,
) -> Product:
    """Create test product."""
    if category_id is None:
        category_id = generate_category_id()

    return Product(
        id=None,
        name=name,
        description=description,
        price=create_test_price(price),
        category_id=category_id,
        stock=stock,
    )


def create_category_with_children(
    num_children: int = 3,
) -> Category:
    """Create category with child categories."""
    parent = Category(id=None, name="Parent Category")

    for i in range(num_children):
        child = Category(id=None, name=f"Child Category {i + 1}")
        parent.add_child(child)

    return parent


# ============================================================================
# Test Data Constants
# ============================================================================

VALID_PRICES = [0.01, 9.99, 19.99, 99.99, 999.99, 9999.99]
INVALID_PRICES = [0, -0.01, -1.99, -100]
VALID_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD"]
INVALID_CURRENCIES = ["", "US", "USDOLLAR", "AB", "XX"]

VALID_PRODUCT_NAMES = [
    "Product A",
    "Super Product",
    "Premium Quality Item",
    "A" * 255,  # Max length
]
INVALID_PRODUCT_NAMES = [
    "",  # Empty
    "   ",  # Whitespace only
    "A" * 256,  # Too long
]

VALID_DESCRIPTIONS = [
    "Short description",
    "This is a detailed product description with multiple features",
    "A" * 5000,  # Max length
]
INVALID_DESCRIPTIONS = [
    "A" * 5001,  # Too long
]

VALID_STOCK_LEVELS = [0, 1, 10, 50, 100, 1000]
INVALID_STOCK_LEVELS = [-1, -10, -100]

CATEGORY_TEST_DATA = {
    "valid_category": {
        "name": "Electronics",
    },
    "category_with_parent": {
        "name": "Laptops",
        "parent_id": uuid4(),
    },
    "root_category": {
        "name": "Root",
        "parent_id": None,
    },
}

PRODUCT_TEST_DATA = {
    "valid_product": {
        "name": "Laptop",
        "description": "High-performance laptop",
        "price": 999.99,
        "stock": 50,
    },
    "cheap_product": {
        "name": "USB Cable",
        "description": "USB charging cable",
        "price": 9.99,
        "stock": 100,
    },
    "expensive_product": {
        "name": "Gaming PC",
        "description": "High-end gaming computer",
        "price": 2999.99,
        "stock": 5,
    },
    "out_of_stock": {
        "name": "Discontinued Item",
        "description": "No longer available",
        "price": 49.99,
        "stock": 0,
    },
    "low_stock": {
        "name": "Last Items",
        "description": "Almost sold out",
        "price": 19.99,
        "stock": 2,
    },
}

FILTER_TEST_DATA = {
    "price_range": {
        "price_min": 10.0,
        "price_max": 100.0,
    },
    "search_query": "laptop",
    "in_stock_only": True,
    "sort_by_price_asc": {
        "order_by": "price",
        "order_dir": "asc",
    },
    "sort_by_name_desc": {
        "order_by": "name",
        "order_dir": "desc",
    },
}
