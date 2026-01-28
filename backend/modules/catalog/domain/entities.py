"""
Domain entities for Catalog module.

Entities are objects with identity and lifecycle.
Follows Entity pattern from DDD.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Final, Optional
from uuid import UUID, uuid4

from .value_objects import Price, ProductName, Quantity


@dataclass
class Category:
    """
    Category entity.

    Represents a product category with hierarchical structure.

    Attributes:
        id: Unique identifier (None for new entities)
        name: Category name
        parent_id: Parent category ID for hierarchy
        children: Child categories
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: Optional[UUID]
    name: str
    parent_id: Optional[UUID] = None
    children: list["Category"] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    MIN_NAME_LENGTH: Final[int] = 1
    MAX_NAME_LENGTH: Final[int] = 100

    def __post_init__(self) -> None:
        """Validate category."""
        if not self.name or len(self.name.strip()) < self.MIN_NAME_LENGTH:
            raise ValueError("Category name cannot be empty")
        if len(self.name) > self.MAX_NAME_LENGTH:
            raise ValueError(
                f"Category name cannot exceed {self.MAX_NAME_LENGTH} characters"
            )

        # Check for circular reference
        if self._creates_circular_reference():
            raise ValueError("Circular reference detected in category hierarchy")

    def _creates_circular_reference(self) -> bool:
        """
        Check if adding this category creates a circular reference.

        Returns:
            True if circular reference would be created
        """
        if self.parent_id is None or self.id is None:
            return False

        # Check if parent_id is in the descendants
        return any(
            child.id == self.parent_id
            for child in self._get_all_descendants()
        )

    def _get_all_descendants(self) -> list["Category"]:
        """
        Get all descendant categories recursively.

        Returns:
            List of all descendant categories
        """
        descendants: list[Category] = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child._get_all_descendants())
        return descendants

    def add_child(self, child: "Category") -> None:
        """
        Add a child category.

        Args:
            child: Child category to add

        Raises:
            ValueError: If child creates circular reference
        """
        if child.id == self.id:
            raise ValueError("Cannot add category as its own child")

        # Temporarily add child and check for circular reference
        self.children.append(child)
        child.parent_id = self.id

        if self._creates_circular_reference():
            self.children.remove(child)
            child.parent_id = None
            raise ValueError("Adding child creates circular reference")

        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id) if self.id else None,
            "name": self.name,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Product:
    """
    Product entity.

    Represents a product in the catalog.

    Attributes:
        id: Unique identifier (None for new entities)
        name: Product name
        description: Product description
        price: Product price
        category_id: Category identifier
        stock: Available stock quantity
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: Optional[UUID]
    name: str
    description: str
    price: Price
    category_id: Optional[UUID]
    stock: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    MIN_NAME_LENGTH: Final[int] = 1
    MAX_NAME_LENGTH: Final[int] = 255
    MAX_DESCRIPTION_LENGTH: Final[int] = 5000

    def __post_init__(self) -> None:
        """Validate product."""
        if not self.name or len(self.name.strip()) < self.MIN_NAME_LENGTH:
            raise ValueError("Product name cannot be empty")
        if len(self.name) > self.MAX_NAME_LENGTH:
            raise ValueError(
                f"Product name cannot exceed {self.MAX_NAME_LENGTH} characters"
            )
        if len(self.description) > self.MAX_DESCRIPTION_LENGTH:
            raise ValueError(
                f"Description cannot exceed {self.MAX_DESCRIPTION_LENGTH} characters"
            )
        if self.stock < 0:
            raise ValueError("Stock cannot be negative")

    def is_available(self, requested_quantity: int = 1) -> bool:
        """
        Check if product is available in requested quantity.

        Args:
            requested_quantity: Quantity to check availability for

        Returns:
            True if product is available
        """
        return self.stock >= requested_quantity

    def reduce_stock(self, quantity: int) -> None:
        """
        Reduce stock by specified quantity.

        Args:
            quantity: Quantity to reduce

        Raises:
            ValueError: If insufficient stock
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if not self.is_available(quantity):
            raise ValueError(
                f"Insufficient stock. Requested: {quantity}, Available: {self.stock}"
            )

        self.stock -= quantity
        self.updated_at = datetime.utcnow()

    def increase_stock(self, quantity: int) -> None:
        """
        Increase stock by specified quantity.

        Args:
            quantity: Quantity to increase

        Raises:
            ValueError: If quantity is not positive
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        self.stock += quantity
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id) if self.id else None,
            "name": self.name,
            "description": self.description,
            "price": float(self.price.amount),
            "currency": self.price.currency,
            "category_id": str(self.category_id) if self.category_id else None,
            "stock": self.stock,
            "is_available": self.is_available(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
