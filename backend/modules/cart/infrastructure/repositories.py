"""
SQLAlchemy repository implementations for Cart module.

Implements repository interfaces using SQLAlchemy.
"""

from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.cart.domain.entities import Cart, CartItem
from modules.cart.domain.repositories import ICartRepository
from modules.cart.infrastructure.orm import CartItemORM, CartORM


class SQLAlchemyCartRepository(ICartRepository):
    """
    SQLAlchemy implementation of cart repository.

    Implements ICartRepository using async SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def get_by_session_id(self, session_id: str) -> Optional[Cart]:
        """
        Get cart by session ID.

        Args:
            session_id: Session identifier

        Returns:
            Cart if found, None otherwise
        """
        result = await self._session.execute(
            select(CartORM)
            .options(selectinload(CartORM.items))
            .where(CartORM.session_id == session_id)
        )
        orm_cart = result.scalar_one_or_none()

        if orm_cart is None:
            return None

        return self._to_entity(orm_cart)

    async def save(self, cart: Cart) -> Cart:
        """
        Save cart (create or update).

        Args:
            cart: Cart entity to save

        Returns:
            Saved cart with ID assigned
        """
        if cart.id is None:
            # Create new cart
            orm_cart = CartORM(
                id=str(uuid4()),
                session_id=cart.session_id,
            )
            self._session.add(orm_cart)
        else:
            # Update existing cart
            orm_cart = await self._session.get(CartORM, str(cart.id))
            if orm_cart is None:
                raise ValueError(f"Cart with ID {cart.id} not found")
            orm_cart.session_id = cart.session_id

        # Flush to get ID if new
        await self._session.flush()

        # Handle items - delete all and re-create (simple approach)
        # For production, might want to track changes more efficiently
        await self._session.execute(
            delete(CartItemORM).where(CartItemORM.cart_id == orm_cart.id)
        )

        for item in cart.items:
            orm_item = CartItemORM(
                id=str(item.id) if item.id else str(uuid4()),
                cart_id=orm_cart.id,
                product_id=str(item.product_id),
                quantity=item.quantity,
                price_at_add=item.price_at_add,
                currency=item.currency,
            )
            self._session.add(orm_item)

        # Refresh to load relationships
        await self._session.refresh(orm_cart, attribute_names=["items"])

        return self._to_entity(orm_cart)

    async def delete(self, cart_id: UUID) -> None:
        """
        Delete cart by ID.

        Args:
            cart_id: Cart identifier
        """
        await self._session.execute(
            delete(CartORM).where(CartORM.id == str(cart_id))
        )

    async def get_item_by_id(self, item_id: UUID) -> Optional[CartItem]:
        """
        Get cart item by ID.

        Args:
            item_id: Cart item identifier

        Returns:
            CartItem if found, None otherwise
        """
        result = await self._session.execute(
            select(CartItemORM).where(CartItemORM.id == str(item_id))
        )
        orm_item = result.scalar_one_or_none()

        if orm_item is None:
            return None

        return self._to_item_entity(orm_item)

    async def delete_item(self, item_id: UUID) -> None:
        """
        Delete cart item by ID.

        Args:
            item_id: Cart item identifier
        """
        await self._session.execute(
            delete(CartItemORM).where(CartItemORM.id == str(item_id))
        )

    def _to_entity(self, orm_cart: CartORM) -> Cart:
        """
        Convert ORM model to domain entity.

        Args:
            orm_cart: CartORM instance

        Returns:
            Cart domain entity
        """
        items = [self._to_item_entity(item) for item in orm_cart.items]

        return Cart(
            id=UUID(orm_cart.id) if orm_cart.id else None,
            session_id=orm_cart.session_id,
            items=items,
            created_at=orm_cart.created_at,
            updated_at=orm_cart.updated_at,
        )

    def _to_item_entity(self, orm_item: CartItemORM) -> CartItem:
        """
        Convert ORM model to CartItem entity.

        Args:
            orm_item: CartItemORM instance

        Returns:
            CartItem domain entity
        """
        return CartItem(
            id=UUID(orm_item.id) if orm_item.id else None,
            cart_id=UUID(orm_item.cart_id),
            product_id=UUID(orm_item.product_id),
            quantity=orm_item.quantity,
            price_at_add=orm_item.price_at_add,
            currency=orm_item.currency,
            created_at=orm_item.created_at,
        )
