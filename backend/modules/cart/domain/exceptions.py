"""
Domain-specific exceptions for Cart module.

Custom exceptions that represent domain error conditions.
"""

from core.exceptions import AppException, NotFoundException


class CartNotFoundException(NotFoundException):
    """
    Exception raised when cart is not found.

    Attributes:
        session_id: Session identifier
    """

    def __init__(self, session_id: str) -> None:
        """Initialize cart not found exception."""
        super().__init__(
            message=f"Cart with session ID '{session_id}' not found",
            resource_type="Cart",
            resource_id=session_id,
        )
        self.session_id = session_id


class CartItemNotFoundException(NotFoundException):
    """
    Exception raised when cart item is not found.

    Attributes:
        item_id: Cart item identifier
    """

    def __init__(self, item_id: str) -> None:
        """Initialize cart item not found exception."""
        super().__init__(
            message=f"Cart item with ID '{item_id}' not found",
            resource_type="CartItem",
            resource_id=item_id,
        )
        self.item_id = item_id


class InvalidQuantityError(AppException):
    """
    Exception raised when quantity is invalid.

    Attributes:
        message: Error message
    """

    def __init__(self, message: str) -> None:
        """Initialize invalid quantity error."""
        super().__init__(
            message=message,
            status_code=400,
        )


class ProductNotAvailableError(AppException):
    """
    Exception raised when product is not available.

    Attributes:
        product_id: Product identifier
        requested_quantity: Requested quantity
        available_stock: Available stock
    """

    def __init__(
        self,
        product_id: str,
        requested_quantity: int,
        available_stock: int,
    ) -> None:
        """Initialize product not available error."""
        super().__init__(
            message=f"Product '{product_id}' not available. "
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
