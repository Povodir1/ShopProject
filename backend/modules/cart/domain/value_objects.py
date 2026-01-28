"""
Value Objects for Cart module.

Immutable objects that represent concepts in the cart domain.
"""

from dataclasses import dataclass
from typing import Final
from uuid import UUID


@dataclass(frozen=True)
class SessionId:
    """
    Represents a session identifier for guest carts.

    Attributes:
        value: The session UUID

    Raises:
        ValueError: If value is not a valid UUID
    """

    value: str

    def __post_init__(self) -> None:
        """Validate session ID."""
        try:
            UUID(self.value)
        except ValueError as e:
            raise ValueError(f"Invalid session ID: {self.value}") from e

    def __str__(self) -> str:
        """String representation."""
        return self.value


@dataclass(frozen=True)
class Quantity:
    """
    Represents an item quantity in cart.

    Attributes:
        value: The quantity value

    Raises:
        ValueError: If quantity is not within valid range
    """

    value: int

    MIN_VALUE: Final[int] = 1
    MAX_VALUE: Final[int] = 100

    def __post_init__(self) -> None:
        """Validate quantity value."""
        if not isinstance(self.value, int):
            raise ValueError("Quantity must be an integer")
        if self.value < self.MIN_VALUE:
            raise ValueError(f"Quantity must be at least {self.MIN_VALUE}")
        if self.value > self.MAX_VALUE:
            raise ValueError(f"Quantity cannot exceed {self.MAX_VALUE}")

    def __int__(self) -> int:
        """Convert to integer."""
        return self.value

    def __add__(self, other: "Quantity") -> "Quantity":
        """Add quantities."""
        return Quantity(self.value + other.value)

    def __sub__(self, other: "Quantity") -> "Quantity":
        """Subtract quantities."""
        result = self.value - other.value
        if result < self.MIN_VALUE:
            raise ValueError("Resulting quantity is too low")
        return Quantity(result)
