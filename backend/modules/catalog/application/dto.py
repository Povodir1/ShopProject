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
        search_query: Search by name or description
        price_min: Minimum price filter
        price_max: Maximum price filter
        in_stock: Only show in-stock items
        order_by: Sort field (name, price, created_at)
        order_dir: Sort direction (asc, desc)
        limit: Maximum results
        offset: Results offset
    """

    category_id: Optional[UUID] = None
    search_query: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    in_stock: bool = False
    order_by: str = "created_at"
    order_dir: str = "desc"
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

        # Validate order_by
        valid_fields = {"name", "price", "created_at"}
        if self.order_by not in valid_fields:
            self.order_by = "created_at"

        # Validate order_dir
        if self.order_dir not in {"asc", "desc"}:
            self.order_dir = "desc"

        # Validate price range
        if self.price_min is not None and self.price_min < 0:
            self.price_min = None
        if self.price_max is not None and self.price_max < 0:
            self.price_max = None
        if (
            self.price_min is not None
            and self.price_max is not None
            and self.price_min > self.price_max
        ):
            # Swap if min > max
            self.price_min, self.price_max = self.price_max, self.price_min
