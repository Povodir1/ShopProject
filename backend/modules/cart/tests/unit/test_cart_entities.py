"""
Unit tests for Cart domain entities.

Tests Cart and CartItem entities for business logic and validation.
"""

import pytest
from uuid import uuid4
from datetime import datetime

from modules.cart.domain.entities import Cart, CartItem
from modules.cart.domain.value_objects import SessionId
from modules.catalog.domain.value_objects import Price
from modules.cart.tests.fixtures import (
    create_empty_cart,
    create_test_price,
    generate_cart_id,
    generate_product_id,
    generate_session_id,
)


# ============================================================================
# CartItem Entity Tests
# ============================================================================

class TestCartItem:
    """Test suite for CartItem entity."""

    def test_create_cart_item_with_valid_data(self):
        """Test creating cart item with valid data."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(29.99)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=5,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        assert item.cart_id == cart_id
        assert item.product_id == product_id
        assert item.quantity == 5
        assert item.price_at_add == 2999
        assert item.currency == "USD"

    def test_create_cart_item_with_min_quantity(self):
        """Test creating cart item with minimum quantity (1)."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=CartItem.MIN_QUANTITY,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        assert item.quantity == CartItem.MIN_QUANTITY

    def test_create_cart_item_with_max_quantity(self):
        """Test creating cart item with maximum quantity (100)."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=CartItem.MAX_QUANTITY,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        assert item.quantity == CartItem.MAX_QUANTITY

    def test_create_cart_item_with_invalid_quantity_too_low(self):
        """Test creating cart item fails with quantity below minimum."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        with pytest.raises(ValueError, match="Quantity must be at least"):
            CartItem(
                id=None,
                cart_id=cart_id,
                product_id=product_id,
                quantity=0,
                price_at_add=int(price.amount * 100),
                currency=price.currency,
            )

    def test_create_cart_item_with_invalid_quantity_too_high(self):
        """Test creating cart item fails with quantity above maximum."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        with pytest.raises(ValueError, match="Quantity cannot exceed"):
            CartItem(
                id=None,
                cart_id=cart_id,
                product_id=product_id,
                quantity=101,
                price_at_add=int(price.amount * 100),
                currency=price.currency,
            )

    def test_create_cart_item_with_negative_price(self):
        """Test creating cart item fails with negative price."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()

        with pytest.raises(ValueError, match="Price cannot be negative"):
            CartItem(
                id=None,
                cart_id=cart_id,
                product_id=product_id,
                quantity=5,
                price_at_add=-100,
                currency="USD",
            )

    def test_create_cart_item_with_invalid_currency(self):
        """Test creating cart item fails with invalid currency."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()

        with pytest.raises(ValueError, match="Currency must be a valid"):
            CartItem(
                id=None,
                cart_id=cart_id,
                product_id=product_id,
                quantity=5,
                price_at_add=2999,
                currency="US",  # Invalid: should be 3 characters
            )

    def test_cart_item_subtotal_calculation(self):
        """Test subtotal calculation for cart item."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(19.99)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=3,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        # 19.99 * 3 = 59.97
        assert float(item.subtotal) == 59.97

    def test_set_quantity_with_valid_value(self):
        """Test setting quantity with valid value."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=5,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        item.set_quantity(10)
        assert item.quantity == 10

    def test_set_quantity_with_invalid_value(self):
        """Test setting quantity with invalid value raises error."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=5,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        with pytest.raises(ValueError):
            item.set_quantity(0)

    def test_increase_quantity(self):
        """Test increasing quantity."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=5,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        item.increase_quantity(3)
        assert item.quantity == 8

    def test_increase_quantity_exceeds_maximum(self):
        """Test increasing quantity beyond maximum raises error."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=95,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        with pytest.raises(ValueError, match="cannot exceed"):
            item.increase_quantity(10)

    def test_increase_quantity_with_negative_amount(self):
        """Test increasing quantity with negative amount raises error."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=5,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        with pytest.raises(ValueError, match="Amount must be positive"):
            item.increase_quantity(-1)

    def test_decrease_quantity(self):
        """Test decreasing quantity."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=10,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        item.decrease_quantity(3)
        assert item.quantity == 7

    def test_decrease_quantity_below_minimum(self):
        """Test decreasing quantity below minimum raises error."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=5,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        with pytest.raises(ValueError, match="must be at least"):
            item.decrease_quantity(5)

    def test_decrease_quantity_with_negative_amount(self):
        """Test decreasing quantity with negative amount raises error."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=10,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        with pytest.raises(ValueError, match="Amount must be positive"):
            item.decrease_quantity(-1)

    def test_to_dict(self):
        """Test converting cart item to dictionary."""
        cart_id = generate_cart_id()
        product_id = generate_product_id()
        price = create_test_price(19.99)

        item = CartItem(
            id=None,
            cart_id=cart_id,
            product_id=product_id,
            quantity=2,
            price_at_add=int(price.amount * 100),
            currency=price.currency,
        )

        result = item.to_dict()

        assert result["cart_id"] == str(cart_id)
        assert result["product_id"] == str(product_id)
        assert result["quantity"] == 2
        assert result["price_at_add"] == 39.98
        assert result["currency"] == "USD"
        assert result["unit_price"] == 19.99


