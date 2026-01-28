"""
API schemas for Catalog module.

Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ProductResponse(BaseModel):
    """
    Product response schema.

    Attributes:
        id: Product identifier
        name: Product name
        description: Product description
        price: Product price
        currency: Price currency
        category_id: Category identifier
        stock: Available stock
        is_available: Availability status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: str
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., max_length=5000)
    price: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    category_id: Optional[str] = None
    stock: int = Field(..., ge=0)
    is_available: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"json_schema_extra": {"example": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Wireless Headphones",
        "description": "High-quality wireless headphones with noise cancellation",
        "price": 99.99,
        "currency": "USD",
        "category_id": "123e4567-e89b-12d3-a456-426614174001",
        "stock": 50,
        "is_available": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }}}


class ProductListResponse(BaseModel):
    """
    Product list response schema.

    Attributes:
        items: List of products
        total: Total number of products
        limit: Page size
        offset: Page offset
    """

    items: list[ProductResponse]
    total: int
    limit: int = Field(..., ge=1, le=1000)
    offset: int = Field(..., ge=0)


class ProductSearchQuery(BaseModel):
    """
    Product search query schema.

    Attributes:
        q: Search query string
        limit: Maximum results
        offset: Results offset
    """

    q: str = Field(..., min_length=2, max_length=100)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class CategoryResponse(BaseModel):
    """
    Category response schema.

    Attributes:
        id: Category identifier
        name: Category name
        parent_id: Parent category identifier
    """

    id: str
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[str] = None

    model_config = {"json_schema_extra": {"example": {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "name": "Electronics",
        "parent_id": None,
    }}}


class CategoryTreeResponse(BaseModel):
    """
    Category tree response schema.

    Attributes:
        id: Category identifier
        name: Category name
        parent_id: Parent category identifier
        children: Child categories
    """

    id: str
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[str] = None
    children: list["CategoryTreeResponse"] = Field(default_factory=list)

    model_config = {"json_schema_extra": {"example": {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "name": "Electronics",
        "parent_id": None,
        "children": [
            {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "name": "Phones",
                "parent_id": "123e4567-e89b-12d3-a456-426614174001",
                "children": [],
            }
        ],
    }}}


# Enable forward references for recursive models
CategoryTreeResponse.model_rebuild()
