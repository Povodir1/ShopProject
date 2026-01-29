"""
Unit tests for Cart application services.

Tests CartService use cases with mocked dependencies.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, AsyncMock

from modules.cart.application.services import CartService
from modules.cart.application.dto import AddItemCommand, UpdateQuantityCommand, RemoveItemCommand
from modules.cart.domain.entities import Cart, CartItem
from modules.cart.domain.exceptions import (
    CartNotFoundException,
    CartItemNotFoundException,
    InvalidQuantityError,
    ProductNotAvailableError,
)
from modules.cart.domain.value_objects import Quantity
from modules.catalog.domain.entities import Product
from modules.catalog.domain.value_objects import Price


# ============================================================================
# CartService Unit Tests
# ============================================================================

class TestCartService:
    """Test suite for CartService."""

    @pytest.mark.asyncio
    async def test_get_cart_creates_new_cart_if_not_exists(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test getting cart creates new one if doesn't exist."""
        session_id = str(uuid4())
        mock_cart_repository.get_by_session_id.return_value = None
        mock_cart_repository.save.return_value = Cart(
            id=uuid4(),
            session_id=session_id,
            items=[],
        )

        service = CartService(mock_cart_repository, mock_product_repository)
        cart_dto = await service.get_cart(session_id)

        mock_cart_repository.get_by_session_id.assert_called_once_with(session_id)
        mock_cart_repository.save.assert_called_once()
        assert cart_dto.session_id == session_id
        assert cart_dto.item_count == 0

    @pytest.mark.asyncio
    async def test_get_cart_returns_existing_cart(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test getting cart returns existing one."""
        session_id = str(uuid4())
        cart = Cart(id=uuid4(), session_id=session_id)

        mock_cart_repository.get_by_session_id.return_value = cart

        service = CartService(mock_cart_repository, mock_product_repository)
        cart_dto = await service.get_cart(session_id)

        mock_cart_repository.get_by_session_id.assert_called_once_with(session_id)
        mock_cart_repository.save.assert_not_called()
        assert cart_dto.session_id == session_id

    @pytest.mark.asyncio
    async def test_add_item_success(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test successfully adding item to cart."""
        session_id = str(uuid4())
        product_id = uuid4()
        price = Price.from_float(29.99, "USD")

        # Setup mocks
        product = Mock(spec=Product)
        product.id = product_id
        product.price = price
        product.stock = 50
        product.is_available = Mock(return_value=True)

        mock_product_repository.get_by_id.return_value = product
        mock_cart_repository.get_by_session_id.return_value = None

        saved_cart = Cart(id=uuid4(), session_id=session_id)
        saved_cart.add_item(product_id, 2, price)
        mock_cart_repository.save.return_value = saved_cart

        # Execute
        command = AddItemCommand(
            session_id=session_id,
            product_id=product_id,
            quantity=2,
        )
        service = CartService(mock_cart_repository, mock_product_repository)
        cart_dto = await service.add_item(command)

        # Verify
        mock_product_repository.get_by_id.assert_called_once_with(product_id)
        product.is_available.assert_called_once_with(2)
        mock_cart_repository.save.assert_called_once()
        assert cart_dto.item_count == 2

    @pytest.mark.asyncio
    async def test_add_item_product_not_found_raises_error(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test adding item for non-existent product raises error."""
        session_id = str(uuid4())
        product_id = uuid4()

        mock_product_repository.get_by_id.return_value = None

        command = AddItemCommand(
            session_id=session_id,
            product_id=product_id,
            quantity=2,
        )
        service = CartService(mock_cart_repository, mock_product_repository)

        with pytest.raises(ProductNotAvailableError):
            await service.add_item(command)

    @pytest.mark.asyncio
    async def test_add_item_insufficient_stock_raises_error(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test adding item with insufficient stock raises error."""
        session_id = str(uuid4())
        product_id = uuid4()
        price = Price.from_float(29.99, "USD")

        product = Mock(spec=Product)
        product.id = product_id
        product.price = price
        product.stock = 5
        product.is_available = Mock(return_value=False)

        mock_product_repository.get_by_id.return_value = product

        command = AddItemCommand(
            session_id=session_id,
            product_id=product_id,
            quantity=10,  # Requesting more than available
        )
        service = CartService(mock_cart_repository, mock_product_repository)

        with pytest.raises(ProductNotAvailableError) as exc_info:
            await service.add_item(command)

        assert exc_info.value.available_stock == 5
        assert exc_info.value.requested_quantity == 10

    @pytest.mark.asyncio
    async def test_update_quantity_success(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test successfully updating item quantity."""
        session_id = str(uuid4())
        product_id = uuid4()
        item_id = uuid4()
        price = Price.from_float(10.0, "USD")

        cart = Cart(id=uuid4(), session_id=session_id)
        cart.add_item(product_id, 2, price)
        cart.items[0].id = item_id

        mock_cart_repository.get_by_session_id.return_value = cart
        mock_cart_repository.save.return_value = cart

        command = UpdateQuantityCommand(
            session_id=session_id,
            item_id=item_id,
            quantity=5,
        )
        service = CartService(mock_cart_repository, mock_product_repository)
        cart_dto = await service.update_quantity(command)

        assert cart_dto.items[0].quantity == 5
        mock_cart_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_quantity_cart_not_found_raises_error(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test updating quantity for non-existent cart raises error."""
        session_id = str(uuid4())

        mock_cart_repository.get_by_session_id.return_value = None

        command = UpdateQuantityCommand(
            session_id=session_id,
            item_id=uuid4(),
            quantity=5,
        )
        service = CartService(mock_cart_repository, mock_product_repository)

        with pytest.raises(CartNotFoundException):
            await service.update_quantity(command)

    @pytest.mark.asyncio
    async def test_update_quantity_invalid_quantity_raises_error(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test updating quantity with invalid value raises error during command creation."""
        # UpdateQuantityCommand validates quantity in __post_init__
        # so we test that validation happens at the command level
        with pytest.raises(ValueError, match="Quantity must be at least 1"):
            UpdateQuantityCommand(
                session_id=str(uuid4()),
                item_id=uuid4(),
                quantity=0,  # Invalid quantity
            )

    @pytest.mark.asyncio
    async def test_remove_item_success(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test successfully removing item from cart."""
        session_id = str(uuid4())
        product_id = uuid4()
        item_id = uuid4()
        price = Price.from_float(10.0, "USD")

        cart = Cart(id=uuid4(), session_id=session_id)
        cart.add_item(product_id, 2, price)
        cart.items[0].id = item_id

        mock_cart_repository.get_by_session_id.return_value = cart
        mock_cart_repository.save.return_value = cart

        command = RemoveItemCommand(
            session_id=session_id,
            item_id=item_id,
        )
        service = CartService(mock_cart_repository, mock_product_repository)
        cart_dto = await service.remove_item(command)

        assert len(cart_dto.items) == 0
        assert cart_dto.item_count == 0
        mock_cart_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_item_cart_not_found_raises_error(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test removing item from non-existent cart raises error."""
        session_id = str(uuid4())

        mock_cart_repository.get_by_session_id.return_value = None

        command = RemoveItemCommand(
            session_id=session_id,
            item_id=uuid4(),
        )
        service = CartService(mock_cart_repository, mock_product_repository)

        with pytest.raises(CartNotFoundException):
            await service.remove_item(command)

    @pytest.mark.asyncio
    async def test_remove_item_not_found_raises_error(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test removing non-existent item raises error."""
        session_id = str(uuid4())

        cart = Cart(id=uuid4(), session_id=session_id)

        mock_cart_repository.get_by_session_id.return_value = cart

        command = RemoveItemCommand(
            session_id=session_id,
            item_id=uuid4(),
        )
        service = CartService(mock_cart_repository, mock_product_repository)

        with pytest.raises(CartItemNotFoundException):
            await service.remove_item(command)

    @pytest.mark.asyncio
    async def test_clear_cart_success(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test successfully clearing cart."""
        session_id = str(uuid4())
        product_id = uuid4()
        price = Price.from_float(10.0, "USD")

        cart = Cart(id=uuid4(), session_id=session_id)
        cart.add_item(product_id, 2, price)

        mock_cart_repository.get_by_session_id.return_value = cart
        mock_cart_repository.save.return_value = cart

        service = CartService(mock_cart_repository, mock_product_repository)
        cart_dto = await service.clear_cart(session_id)

        assert len(cart_dto.items) == 0
        assert cart_dto.item_count == 0
        assert cart_dto.total == 0
        mock_cart_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_cart_not_found_raises_error(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test clearing non-existent cart raises error."""
        session_id = str(uuid4())

        mock_cart_repository.get_by_session_id.return_value = None

        service = CartService(mock_cart_repository, mock_product_repository)

        with pytest.raises(CartNotFoundException):
            await service.clear_cart(session_id)

    @pytest.mark.asyncio
    async def test_to_dto_conversion(
        self, mock_cart_repository, mock_product_repository
    ):
        """Test Cart to DTO conversion."""
        session_id = str(uuid4())
        product_id = uuid4()
        price = Price.from_float(19.99, "USD")

        cart = Cart(id=uuid4(), session_id=session_id)
        cart.add_item(product_id, 2, price)

        mock_cart_repository.get_by_session_id.return_value = cart

        service = CartService(mock_cart_repository, mock_product_repository)
        cart_dto = await service.get_cart(session_id)

        assert cart_dto.session_id == session_id
        assert len(cart_dto.items) == 1
        assert cart_dto.items[0].quantity == 2
        assert cart_dto.items[0].price_at_add == 19.99
        assert cart_dto.items[0].currency == "USD"
        assert cart_dto.items[0].subtotal == 39.98
        assert cart_dto.total == 39.98
        assert cart_dto.item_count == 2
