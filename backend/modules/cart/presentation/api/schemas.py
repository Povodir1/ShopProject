"""
API schemas for Cart module.

Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class CartItemResponse(BaseModel):
    """
    Cart item response schema.

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
    quantity: int = Field(..., ge=1, le=100)
    price_at_add: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    subtotal: float = Field(..., ge=0)

    model_config = {"json_schema_extra": {"example": {
        "id": "123e4567-e89b-12d3-a456-426614174100",
        "product_id": "123e4567-e89b-12d3-a456-426614174000",
        "quantity": 2,
        "price_at_add": 99.99,
        "currency": "USD",
        "subtotal": 199.98,
    }}}


class CartResponse(BaseModel):
    """
    Cart response schema.

    Attributes:
        id: Cart identifier
        session_id: Session identifier
        items: Cart items
        total: Cart total amount
        item_count: Total number of items
    """

    id: str
    session_id: str = Field(..., min_length=1)
    items: list[CartItemResponse] = Field(default_factory=list)
    total: float = Field(..., ge=0)
    item_count: int = Field(..., ge=0)

    model_config = {"json_schema_extra": {"example": {
        "id": "123e4567-e89b-12d3-a456-426614174099",
        "session_id": "guest-session-123",
        "items": [
            {
                "id": "123e4567-e89b-12d3-a456-426614174100",
                "product_id": "123e4567-e89b-12d3-a456-426614174000",
                "quantity": 2,
                "price_at_add": 99.99,
                "currency": "USD",
                "subtotal": 199.98,
            }
        ],
        "total": 199.98,
        "item_count": 2,
    }}}


class AddItemRequest(BaseModel):
    """
    Add item to cart request schema.

    Attributes:
        session_id: Session identifier
        product_id: Product identifier
        quantity: Quantity to add
    """

    session_id: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(default=1, ge=1, le=100)

    @field_validator("product_id")
    @classmethod
    def validate_product_id(cls, v: str) -> str:
        """Validate product ID is a valid UUID."""
        try:
            UUID(v)
        except ValueError as e:
            raise ValueError("Invalid product ID format") from e
        return v

    model_config = {"json_schema_extra": {"example": {
        "session_id": "guest-session-123",
        "product_id": "123e4567-e89b-12d3-a456-426614174000",
        "quantity": 2,
    }}}


class UpdateQuantityRequest(BaseModel):
    """
    Update cart item quantity request schema.

    Attributes:
        quantity: New quantity
    """

    quantity: int = Field(..., ge=1, le=100)

    model_config = {"json_schema_extra": {"example": {
        "quantity": 5,
    }}}


class ClearCartResponse(BaseModel):
    """
    Clear cart response schema.

    Attributes:
        message: Success message
    """

    message: str