# ============================================================================
# Cart Entity Tests
# ============================================================================

class TestCart:
    """Test suite for Cart entity."""

    def test_create_empty_cart(self):
        """Test creating empty cart."""
        session_id = generate_session_id()

        cart = Cart(id=None, session_id=session_id)

        assert cart.session_id == session_id
        assert len(cart.items) == 0
        assert cart.total == 0
        assert cart.item_count == 0

    def test_create_cart_with_empty_session_id_raises_error(self):
        """Test creating cart with empty session ID raises error."""
        with pytest.raises(ValueError, match="Session ID cannot be empty"):
            Cart(id=None, session_id="")

    def test_create_cart_with_whitespace_session_id_raises_error(self):
        """Test creating cart with whitespace session ID raises error."""
        with pytest.raises(ValueError, match="Session ID cannot be empty"):
            Cart(id=None, session_id="   ")

    def test_add_item_to_cart(self):
        """Test adding item to cart."""
        session_id = generate_session_id()
        product_id = generate_product_id()
        price = create_test_price(29.99)

        cart = Cart(id=None, session_id=session_id)
        item = cart.add_item(product_id=product_id, quantity=2, price=price)

        assert len(cart.items) == 1
        assert cart.item_count == 2
        assert item.product_id == product_id
        assert item.quantity == 2

    def test_add_existing_item_increases_quantity(self):
        """Test adding existing item increases quantity."""
        session_id = generate_session_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        cart = Cart(id=None, session_id=session_id)
        cart.add_item(product_id=product_id, quantity=2, price=price)
        cart.add_item(product_id=product_id, quantity=3, price=price)

        assert len(cart.items) == 1
        assert cart.item_count == 5
        assert cart.items[0].quantity == 5

    def test_add_item_exceeds_max_quantity(self):
        """Test adding item that would exceed maximum quantity raises error."""
        session_id = generate_session_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        cart = Cart(id=None, session_id=session_id)
        cart.add_item(product_id=product_id, quantity=50, price=price)

        with pytest.raises(ValueError, match="Quantity cannot exceed"):
            cart.add_item(product_id=product_id, quantity=60, price=price)

    def test_remove_item_from_cart(self):
        """Test removing item from cart."""
        session_id = generate_session_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        cart = Cart(id=None, session_id=session_id)
        item = cart.add_item(product_id=product_id, quantity=2, price=price)

        cart.remove_item(item.id)

        assert len(cart.items) == 0
        assert cart.item_count == 0

    def test_remove_nonexistent_item_raises_error(self):
        """Test removing nonexistent item raises error."""
        session_id = generate_session_id()
        cart = Cart(id=None, session_id=session_id)

        with pytest.raises(ValueError, match="not found in cart"):
            cart.remove_item(uuid4())

    def test_update_item_quantity(self):
        """Test updating item quantity."""
        session_id = generate_session_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        cart = Cart(id=None, session_id=session_id)
        item = cart.add_item(product_id=product_id, quantity=2, price=price)

        cart.update_item_quantity(item.id, 5)

        assert item.quantity == 5
        assert cart.item_count == 5

    def test_update_nonexistent_item_quantity_raises_error(self):
        """Test updating nonexistent item quantity raises error."""
        session_id = generate_session_id()
        cart = Cart(id=None, session_id=session_id)

        with pytest.raises(ValueError, match="not found in cart"):
            cart.update_item_quantity(uuid4(), 5)

    def test_clear_cart(self):
        """Test clearing all items from cart."""
        session_id = generate_session_id()
        product_id1 = generate_product_id()
        product_id2 = generate_product_id()
        price = create_test_price(10.0)

        cart = Cart(id=None, session_id=session_id)
        cart.add_item(product_id=product_id1, quantity=2, price=price)
        cart.add_item(product_id=product_id2, quantity=3, price=price)

        cart.clear()

        assert len(cart.items) == 0
        assert cart.item_count == 0
        assert cart.total == 0

    def test_merge_carts(self):
        """Test merging two carts."""
        session_id1 = generate_session_id()
        session_id2 = generate_session_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        cart1 = Cart(id=None, session_id=session_id1)
        cart1.add_item(product_id=product_id, quantity=2, price=price)

        cart2 = Cart(id=None, session_id=session_id2)
        cart2.add_item(product_id=product_id, quantity=3, price=price)

        cart1.merge(cart2)

        # Should have merged quantities
        assert len(cart1.items) == 1
        assert cart1.item_count == 5

    def test_merge_carts_with_different_products(self):
        """Test merging carts with different products."""
        session_id1 = generate_session_id()
        session_id2 = generate_session_id()
        product_id1 = generate_product_id()
        product_id2 = generate_product_id()
        price = create_test_price(10.0)

        cart1 = Cart(id=None, session_id=session_id1)
        cart1.add_item(product_id=product_id1, quantity=2, price=price)

        cart2 = Cart(id=None, session_id=session_id2)
        cart2.add_item(product_id=product_id2, quantity=3, price=price)

        cart1.merge(cart2)

        # Should have both items
        assert len(cart1.items) == 2
        assert cart1.item_count == 5

    def test_cart_total_calculation(self):
        """Test cart total calculation."""
        session_id = generate_session_id()
        product_id1 = generate_product_id()
        product_id2 = generate_product_id()
        price1 = create_test_price(10.0)
        price2 = create_test_price(20.0)

        cart = Cart(id=None, session_id=session_id)
        cart.add_item(product_id=product_id1, quantity=2, price=price1)
        cart.add_item(product_id=product_id2, quantity=3, price=price2)

        # 2 * 10.0 + 3 * 20.0 = 20.0 + 60.0 = 80.0
        assert float(cart.total) == 80.0

    def test_find_item_by_product_id(self):
        """Test finding item by product ID."""
        session_id = generate_session_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        cart = Cart(id=None, session_id=session_id)
        added_item = cart.add_item(product_id=product_id, quantity=2, price=price)

        found_item = cart.find_item(product_id)

        assert found_item is not None
        assert found_item.id == added_item.id

    def test_find_nonexistent_item_by_product_id(self):
        """Test finding nonexistent item by product ID."""
        session_id = generate_session_id()
        cart = Cart(id=None, session_id=session_id)

        found_item = cart.find_item(generate_product_id())

        assert found_item is None

    def test_find_item_by_id(self):
        """Test finding item by cart item ID."""
        session_id = generate_session_id()
        product_id = generate_product_id()
        price = create_test_price(10.0)

        cart = Cart(id=None, session_id=session_id)
        added_item = cart.add_item(product_id=product_id, quantity=2, price=price)

        found_item = cart.find_item_by_id(added_item.id)

        assert found_item is not None
        assert found_item.id == added_item.id

    def test_to_dict(self):
        """Test converting cart to dictionary."""
        session_id = generate_session_id()
        product_id = generate_product_id()
        price = create_test_price(19.99)

        cart = Cart(id=None, session_id=session_id)
        cart.add_item(product_id=product_id, quantity=2, price=price)

        result = cart.to_dict()

        assert result["session_id"] == session_id
        assert len(result["items"]) == 1
        assert result["item_count"] == 2
        assert result["total"] == 39.98
