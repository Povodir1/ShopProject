"""
Data Transfer Objects for Cart module.

Used to transfer data between layers.
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class CartItemDTO:
    """
    Cart item data transfer object.

    Attributes:
        id: Cart item identifier
        product_id: Product identifier
        quantity: Item quantity
        price_at_add: Unit price when item was added
        currency: Currency code
        subtotal: Subtotal for this item
    """

    id: str
    product_id: str
    quantity: int
    price_at_add: float
    currency: str
    subtotal: float


@dataclass
class CartDTO:
    """
    Cart data transfer object.

    Attributes:
        id: Cart identifier
        session_id: Session identifier
        items: Cart items
        total: Cart total amount
        item_count: Total number of items
    """

    id: str
    session_id: str
    items: list[CartItemDTO]
    total: float
    item_count: int


@dataclass
class AddItemCommand:
    """
    Command to add item to cart.

    Attributes:
        session_id: Session identifier
        product_id: Product identifier
        quantity: Quantity to add
    """

    session_id: str
    product_id: UUID
    quantity: int

    def __post_init__(self) -> None:
        """Validate command."""
        if self.quantity < 1:
            raise ValueError("Quantity must be at least 1")
        if self.quantity > 100:
            raise ValueError("Quantity cannot exceed 100")


@dataclass
class UpdateQuantityCommand:
    """
    Command to update cart item quantity.

    Attributes:
        session_id: Session identifier
        item_id: Cart item identifier
        quantity: New quantity
    """

    session_id: str
    item_id: UUID
    quantity: int

    def __post_init__(self) -> None:
        """Validate command."""
        if self.quantity < 1:
            raise ValueError("Quantity must be at least 1")
        if self.quantity > 100:
            raise ValueError("Quantity cannot exceed 100")


@dataclass
class RemoveItemCommand:
    """
    Command to remove item from cart.

    Attributes:
        session_id: Session identifier
        item_id: Cart item identifier
    """

    session_id: str
    item_id: UUID
