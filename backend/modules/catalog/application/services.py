"""
Application services for Catalog module.

Contains use cases for catalog operations.
Follows Single Responsibility Principle (SRP).
"""

from typing import Optional
from uuid import UUID

from modules.catalog.application.dto import (
    CategoryDTO,
    CategoryTreeDTO,
    ProductDTO,
    ProductFilterDTO,
    ProductListDTO,
)
from modules.catalog.domain.entities import Category, Product
from modules.catalog.domain.exceptions import CategoryNotFoundException, ProductNotFoundException
from modules.catalog.domain.repositories import ICategoryRepository, IProductRepository


class ProductService:
    """
    Product application service.

    Handles product-related use cases.
    """

    def __init__(self, product_repository: IProductRepository) -> None:
        """
        Initialize product service.

        Args:
            product_repository: Product repository instance
        """
        self._product_repository = product_repository

    async def get_product(self, product_id: UUID) -> ProductDTO:
        """
        Get product by ID.

        Args:
            product_id: Product UUID

        Returns:
            ProductDTO

        Raises:
            ProductNotFoundException: If product not found
        """
        product = await self._product_repository.get_by_id(product_id)

        if product is None:
            raise ProductNotFoundException(str(product_id))

        return self._to_dto(product)

    async def list_products(
        self, filters: ProductFilterDTO
    ) -> ProductListDTO:
        """
        List products with filtering.

        Args:
            filters: Filter parameters

        Returns:
            ProductListDTO with products and metadata
        """
        products = await self._product_repository.get_all(
            limit=filters.limit,
            offset=filters.offset,
            category_id=filters.category_id,
        )

        total = await self._product_repository.count(
            category_id=filters.category_id
        )

        return ProductListDTO(
            items=[self._to_dto(p) for p in products],
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    async def search_products(
        self,
        query: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProductDTO]:
        """
        Search products by query.

        Args:
            query: Search query string
            limit: Maximum results
            offset: Results offset

        Returns:
            List of ProductDTO
        """
        if not query or len(query.strip()) < 2:
            return []

        products = await self._product_repository.search(
            query=query.strip(),
            limit=limit,
            offset=offset,
        )

        return [self._to_dto(p) for p in products]

    def _to_dto(self, product: Product) -> ProductDTO:
        """
        Convert Product entity to DTO.

        Args:
            product: Product entity

        Returns:
            ProductDTO
        """
        return ProductDTO(
            id=str(product.id) if product.id else "",
            name=product.name,
            description=product.description,
            price=float(product.price.amount),
            currency=product.price.currency,
            category_id=str(product.category_id) if product.category_id else None,
            stock=product.stock,
            is_available=product.is_available(),
        )


class CategoryService:
    """
    Category application service.

    Handles category-related use cases.
    """

    def __init__(self, category_repository: ICategoryRepository) -> None:
        """
        Initialize category service.

        Args:
            category_repository: Category repository instance
        """
        self._category_repository = category_repository

    async def get_category(self, category_id: UUID) -> CategoryDTO:
        """
        Get category by ID.

        Args:
            category_id: Category UUID

        Returns:
            CategoryDTO

        Raises:
            CategoryNotFoundException: If category not found
        """
        category = await self._category_repository.get_by_id(category_id)

        if category is None:
            raise CategoryNotFoundException(str(category_id))

        return self._to_dto(category)

    async def list_categories(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CategoryDTO]:
        """
        List all categories.

        Args:
            limit: Maximum results
            offset: Results offset

        Returns:
            List of CategoryDTO
        """
        categories = await self._category_repository.get_all(
            limit=limit,
            offset=offset,
        )

        return [self._to_dto(c) for c in categories]

    async def get_category_tree(self) -> list[CategoryTreeDTO]:
        """
        Get category hierarchy tree.

        Returns:
            List of root CategoryTreeDTO with children
        """
        categories = await self._category_repository.get_tree()

        return [self._to_tree_dto(c) for c in categories]

    def _to_dto(self, category: Category) -> CategoryDTO:
        """
        Convert Category entity to DTO.

        Args:
            category: Category entity

        Returns:
            CategoryDTO
        """
        return CategoryDTO(
            id=str(category.id) if category.id else "",
            name=category.name,
            parent_id=str(category.parent_id) if category.parent_id else None,
        )

    def _to_tree_dto(self, category: Category) -> CategoryTreeDTO:
        """
        Convert Category entity to tree DTO.

        Args:
            category: Category entity

        Returns:
            CategoryTreeDTO with children
        """
        return CategoryTreeDTO(
            id=str(category.id) if category.id else "",
            name=category.name,
            parent_id=str(category.parent_id) if category.parent_id else None,
            children=[self._to_tree_dto(child) for child in category.children],
        )
