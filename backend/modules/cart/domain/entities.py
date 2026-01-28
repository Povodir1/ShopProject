"""
Domain entities for Cart module.

Entities are objects with identity and lifecycle.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Final, Optional
from uuid import UUID, uuid4

from modules.catalog.domain.value_objects import Price


@dataclass
class CartItem:
    """
    CartItem entity.

    Represents a product in the shopping cart.

    Attributes:
        id: Unique identifier (None for new entities)
        cart_id: Parent cart identifier
        product_id: Product identifier
        quantity: Item quantity
        price_at_add: Price when item was added (in cents)
        currency: Currency code
        created_at: Creation timestamp
    """

    id: Optional[UUID]
    cart_id: UUID
    product_id: UUID
    quantity: int
    price_at_add: int  # Stored as cents
    currency: str = "USD"
    created_at: datetime = field(default_factory=datetime.utcnow)

    MIN_QUANTITY: Final[int] = 1
    MAX_QUANTITY: Final[int] = 100

    def __post_init__(self) -> None:
        """Validate cart item."""
        if self.quantity < self.MIN_QUANTITY:
            raise ValueError(f"Quantity must be at least {self.MIN_QUANTITY}")
        if self.quantity > self.MAX_QUANTITY:
            raise ValueError(f"Quantity cannot exceed {self.MAX_QUANTITY}")
        if self.price_at_add < 0:
            raise ValueError("Price cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a valid 3-letter code")

    @property
    def subtotal(self) -> Decimal:
        """
        Calculate subtotal for this item.

        Returns:
            Decimal: Subtotal amount
        """
        return Decimal(self.price_at_add * self.quantity) / Decimal(100)

    def set_quantity(self, quantity: int) -> None:
        """
        Set new quantity.

        Args:
            quantity: New quantity

        Raises:
            ValueError: If quantity is invalid
        """
        if quantity < self.MIN_QUANTITY:
            raise ValueError(f"Quantity must be at least {self.MIN_QUANTITY}")
        if quantity > self.MAX_QUANTITY:
            raise ValueError(f"Quantity cannot exceed {self.MAX_QUANTITY}")
        self.quantity = quantity

    def increase_quantity(self, amount: int = 1) -> None:
        """
        Increase quantity.

        Args:
            amount: Amount to increase

        Raises:
            ValueError: If resulting quantity exceeds maximum
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        new_quantity = self.quantity + amount
        if new_quantity > self.MAX_QUANTITY:
            raise ValueError(
                f"Resulting quantity cannot exceed {self.MAX_QUANTITY}"
            )

        self.quantity = new_quantity

    def decrease_quantity(self, amount: int = 1) -> None:
        """
        Decrease quantity.

        Args:
            amount: Amount to decrease

        Raises:
            ValueError: If resulting quantity is below minimum
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        new_quantity = self.quantity - amount
        if new_quantity < self.MIN_QUANTITY:
            raise ValueError(
                f"Resulting quantity must be at least {self.MIN_QUANTITY}"
            )

        self.quantity = new_quantity

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id) if self.id else None,
            "cart_id": str(self.cart_id),
            "product_id": str(self.product_id),
            "quantity": self.quantity,
            "price_at_add": float(self.subtotal),
            "currency": self.currency,
            "unit_price": float(Decimal(self.price_at_add) / Decimal(100)),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Cart:
    """
    Cart entity.

    Represents a shopping cart (guest or user).

    Attributes:
        id: Unique identifier (None for new entities)
        session_id: Session identifier for guest carts
        items: Cart items
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: Optional[UUID]
    session_id: str
    items: list[CartItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate cart."""
        if not self.session_id or len(self.session_id.strip()) == 0:
            raise ValueError("Session ID cannot be empty")

    def add_item(
        self,
        product_id: UUID,
        quantity: int,
        price: Price,
    ) -> CartItem:
        """
        Add item to cart.

        If item already exists, updates quantity.

        Args:
            product_id: Product identifier
            quantity: Quantity to add
            price: Product price (fixed at add time)

        Returns:
            CartItem: Added or updated item

        Raises:
            ValueError: If quantity is invalid
        """
        # Check if item already exists
        existing_item = self.find_item(product_id)

        if existing_item:
            # Update quantity of existing item
            new_quantity = existing_item.quantity + quantity
            if new_quantity > CartItem.MAX_QUANTITY:
                raise ValueError(
                    f"Quantity cannot exceed {CartItem.MAX_QUANTITY}"
                )
            existing_item.quantity = new_quantity
            item = existing_item
        else:
            # Create new item
            item = CartItem(
                id=None,
                cart_id=self.id if self.id else uuid4(),
                product_id=product_id,
                quantity=quantity,
                price_at_add=int(price.amount * 100),  # Convert to cents
                currency=price.currency,
            )
            self.items.append(item)

        self.updated_at = datetime.utcnow()
        return item

    def remove_item(self, item_id: UUID) -> None:
        """
        Remove item from cart.

        Args:
            item_id: Cart item identifier

        Raises:
            ValueError: If item not found
        """
        item = self.find_item_by_id(item_id)

        if item is None:
            raise ValueError(f"Item with ID '{item_id}' not found in cart")

        self.items.remove(item)
        self.updated_at = datetime.utcnow()

    def update_item_quantity(self, item_id: UUID, quantity: int) -> CartItem:
        """
        Update item quantity.

        Args:
            item_id: Cart item identifier
            quantity: New quantity

        Returns:
            CartItem: Updated item

        Raises:
            ValueError: If item not found or quantity invalid
        """
        item = self.find_item_by_id(item_id)

        if item is None:
            raise ValueError(f"Item with ID '{item_id}' not found in cart")

        item.set_quantity(quantity)
        self.updated_at = datetime.utcnow()

        return item

    def clear(self) -> None:
        """Remove all items from cart."""
        self.items.clear()
        self.updated_at = datetime.utcnow()

    def merge(self, other: "Cart") -> None:
        """
        Merge another cart into this one.

        Args:
            other: Cart to merge from

        Note:
            Quantities are summed for matching products.
            Price from this cart is kept.
        """
        for other_item in other.items:
            existing = self.find_item(other_item.product_id)

            if existing:
                # Sum quantities
                new_quantity = existing.quantity + other_item.quantity
                if new_quantity > CartItem.MAX_QUANTITY:
                    # Cap at maximum
                    new_quantity = CartItem.MAX_QUANTITY
                existing.quantity = new_quantity
            else:
                # Add item (copy with this cart's ID)
                new_item = CartItem(
                    id=None,
                    cart_id=self.id if self.id else uuid4(),
                    product_id=other_item.product_id,
                    quantity=other_item.quantity,
                    price_at_add=other_item.price_at_add,
                    currency=other_item.currency,
                )
                self.items.append(new_item)

        self.updated_at = datetime.utcnow()

    @property
    def total(self) -> Decimal:
        """
        Calculate cart total.

        Returns:
            Decimal: Total amount
        """
        return sum(item.subtotal for item in self.items)

    @property
    def item_count(self) -> int:
        """
        Get total number of items.

        Returns:
            int: Total item count
        """
        return sum(item.quantity for item in self.items)

    def find_item(self, product_id: UUID) -> Optional[CartItem]:
        """
        Find item by product ID.

        Args:
            product_id: Product identifier

        Returns:
            CartItem if found, None otherwise
        """
        for item in self.items:
            if item.product_id == product_id:
                return item
        return None

    def find_item_by_id(self, item_id: UUID) -> Optional[CartItem]:
        """
        Find item by cart item ID.

        Args:
            item_id: Cart item identifier

        Returns:
            CartItem if found, None otherwise
        """
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id) if self.id else None,
            "session_id": self.session_id,
            "items": [item.to_dict() for item in self.items],
            "total": float(self.total),
            "item_count": self.item_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
