"""
Data Transfer Objects for Catalog module.

Used to transfer data between layers.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class ProductDTO:
    """
    Product data transfer object.

    Attributes:
        id: Product identifier
        name: Product name
        description: Product description
        price: Product price amount
        currency: Price currency
        category_id: Category identifier
        stock: Available stock
        is_available: Availability status
    """

    id: str
    name: str
    description: str
    price: float
    currency: str
    category_id: Optional[str]
    stock: int
    is_available: bool


@dataclass
class ProductListDTO:
    """
    Product list data transfer object.

    Attributes:
        items: List of products
        total: Total number of products
        limit: Page size
        offset: Page offset
    """

    items: list[ProductDTO]
    total: int
    limit: int
    offset: int


@dataclass
class CategoryDTO:
    """
    Category data transfer object.

    Attributes:
        id: Category identifier
        name: Category name
        parent_id: Parent category identifier
    """

    id: str
    name: str
    parent_id: Optional[str]


@dataclass
class CategoryTreeDTO:
    """
    Category tree node data transfer object.

    Attributes:
        id: Category identifier
        name: Category name
        parent_id: Parent category identifier
        children: Child categories
    """

    id: str
    name: str
    parent_id: Optional[str]
    children: list["CategoryTreeDTO"]


@dataclass
class ProductFilterDTO:
    """
    Product filter parameters.

    Attributes:
        category_id: Filter by category
        limit: Maximum results
        offset: Results offset
    """

    category_id: Optional[UUID] = None
    limit: int = 100
    offset: int = 0

    def __post_init__(self) -> None:
        """Validate filter parameters."""
        if self.limit < 1:
            self.limit = 100
        if self.limit > 1000:
            self.limit = 1000
        if self.offset < 0:
            self.offset = 0
