"""
API routes for Cart module.

FastAPI router for cart endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.cart.application.dto import AddItemCommand, RemoveItemCommand, UpdateQuantityCommand
from modules.cart.application.services import CartService
from modules.cart.infrastructure.repositories import (
    SQLAlchemyCartRepository,
)
from modules.cart.infrastructure.orm import CartORM
from modules.cart.presentation.api.schemas import (
    AddItemRequest,
    CartResponse,
    ClearCartResponse,
    CartItemResponse,
    UpdateQuantityRequest,
)
from modules.catalog.infrastructure.repositories import (
    SQLAlchemyProductRepository,
)

router = APIRouter()


async def get_cart_service(
    db: AsyncSession = Depends(get_db),
) -> CartService:
    """
    Get cart service instance.

    Args:
        db: Database session

    Returns:
        CartService instance
    """
    cart_repository = SQLAlchemyCartRepository(db)
    product_repository = SQLAlchemyProductRepository(db)
    return CartService(cart_repository, product_repository)


# =============================================================================
# Cart endpoints
# =============================================================================


@router.get(
    "/cart",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Get cart",
    description="Get cart by session ID. Creates new cart if not exists.",
)
async def get_cart(
    session_id: str = Query(..., description="Session identifier"),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    """
    Get cart by session ID.

    Args:
        session_id: Session identifier
        service: Cart service

    Returns:
        Cart details
    """
    cart = await service.get_cart(session_id)

    return _to_response(cart)


@router.post(
    "/cart/items",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to cart",
    description="Add product to cart. Creates new cart if not exists.",
)
async def add_item(
    request: AddItemRequest,
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    """
    Add item to cart.

    Args:
        request: Add item request
        service: Cart service

    Returns:
        Updated cart

    Raises:
        ProductNotAvailableError: If product not available
        InvalidQuantityError: If quantity is invalid
    """
    command = AddItemCommand(
        session_id=request.session_id,
        product_id=UUID(request.product_id),
        quantity=request.quantity,
    )

    cart = await service.add_item(command)

    return _to_response(cart)


@router.put(
    "/cart/items/{item_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Update cart item quantity",
    description="Update quantity of item in cart.",
)
async def update_item_quantity(
    item_id: str,
    request: UpdateQuantityRequest,
    session_id: str = Query(..., description="Session identifier"),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    """
    Update cart item quantity.

    Args:
        item_id: Cart item identifier
        request: Update quantity request
        session_id: Session identifier
        service: Cart service

    Returns:
        Updated cart

    Raises:
        CartNotFoundException: If cart not found
        CartItemNotFoundException: If item not found
        InvalidQuantityError: If quantity is invalid
    """
    command = UpdateQuantityCommand(
        session_id=session_id,
        item_id=UUID(item_id),
        quantity=request.quantity,
    )

    cart = await service.update_quantity(command)

    return _to_response(cart)


@router.delete(
    "/cart/items/{item_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove item from cart",
    description="Remove item from cart.",
)
async def remove_item(
    item_id: str,
    session_id: str = Query(..., description="Session identifier"),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    """
    Remove item from cart.

    Args:
        item_id: Cart item identifier
        session_id: Session identifier
        service: Cart service

    Returns:
        Updated cart

    Raises:
        CartNotFoundException: If cart not found
        CartItemNotFoundException: If item not found
    """
    command = RemoveItemCommand(
        session_id=session_id,
        item_id=UUID(item_id),
    )

    cart = await service.remove_item(command)

    return _to_response(cart)


@router.delete(
    "/cart",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Clear cart",
    description="Remove all items from cart.",
)
async def clear_cart(
    session_id: str = Query(..., description="Session identifier"),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    """
    Clear all items from cart.

    Args:
        session_id: Session identifier
        service: Cart service

    Returns:
        Cleared cart

    Raises:
        CartNotFoundException: If cart not found
    """
    cart = await service.clear_cart(session_id)

    return _to_response(cart)


# =============================================================================
# Helper functions
# =============================================================================


def _to_response(dto) -> CartResponse:
    """Convert CartDTO to CartResponse."""
    items = [
        CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_add=item.price_at_add,
            currency=item.currency,
            subtotal=item.subtotal,
        )
        for item in dto.items
    ]

    return CartResponse(
        id=dto.id,
        session_id=dto.session_id,
        items=items,
        total=dto.total,
        item_count=dto.item_count,
    )
