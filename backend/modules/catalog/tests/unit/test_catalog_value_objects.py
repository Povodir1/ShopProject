"""
Unit tests for Catalog value objects.

Tests Price, Money, ProductName, Description, and Quantity value objects.
"""

import pytest
from decimal import Decimal

from modules.catalog.domain.value_objects import (
    Price,
    Money,
    ProductName,
    Description,
    Quantity,
)


# ============================================================================
# Money Value Object Tests
# ============================================================================

class TestMoney:
    """Test suite for Money value object."""

    def test_create_valid_money(self):
        """Test creating money with valid amount and currency."""
        money = Money(amount=Decimal("100.50"), currency="USD")

        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"

    def test_create_money_with_default_currency(self):
        """Test creating money defaults to USD."""
        money = Money(amount=Decimal("50.00"))

        assert money.currency == "USD"

    def test_create_money_with_negative_amount_raises_error(self):
        """Test creating money with negative amount raises error."""
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            Money(amount=Decimal("-10.00"), currency="USD")

    def test_create_money_with_zero_amount(self):
        """Test creating money with zero amount succeeds."""
        money = Money(amount=Decimal("0.00"), currency="USD")

        assert money.amount == Decimal("0.00")

    def test_create_money_with_invalid_currency_raises_error(self):
        """Test creating money with invalid currency raises error."""
        with pytest.raises(ValueError, match="Currency must be a valid"):
            Money(amount=Decimal("10.00"), currency="US")

    def test_create_money_with_empty_currency_raises_error(self):
        """Test creating money with empty currency raises error."""
        with pytest.raises(ValueError, match="Currency must be a valid"):
            Money(amount=Decimal("10.00"), currency="")

    def test_money_string_representation(self):
        """Test string representation of Money."""
        money = Money(amount=Decimal("99.99"), currency="USD")

        assert str(money) == "99.99 USD"

    def test_money_is_immutable(self):
        """Test that Money is frozen/immutable."""
        money = Money(amount=Decimal("10.00"), currency="USD")

        with pytest.raises(Exception):  # FrozenInstanceError
            money.amount = Decimal("20.00")


# ============================================================================
# Price Value Object Tests
# ============================================================================

class TestPrice:
    """Test suite for Price value object."""

    def test_create_valid_price(self):
        """Test creating price with valid amount."""
        price = Price(amount=Decimal("29.99"), currency="USD")

        assert price.amount == Decimal("29.99")
        assert price.currency == "USD"

    def test_create_price_with_zero_amount_raises_error(self):
        """Test creating price with zero amount raises error."""
        with pytest.raises(ValueError, match="Price cannot be zero"):
            Price(amount=Decimal("0.00"), currency="USD")

    def test_price_from_decimal(self):
        """Test creating Price from Decimal."""
        price = Price.from_decimal(Decimal("19.997"), "USD")

        # Should round to 2 decimal places
        assert price.amount == Decimal("20.00")

    def test_price_from_float(self):
        """Test creating Price from float."""
        price = Price.from_float(29.99, "USD")

        assert price.amount == Decimal("29.99")

    def test_price_from_int_cents(self):
        """Test creating Price from integer cents."""
        price = Price.from_int(2999, "USD")  # 2999 cents = $29.99

        assert price.amount == Decimal("29.99")

    def test_price_from_int_with_rounding(self):
        """Test Price from int handles rounding correctly."""
        price = Price.from_int(2997, "USD")  # 2997 cents

        assert price.amount == Decimal("29.97")

    def test_price_string_representation(self):
        """Test string representation of Price."""
        price = Price(amount=Decimal("99.99"), currency="EUR")

        assert str(price) == "99.99 EUR"


# ============================================================================
# ProductName Value Object Tests
# ============================================================================

class TestProductName:
    """Test suite for ProductName value object."""

    def test_create_valid_product_name(self):
        """Test creating product name with valid value."""
        name = ProductName(value="Laptop")

        assert str(name) == "Laptop"
        assert name.value == "Laptop"

    def test_create_product_name_with_whitespace_trims(self):
        """Test creating product name with whitespace trims it."""
        name = ProductName(value="  Laptop  ")

        assert str(name) == "Laptop"

    def test_create_product_name_with_empty_string_raises_error(self):
        """Test creating product name with empty string raises error."""
        with pytest.raises(ValueError, match="Product name cannot be empty"):
            ProductName(value="")

    def test_create_product_name_with_whitespace_only_raises_error(self):
        """Test creating product name with whitespace only raises error."""
        with pytest.raises(ValueError, match="Product name cannot be empty"):
            ProductName(value="   ")

    def test_create_product_name_with_too_long_name_raises_error(self):
        """Test creating product name too long raises error."""
        with pytest.raises(ValueError, match="cannot exceed"):
            ProductName(value="A" * 256)

    def test_create_product_name_with_max_length(self):
        """Test creating product name with max length succeeds."""
        name = ProductName(value="A" * 255)

        assert len(str(name)) == 255

    def test_create_product_name_with_min_length(self):
        """Test creating product name with min length succeeds."""
        name = ProductName(value="A")

        assert len(str(name)) == 1

    def test_product_name_is_immutable(self):
        """Test that ProductName is frozen/immutable."""
        name = ProductName(value="Laptop")

        with pytest.raises(Exception):  # FrozenInstanceError
            name.value = "Desktop"


