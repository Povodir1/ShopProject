"""
Repository interfaces for Catalog module.

Defines abstract contracts for data access.
Follows Dependency Inversion Principle (DIP) - high-level modules depend on abstractions.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from modules.catalog.domain.entities import Category, Product


class IProductRepository(ABC):
    """
    Product repository interface.

    Defines contract for product data access operations.
    """

    @abstractmethod
    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """
        Get product by ID.

        Args:
            product_id: Product UUID

        Returns:
            Product if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        category_id: Optional[UUID] = None,
    ) -> list[Product]:
        """
        Get all products with optional filtering.

        Args:
            limit: Maximum number of products to return
            offset: Number of products to skip
            category_id: Filter by category ID

        Returns:
            List of products
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Product]:
        """
        Search products by name or description.

        Args:
            query: Search query string
            limit: Maximum number of products to return
            offset: Number of products to skip

        Returns:
            List of matching products
        """
        pass

    @abstractmethod
    async def count(self, category_id: Optional[UUID] = None) -> int:
        """
        Count products with optional filtering.

        Args:
            category_id: Filter by category ID

        Returns:
            Number of products
        """
        pass


class ICategoryRepository(ABC):
    """
    Category repository interface.

    Defines contract for category data access operations.
    """

    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        """
        Get category by ID.

        Args:
            category_id: Category UUID

        Returns:
            Category if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Category]:
        """
        Get all categories.

        Args:
            limit: Maximum number of categories to return
            offset: Number of categories to skip

        Returns:
            List of categories
        """
        pass

    @abstractmethod
    async def get_tree(self) -> list[Category]:
        """
        Get category hierarchy tree.

        Returns:
            List of root categories with their children
        """
        pass

    @abstractmethod
    async def get_children(self, parent_id: UUID) -> list[Category]:
        """
        Get child categories for a parent.

        Args:
            parent_id: Parent category ID

        Returns:
            List of child categories
        """
        pass
