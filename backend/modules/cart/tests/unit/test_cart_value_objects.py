"""
Unit tests for Cart value objects.

Tests SessionId and Quantity value objects for validation and immutability.
"""

import pytest
from uuid import uuid4

from modules.cart.domain.value_objects import SessionId, Quantity


# ============================================================================
# SessionId Value Object Tests
# ============================================================================

class TestSessionId:
    """Test suite for SessionId value object."""

    def test_create_valid_session_id(self):
        """Test creating session ID with valid UUID."""
        valid_uuid = str(uuid4())
        session_id = SessionId(valid_uuid)

        assert session_id.value == valid_uuid
        assert str(session_id) == valid_uuid

    def test_create_session_id_with_invalid_uuid(self):
        """Test creating session ID with invalid UUID raises error."""
        with pytest.raises(ValueError, match="Invalid session ID"):
            SessionId("not-a-uuid")

    def test_create_session_id_with_empty_string(self):
        """Test creating session ID with empty string raises error."""
        with pytest.raises(ValueError, match="Invalid session ID"):
            SessionId("")

    def test_create_session_id_with_malformed_uuid(self):
        """Test creating session ID with malformed UUID raises error."""
        with pytest.raises(ValueError, match="Invalid session ID"):
            SessionId("12345-67890-abcde")

    def test_session_id_is_immutable(self):
        """Test that SessionId is frozen/immutable."""
        session_id = SessionId(str(uuid4()))

        with pytest.raises(Exception):  # FrozenInstanceError from dataclasses
            session_id.value = "new-value"

    def test_session_id_string_representation(self):
        """Test string representation of SessionId."""
        uuid_str = str(uuid4())
        session_id = SessionId(uuid_str)

        assert str(session_id) == uuid_str
        assert repr(session_id).startswith("SessionId(")


# ============================================================================
# Quantity Value Object Tests
# ============================================================================

class TestQuantity:
    """Test suite for Quantity value object."""

    def test_create_valid_quantity(self):
        """Test creating quantity with valid value."""
        quantity = Quantity(5)

        assert quantity.value == 5
        assert int(quantity) == 5

    def test_create_quantity_with_minimum_value(self):
        """Test creating quantity with minimum value (1)."""
        quantity = Quantity(Quantity.MIN_VALUE)

        assert quantity.value == 1

    def test_create_quantity_with_maximum_value(self):
        """Test creating quantity with maximum value (100)."""
        quantity = Quantity(Quantity.MAX_VALUE)

        assert quantity.value == 100

    def test_create_quantity_below_minimum_raises_error(self):
        """Test creating quantity below minimum raises error."""
        with pytest.raises(ValueError, match="Quantity must be at least"):
            Quantity(0)

    def test_create_quantity_above_maximum_raises_error(self):
        """Test creating quantity above maximum raises error."""
        with pytest.raises(ValueError, match="Quantity cannot exceed"):
            Quantity(101)

    def test_create_quantity_with_negative_value_raises_error(self):
        """Test creating quantity with negative value raises error."""
        with pytest.raises(ValueError, match="Quantity must be at least"):
            Quantity(-1)

    def test_create_quantity_with_non_integer_raises_error(self):
        """Test creating quantity with non-integer raises error."""
        with pytest.raises(ValueError, match="Quantity must be an integer"):
            Quantity(5.5)  # type: ignore

    def test_add_quantities(self):
        """Test adding two quantities."""
        quantity1 = Quantity(5)
        quantity2 = Quantity(10)

        result = quantity1 + quantity2

        assert result.value == 15
        assert isinstance(result, Quantity)

    def test_add_quantities_exceeds_maximum(self):
        """Test adding quantities that exceed maximum raises error."""
        quantity1 = Quantity(60)
        quantity2 = Quantity(50)

        with pytest.raises(ValueError, match="cannot exceed"):
            _ = quantity1 + quantity2

    def test_subtract_quantities(self):
        """Test subtracting two quantities."""
        quantity1 = Quantity(10)
        quantity2 = Quantity(3)

        result = quantity1 - quantity2

        assert result.value == 7
        assert isinstance(result, Quantity)

    def test_subtract_quantities_below_minimum(self):
        """Test subtracting quantities below minimum raises error."""
        quantity1 = Quantity(5)
        quantity2 = Quantity(5)

        with pytest.raises(ValueError, match="too low"):
            _ = quantity1 - quantity2

    def test_quantity_is_immutable(self):
        """Test that Quantity is frozen/immutable."""
        quantity = Quantity(5)

        with pytest.raises(Exception):  # FrozenInstanceError from dataclasses
            quantity.value = 10

    def test_quantity_integer_conversion(self):
        """Test converting quantity to integer."""
        quantity = Quantity(42)

        assert int(quantity) == 42
        # Can be used in arithmetic
        assert int(quantity) + 10 == 52

    def test_quantity_string_representation(self):
        """Test string representation of Quantity."""
        quantity = Quantity(5)

        # Quantity uses dataclass default repr
        assert repr(quantity).startswith("Quantity(")
        # Can convert to int
        assert int(quantity) == 5

    def test_quantity_equality(self):
        """Test quantity equality."""
        quantity1 = Quantity(5)
        quantity2 = Quantity(5)
        quantity3 = Quantity(10)

        # Value objects with same value should be equal
        assert quantity1 == quantity2
        assert quantity1 != quantity3

    def test_quantity_hash(self):
        """Test quantity can be used in sets and as dict keys."""
        quantity1 = Quantity(5)
        quantity2 = Quantity(5)
        quantity3 = Quantity(10)

        # Can be used in set
        quantities = {quantity1, quantity2, quantity3}
        assert len(quantities) == 2  # quantity1 and quantity2 are equal

        # Can be used as dict key
        quantity_dict = {quantity1: "first", quantity3: "second"}
        assert quantity_dict[quantity2] == "first"  # quantity1 == quantity2
