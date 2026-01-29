"""
Unit tests for Cart DTOs.

Tests data transfer objects for validation and serialization.
"""

import pytest
from uuid import uuid4

from modules.cart.application.dto import (
    CartItemDTO,
    CartDTO,
    AddItemCommand,
    UpdateQuantityCommand,
    RemoveItemCommand,
)


# ============================================================================
# CartItemDTO Tests
# ============================================================================

class TestCartItemDTO:
    """Test suite for CartItemDTO."""

    def test_create_cart_item_dto(self):
        """Test creating cart item DTO."""
        item_id = str(uuid4())
        product_id = str(uuid4())

        dto = CartItemDTO(
            id=item_id,
            product_id=product_id,
            quantity=3,
            price_at_add=19.99,
            currency="USD",
            subtotal=59.97,
        )

        assert dto.id == item_id
        assert dto.product_id == product_id
        assert dto.quantity == 3
        assert dto.price_at_add == 19.99
        assert dto.currency == "USD"
        assert dto.subtotal == 59.97


# ============================================================================
# CartDTO Tests
# ============================================================================

class TestCartDTO:
    """Test suite for CartDTO."""

    def test_create_cart_dto(self):
        """Test creating cart DTO."""
        cart_id = str(uuid4())
        session_id = str(uuid4())

        items = [
            CartItemDTO(
                id=str(uuid4()),
                product_id=str(uuid4()),
                quantity=2,
                price_at_add=10.0,
                currency="USD",
                subtotal=20.0,
            )
        ]

        dto = CartDTO(
            id=cart_id,
            session_id=session_id,
            items=items,
            total=20.0,
            item_count=2,
        )

        assert dto.id == cart_id
        assert dto.session_id == session_id
        assert len(dto.items) == 1
        assert dto.total == 20.0
        assert dto.item_count == 2


# ============================================================================
# AddItemCommand Tests
# ============================================================================

class TestAddItemCommand:
    """Test suite for AddItemCommand."""

    def test_create_valid_command(self):
        """Test creating valid add item command."""
        session_id = str(uuid4())
        product_id = uuid4()

        command = AddItemCommand(
            session_id=session_id,
            product_id=product_id,
            quantity=5,
        )

        assert command.session_id == session_id
        assert command.product_id == product_id
        assert command.quantity == 5

    def test_create_command_with_min_quantity(self):
        """Test creating command with minimum quantity."""
        command = AddItemCommand(
            session_id=str(uuid4()),
            product_id=uuid4(),
            quantity=1,
        )

        assert command.quantity == 1

    def test_create_command_with_max_quantity(self):
        """Test creating command with maximum quantity."""
        command = AddItemCommand(
            session_id=str(uuid4()),
            product_id=uuid4(),
            quantity=100,
        )

        assert command.quantity == 100

    def test_create_command_with_zero_quantity_raises_error(self):
        """Test creating command with zero quantity raises error."""
        with pytest.raises(ValueError, match="Quantity must be at least 1"):
            AddItemCommand(
                session_id=str(uuid4()),
                product_id=uuid4(),
                quantity=0,
            )

    def test_create_command_with_negative_quantity_raises_error(self):
        """Test creating command with negative quantity raises error."""
        with pytest.raises(ValueError, match="Quantity must be at least 1"):
            AddItemCommand(
                session_id=str(uuid4()),
                product_id=uuid4(),
                quantity=-1,
            )

    def test_create_command_with_excessive_quantity_raises_error(self):
        """Test creating command with excessive quantity raises error."""
        with pytest.raises(ValueError, match="Quantity cannot exceed 100"):
            AddItemCommand(
                session_id=str(uuid4()),
                product_id=uuid4(),
                quantity=101,
            )


# ============================================================================
# UpdateQuantityCommand Tests
# ============================================================================

class TestUpdateQuantityCommand:
    """Test suite for UpdateQuantityCommand."""

    def test_create_valid_command(self):
        """Test creating valid update quantity command."""
        session_id = str(uuid4())
        item_id = uuid4()

        command = UpdateQuantityCommand(
            session_id=session_id,
            item_id=item_id,
            quantity=10,
        )

        assert command.session_id == session_id
        assert command.item_id == item_id
        assert command.quantity == 10

    def test_create_command_with_min_quantity(self):
        """Test creating command with minimum quantity."""
        command = UpdateQuantityCommand(
            session_id=str(uuid4()),
            item_id=uuid4(),
            quantity=1,
        )

        assert command.quantity == 1

    def test_create_command_with_max_quantity(self):
        """Test creating command with maximum quantity."""
        command = UpdateQuantityCommand(
            session_id=str(uuid4()),
            item_id=uuid4(),
            quantity=100,
        )

        assert command.quantity == 100

    def test_create_command_with_zero_quantity_raises_error(self):
        """Test creating command with zero quantity raises error."""
        with pytest.raises(ValueError, match="Quantity must be at least 1"):
            UpdateQuantityCommand(
                session_id=str(uuid4()),
                item_id=uuid4(),
                quantity=0,
            )

    def test_create_command_with_negative_quantity_raises_error(self):
        """Test creating command with negative quantity raises error."""
        with pytest.raises(ValueError, match="Quantity must be at least 1"):
            UpdateQuantityCommand(
                session_id=str(uuid4()),
                item_id=uuid4(),
                quantity=-1,
            )

    def test_create_command_with_excessive_quantity_raises_error(self):
        """Test creating command with excessive quantity raises error."""
        with pytest.raises(ValueError, match="Quantity cannot exceed 100"):
            UpdateQuantityCommand(
                session_id=str(uuid4()),
                item_id=uuid4(),
                quantity=101,
            )


# ============================================================================
# RemoveItemCommand Tests
# ============================================================================

class TestRemoveItemCommand:
    """Test suite for RemoveItemCommand."""

    def test_create_valid_command(self):
        """Test creating valid remove item command."""
        session_id = str(uuid4())
        item_id = uuid4()

        command = RemoveItemCommand(
            session_id=session_id,
            item_id=item_id,
        )

        assert command.session_id == session_id
        assert command.item_id == item_id
