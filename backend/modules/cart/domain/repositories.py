"""
Repository interfaces for Cart module.

Defines abstract contracts for data access.
Follows Dependency Inversion Principle (DIP) - high-level modules depend on abstractions.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from modules.cart.domain.entities import Cart, CartItem


class ICartRepository(ABC):
    """
    Cart repository interface.

    Defines contract for cart data access operations.
    """

    @abstractmethod
    async def get_by_session_id(self, session_id: str) -> Optional[Cart]:
        """
        Get cart by session ID.

        Args:
            session_id: Session identifier

        Returns:
            Cart if found, None otherwise
        """
        pass

    @abstractmethod
    async def save(self, cart: Cart) -> Cart:
        """
        Save cart (create or update).

        Args:
            cart: Cart entity to save

        Returns:
            Saved cart with ID assigned
        """
        pass

    @abstractmethod
    async def delete(self, cart_id: UUID) -> None:
        """
        Delete cart by ID.

        Args:
            cart_id: Cart identifier
        """
        pass

    @abstractmethod
    async def get_item_by_id(self, item_id: UUID) -> Optional[CartItem]:
        """
        Get cart item by ID.

        Args:
            item_id: Cart item identifier

        Returns:
            CartItem if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete_item(self, item_id: UUID) -> None:
        """
        Delete cart item by ID.

        Args:
            item_id: Cart item identifier
        """
        pass
