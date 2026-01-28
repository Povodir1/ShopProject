"""
Value Objects for Catalog module.

Immutable objects that represent concepts in the domain.
Follows Value Object pattern from DDD.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Final


@dataclass(frozen=True)
class Money:
    """
    Represents a monetary value.

    Attributes:
        amount: The monetary amount
        currency: Currency code (e.g., "USD", "EUR")

    Raises:
        ValueError: If amount is negative or currency is invalid
    """

    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        """Validate money value."""
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a valid 3-letter code")

    def __str__(self) -> str:
        """String representation of money."""
        return f"{self.amount:.2f} {self.currency}"


@dataclass(frozen=True)
class Price(Money):
    """
    Represents a product price.

    Extends Money with price-specific validation.
    """

    def __post_init__(self) -> None:
        """Validate price value."""
        super().__post_init__()
        if self.amount == 0:
            raise ValueError("Price cannot be zero")

    @classmethod
    def from_decimal(cls, amount: Decimal, currency: str = "USD") -> "Price":
        """
        Create Price from Decimal.

        Args:
            amount: Price amount
            currency: Currency code

        Returns:
            Price instance
        """
        # Round to 2 decimal places (cents)
        rounded_amount = amount.quantize(Decimal("0.01"))
        return cls(amount=rounded_amount, currency=currency)

    @classmethod
    def from_float(cls, amount: float, currency: str = "USD") -> "Price":
        """
        Create Price from float.

        Args:
            amount: Price amount
            currency: Currency code

        Returns:
            Price instance
        """
        return cls.from_decimal(Decimal(str(amount)), currency)

    @classmethod
    def from_int(cls, amount: int, currency: str = "USD") -> "Price":
        """
        Create Price from integer cents.

        Args:
            amount: Price in cents
            currency: Currency code

        Returns:
            Price instance
        """
        return cls.from_decimal(Decimal(amount) / Decimal("100"), currency)


@dataclass(frozen=True)
class Quantity:
    """
    Represents a product quantity.

    Attributes:
        value: The quantity value

    Raises:
        ValueError: If quantity is not positive
    """

    value: int

    MIN_VALUE: Final[int] = 1
    MAX_VALUE: Final[int] = 1000000

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


@dataclass(frozen=True)
class ProductName:
    """
    Represents a product name.

    Attributes:
        value: The product name

    Raises:
        ValueError: If name is empty or too long
    """

    value: str

    MIN_LENGTH: Final[int] = 1
    MAX_LENGTH: Final[int] = 255

    def __post_init__(self) -> None:
        """Validate product name."""
        if not self.value or len(self.value.strip()) < self.MIN_LENGTH:
            raise ValueError("Product name cannot be empty")
        if len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"Product name cannot exceed {self.MAX_LENGTH} characters"
            )

    def __str__(self) -> str:
        """String representation."""
        return self.value.strip()


@dataclass(frozen=True)
class Description:
    """
    Represents a product description.

    Attributes:
        value: The description text

    Raises:
        ValueError: If description is too long
    """

    value: str

    MAX_LENGTH: Final[int] = 5000

    def __post_init__(self) -> None:
        """Validate description."""
        if len(self.value) > self.MAX_LENGTH:
            raise ValueError(
                f"Description cannot exceed {self.MAX_LENGTH} characters"
            )

    def __str__(self) -> str:
        """String representation."""
        return self.value.strip()