# ============================================================================
# Description Value Object Tests
# ============================================================================

class TestDescription:
    """Test suite for Description value object."""

    def test_create_valid_description(self):
        """Test creating description with valid value."""
        description = Description(value="A great product")

        assert str(description) == "A great product"

    def test_create_description_with_whitespace_trims(self):
        """Test creating description with whitespace trims it."""
        description = Description(value="  A great product  ")

        assert str(description) == "A great product"

    def test_create_description_with_empty_string(self):
        """Test creating description with empty string succeeds."""
        description = Description(value="")

        assert str(description) == ""

    def test_create_description_with_too_long_text_raises_error(self):
        """Test creating description too long raises error."""
        with pytest.raises(ValueError, match="cannot exceed"):
            Description(value="A" * 5001)

    def test_create_description_with_max_length(self):
        """Test creating description with max length succeeds."""
        description = Description(value="A" * 5000)

        assert len(str(description)) == 5000

    def test_description_is_immutable(self):
        """Test that Description is frozen/immutable."""
        description = Description(value="Original description")

        with pytest.raises(Exception):  # FrozenInstanceError
            description.value = "New description"


# ============================================================================
# Quantity Value Object Tests
# ============================================================================

class TestQuantity:
    """Test suite for Quantity value object."""

    def test_create_valid_quantity(self):
        """Test creating quantity with valid value."""
        quantity = Quantity(value=50)

        assert quantity.value == 50
        assert int(quantity) == 50

    def test_create_quantity_with_minimum_value(self):
        """Test creating quantity with minimum value."""
        quantity = Quantity(value=Quantity.MIN_VALUE)

        assert quantity.value == 1

    def test_create_quantity_with_maximum_value(self):
        """Test creating quantity with maximum value."""
        quantity = Quantity(value=Quantity.MAX_VALUE)

        assert quantity.value == 1000000

    def test_create_quantity_below_minimum_raises_error(self):
        """Test creating quantity below minimum raises error."""
        with pytest.raises(ValueError, match="Quantity must be at least"):
            Quantity(value=0)

    def test_create_quantity_above_maximum_raises_error(self):
        """Test creating quantity above maximum raises error."""
        with pytest.raises(ValueError, match="Quantity cannot exceed"):
            Quantity(value=1000001)

    def test_create_quantity_with_non_integer_raises_error(self):
        """Test creating quantity with non-integer raises error."""
        with pytest.raises(ValueError, match="Quantity must be an integer"):
            Quantity(value=5.5)  # type: ignore

    def test_add_quantities(self):
        """Test adding two quantities."""
        quantity1 = Quantity(value=100)
        quantity2 = Quantity(value=250)

        result = quantity1 + quantity2

        assert result.value == 350

    def test_add_quantities_exceeds_maximum_raises_error(self):
        """Test adding quantities that exceed maximum raises error."""
        quantity1 = Quantity(value=900000)
        quantity2 = Quantity(value=200000)

        with pytest.raises(ValueError, match="cannot exceed"):
            _ = quantity1 + quantity2

    def test_subtract_quantities(self):
        """Test subtracting two quantities."""
        quantity1 = Quantity(value=500)
        quantity2 = Quantity(value=200)

        result = quantity1 - quantity2

        assert result.value == 300

    def test_subtract_quantities_below_minimum_raises_error(self):
        """Test subtracting quantities below minimum raises error."""
        quantity1 = Quantity(value=10)
        quantity2 = Quantity(value=10)

        with pytest.raises(ValueError, match="too low"):
            _ = quantity1 - quantity2

    def test_quantity_is_immutable(self):
        """Test that Quantity is frozen/immutable."""
        quantity = Quantity(value=50)

        with pytest.raises(Exception):  # FrozenInstanceError
            quantity.value = 100

    def test_quantity_equality(self):
        """Test quantity equality."""
        quantity1 = Quantity(value=100)
        quantity2 = Quantity(value=100)
        quantity3 = Quantity(value=200)

        assert quantity1 == quantity2
        assert quantity1 != quantity3

    def test_quantity_hash(self):
        """Test quantity can be used in sets and as dict keys."""
        quantity1 = Quantity(value=100)
        quantity2 = Quantity(value=100)
        quantity3 = Quantity(value=200)

        # Can be used in set
        quantities = {quantity1, quantity2, quantity3}
        assert len(quantities) == 2

        # Can be used as dict key
        quantity_dict = {quantity1: "first", quantity3: "second"}
        assert quantity_dict[quantity2] == "first"
