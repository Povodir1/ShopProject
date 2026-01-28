"""
Domain-specific exceptions for Catalog module.

Custom exceptions that represent domain error conditions.
"""

from core.exceptions import AppException, NotFoundException


class ProductNotFoundException(NotFoundException):
    """
    Exception raised when product is not found.

    Attributes:
        product_id: ID of the product that was not found
    """

    def __init__(self, product_id: str) -> None:
        """Initialize product not found exception."""
        super().__init__(
            message=f"Product with ID '{product_id}' not found",
            resource_type="Product",
            resource_id=product_id,
        )
        self.product_id = product_id


class CategoryNotFoundException(NotFoundException):
    """
    Exception raised when category is not found.

    Attributes:
        category_id: ID of the category that was not found
    """

    def __init__(self, category_id: str) -> None:
        """Initialize category not found exception."""
        super().__init__(
            message=f"Category with ID '{category_id}' not found",
            resource_type="Category",
            resource_id=category_id,
        )
        self.category_id = category_id


class InsufficientStockError(AppException):
    """
    Exception raised when product stock is insufficient.

    Attributes:
        product_id: ID of the product
        requested_quantity: Requested quantity
        available_stock: Available stock
    """

    def __init__(self, product_id: str, requested_quantity: int, available_stock: int) -> None:
        """Initialize insufficient stock error."""
        super().__init__(
            message=f"Insufficient stock for product '{product_id}'. "
            f"Requested: {requested_quantity}, Available: {available_stock}",
            status_code=400,
            details={
                "product_id": product_id,
                "requested_quantity": requested_quantity,
                "available_stock": available_stock,
            },
        )
        self.product_id = product_id
        self.requested_quantity = requested_quantity
        self.available_stock = available_stock
