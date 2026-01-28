"""
Application services for Cart module.

Contains use cases for cart operations.
Follows Single Responsibility Principle (SRP).
"""

from uuid import UUID

from modules.cart.application.dto import (
    AddItemCommand,
    CartDTO,
    CartItemDTO,
    RemoveItemCommand,
    UpdateQuantityCommand,
)
from modules.cart.domain.entities import Cart
from modules.cart.domain.exceptions import (
    CartItemNotFoundException,
    CartNotFoundException,
    InvalidQuantityError,
    ProductNotAvailableError,
)
from modules.cart.domain.repositories import ICartRepository
from modules.catalog.domain.entities import Product
from modules.catalog.domain.repositories import IProductRepository


class CartService:
    """
    Cart application service.

    Handles cart-related use cases.
    """

    def __init__(
        self,
        cart_repository: ICartRepository,
        product_repository: IProductRepository,
    ) -> None:
        """
        Initialize cart service.

        Args:
            cart_repository: Cart repository instance
            product_repository: Product repository instance
        """
        self._cart_repository = cart_repository
        self._product_repository = product_repository

    async def get_cart(self, session_id: str) -> CartDTO:
        """
        Get cart by session ID.

        Creates new cart if not exists.

        Args:
            session_id: Session identifier

        Returns:
            CartDTO
        """
        cart = await self._cart_repository.get_by_session_id(session_id)

        if cart is None:
            # Create new empty cart
            cart = Cart(id=None, session_id=session_id)
            cart = await self._cart_repository.save(cart)

        return self._to_dto(cart)

    async def add_item(self, command: AddItemCommand) -> CartDTO:
        """
        Add item to cart.

        Args:
            command: Add item command

        Returns:
            Updated CartDTO

        Raises:
            ProductNotAvailableError: If product not available
            InvalidQuantityError: If quantity is invalid
        """
        # Get product to check availability and get price
        product = await self._product_repository.get_by_id(command.product_id)

        if product is None:
            raise ProductNotAvailableError(
                product_id=str(command.product_id),
                requested_quantity=command.quantity,
                available_stock=0,
            )

        if not product.is_available(command.quantity):
            raise ProductNotAvailableError(
                product_id=str(command.product_id),
                requested_quantity=command.quantity,
                available_stock=product.stock,
            )

        # Get or create cart
        cart = await self._cart_repository.get_by_session_id(command.session_id)
        if cart is None:
            cart = Cart(id=None, session_id=command.session_id)

        # Add item to cart (price is fixed at add time)
        cart.add_item(
            product_id=command.product_id,
            quantity=command.quantity,
            price=product.price,
        )

        # Save cart
        saved_cart = await self._cart_repository.save(cart)

        return self._to_dto(saved_cart)

    async def update_quantity(self, command: UpdateQuantityCommand) -> CartDTO:
        """
        Update cart item quantity.

        Args:
            command: Update quantity command

        Returns:
            Updated CartDTO

        Raises:
            CartNotFoundException: If cart not found
            CartItemNotFoundException: If item not found
            InvalidQuantityError: If quantity is invalid
        """
        # Get cart
        cart = await self._cart_repository.get_by_session_id(command.session_id)

        if cart is None:
            raise CartNotFoundException(command.session_id)

        # Update item quantity
        try:
            cart.update_item_quantity(command.item_id, command.quantity)
        except ValueError as e:
            raise InvalidQuantityError(str(e)) from e

        # Save cart
        saved_cart = await self._cart_repository.save(cart)

        return self._to_dto(saved_cart)

    async def remove_item(self, command: RemoveItemCommand) -> CartDTO:
        """
        Remove item from cart.

        Args:
            command: Remove item command

        Returns:
            Updated CartDTO

        Raises:
            CartNotFoundException: If cart not found
            CartItemNotFoundException: If item not found
        """
        # Get cart
        cart = await self._cart_repository.get_by_session_id(command.session_id)

        if cart is None:
            raise CartNotFoundException(command.session_id)

        # Remove item
        try:
            cart.remove_item(command.item_id)
        except ValueError as e:
            raise CartItemNotFoundException(str(command.item_id)) from e

        # Save cart
        saved_cart = await self._cart_repository.save(cart)

        return self._to_dto(saved_cart)

    async def clear_cart(self, session_id: str) -> CartDTO:
        """
        Clear all items from cart.

        Args:
            session_id: Session identifier

        Returns:
            Cleared CartDTO

        Raises:
            CartNotFoundException: If cart not found
        """
        # Get cart
        cart = await self._cart_repository.get_by_session_id(session_id)

        if cart is None:
            raise CartNotFoundException(session_id)

        # Clear cart
        cart.clear()

        # Save cart
        saved_cart = await self._cart_repository.save(cart)

        return self._to_dto(saved_cart)

    def _to_dto(self, cart: Cart) -> CartDTO:
        """
        Convert Cart entity to DTO.

        Args:
            cart: Cart entity

        Returns:
            CartDTO
        """
        return CartDTO(
            id=str(cart.id) if cart.id else "",
            session_id=cart.session_id,
            items=[self._item_to_dto(item) for item in cart.items],
            total=float(cart.total),
            item_count=cart.item_count,
        )

    def _item_to_dto(self, item) -> CartItemDTO:
        """
        Convert CartItem entity to DTO.

        Args:
            item: CartItem entity

        Returns:
            CartItemDTO
        """
        return CartItemDTO(
            id=str(item.id) if item.id else "",
            product_id=str(item.product_id),
            quantity=item.quantity,
            price_at_add=float(item.subtotal) / item.quantity,
            currency=item.currency,
            subtotal=float(item.subtotal),
        )
