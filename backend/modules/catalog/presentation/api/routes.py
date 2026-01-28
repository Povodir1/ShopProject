"""
API routes for Catalog module.

FastAPI router for catalog endpoints.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.catalog.application.dto import ProductFilterDTO
from modules.catalog.application.services import CategoryService, ProductService
from modules.catalog.infrastructure.repositories import (
    SQLAlchemyCategoryRepository,
    SQLAlchemyProductRepository,
)
from modules.catalog.presentation.api.schemas import (
    CategoryResponse,
    CategoryTreeResponse,
    ProductListResponse,
    ProductResponse,
    ProductSearchQuery,
)

router = APIRouter()


async def get_product_service(
    db: AsyncSession = Depends(get_db),
) -> ProductService:
    """
    Get product service instance.

    Args:
        db: Database session

    Returns:
        ProductService instance
    """
    repository = SQLAlchemyProductRepository(db)
    return ProductService(repository)


async def get_category_service(
    db: AsyncSession = Depends(get_db),
) -> CategoryService:
    """
    Get category service instance.

    Args:
        db: Database session

    Returns:
        CategoryService instance
    """
    repository = SQLAlchemyCategoryRepository(db)
    return CategoryService(repository)


# =============================================================================
# Product endpoints
# =============================================================================


@router.get(
    "/products",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all products",
    description="Get a paginated list of products with optional filtering and sorting",
)
async def list_products(
    category_id: Optional[str] = Query(
        default=None,
        description="Filter by category ID",
    ),
    q: Optional[str] = Query(
        default=None,
        description="Search query for name or description",
        min_length=2,
    ),
    price_min: Optional[float] = Query(
        default=None,
        description="Minimum price filter",
        ge=0,
    ),
    price_max: Optional[float] = Query(
        default=None,
        description="Maximum price filter",
        ge=0,
    ),
    in_stock: bool = Query(
        default=False,
        description="Only show items in stock",
    ),
    order_by: str = Query(
        default="created_at",
        description="Sort field (name, price, created_at)",
    ),
    order_dir: str = Query(
        default="desc",
        description="Sort direction (asc, desc)",
        regex="^(asc|desc)$",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of products to return",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of products to skip",
    ),
    service: ProductService = Depends(get_product_service),
) -> ProductListResponse:
    """
    List all products with optional filtering and sorting.

    Args:
        category_id: Optional category filter
        q: Optional search query
        price_min: Optional minimum price
        price_max: Optional maximum price
        in_stock: Filter in-stock items only
        order_by: Sort field
        order_dir: Sort direction
        limit: Page size
        offset: Page offset
        service: Product service

    Returns:
        ProductListResponse with products and metadata
    """
    filters = ProductFilterDTO(
        category_id=UUID(category_id) if category_id else None,
        search_query=q,
        price_min=price_min,
        price_max=price_max,
        in_stock=in_stock,
        order_by=order_by,
        order_dir=order_dir,
        limit=limit,
        offset=offset,
    )

    result = await service.list_products(filters)

    return ProductListResponse(
        items=[_product_to_response(item) for item in result.items],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )


@router.get(
    "/products/search",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Search products",
    description="Search products by name or description",
)
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ProductService = Depends(get_product_service),
) -> list[ProductResponse]:
    """
    Search products by query string.

    Args:
        q: Search query
        limit: Maximum results
        offset: Results offset
        service: Product service

    Returns:
        List of matching products
    """
    results = await service.search_products(query=q, limit=limit, offset=offset)

    return [_product_to_response(item) for item in results]


@router.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get product by ID",
    description="Get detailed information about a specific product",
)
async def get_product(
    product_id: str,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """
    Get product by ID.

    Args:
        product_id: Product UUID
        service: Product service

    Returns:
        Product details

    Raises:
        ProductNotFoundException: If product not found
    """
    product = await service.get_product(UUID(product_id))

    return _product_to_response(product)


# =============================================================================
# Category endpoints
# =============================================================================


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List all categories",
    description="Get a list of all categories",
)
async def list_categories(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: CategoryService = Depends(get_category_service),
) -> list[CategoryResponse]:
    """
    List all categories.

    Args:
        limit: Maximum results
        offset: Results offset
        service: Category service

    Returns:
        List of categories
    """
    categories = await service.list_categories(limit=limit, offset=offset)

    return [_category_to_response(cat) for cat in categories]


@router.get(
    "/categories/tree",
    response_model=list[CategoryTreeResponse],
    status_code=status.HTTP_200_OK,
    summary="Get category tree",
    description="Get hierarchical tree of all categories",
)
async def get_category_tree(
    service: CategoryService = Depends(get_category_service),
) -> list[CategoryTreeResponse]:
    """
    Get category hierarchy tree.

    Args:
        service: Category service

    Returns:
        List of root categories with children
    """
    categories = await service.get_category_tree()

    return [_category_to_tree_response(cat) for cat in categories]


@router.get(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category by ID",
    description="Get detailed information about a specific category",
)
async def get_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    """
    Get category by ID.

    Args:
        category_id: Category UUID
        service: Category service

    Returns:
        Category details

    Raises:
        CategoryNotFoundException: If category not found
    """
    category = await service.get_category(UUID(category_id))

    return _category_to_response(category)


# =============================================================================
# Helper functions
# =============================================================================


def _product_to_response(dto) -> ProductResponse:
    """Convert ProductDTO to ProductResponse."""
    return ProductResponse(
        id=dto.id,
        name=dto.name,
        description=dto.description,
        price=dto.price,
        currency=dto.currency,
        category_id=dto.category_id,
        stock=dto.stock,
        is_available=dto.is_available,
        created_at=dto.created_at if hasattr(dto, "created_at") else None,
        updated_at=dto.updated_at if hasattr(dto, "updated_at") else None,
    )


def _category_to_response(dto) -> CategoryResponse:
    """Convert CategoryDTO to CategoryResponse."""
    return CategoryResponse(
        id=dto.id,
        name=dto.name,
        parent_id=dto.parent_id,
    )


def _category_to_tree_response(dto) -> CategoryTreeResponse:
    """Convert CategoryDTO to CategoryTreeResponse."""
    return CategoryTreeResponse(
        id=dto.id,
        name=dto.name,
        parent_id=dto.parent_id,
        children=[_category_to_tree_response(child) for child in dto.children],
    )
