"""
SQLAlchemy repository implementations for Catalog module.

Implements repository interfaces using SQLAlchemy.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.catalog.domain.entities import Category, Product
from modules.catalog.domain.repositories import ICategoryRepository, IProductRepository
from modules.catalog.domain.value_objects import Price
from modules.catalog.infrastructure.orm import CategoryORM, ProductORM


class SQLAlchemyProductRepository(IProductRepository):
    """
    SQLAlchemy implementation of product repository.

    Implements IProductRepository using async SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """
        Get product by ID.

        Args:
            product_id: Product UUID

        Returns:
            Product if found, None otherwise
        """
        result = await self._session.execute(
            select(ProductORM).where(ProductORM.id == str(product_id))
        )
        orm_product = result.scalar_one_or_none()

        if orm_product is None:
            return None

        return self._to_entity(orm_product)

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        category_id: Optional[UUID] = None,
        search_query: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        in_stock: bool = False,
        order_by: str = "created_at",
        order_dir: str = "desc",
    ) -> list[Product]:
        """
        Get all products with optional filtering and sorting.

        Args:
            limit: Maximum number of products to return
            offset: Number of products to skip
            category_id: Filter by category ID
            search_query: Search by name or description
            price_min: Minimum price filter
            price_max: Maximum price filter
            in_stock: Only show in-stock items
            order_by: Sort field
            order_dir: Sort direction

        Returns:
            List of products
        """
        query = select(ProductORM)

        # Apply filters
        if category_id is not None:
            query = query.where(ProductORM.category_id == str(category_id))

        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.where(
                or_(
                    ProductORM.name.ilike(search_pattern),
                    ProductORM.description.ilike(search_pattern),
                )
            )

        if price_min is not None:
            # Price is stored as integer (cents)
            min_cents = int(price_min * 100)
            query = query.where(ProductORM.price >= min_cents)

        if price_max is not None:
            # Price is stored as integer (cents)
            max_cents = int(price_max * 100)
            query = query.where(ProductORM.price <= max_cents)

        if in_stock:
            query = query.where(ProductORM.stock > 0)

        # Apply sorting
        order_column = self._get_order_column(order_by)
        if order_dir == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Apply pagination
        query = query.limit(limit).offset(offset)

        result = await self._session.execute(query)
        orm_products = result.scalars().all()

        return [self._to_entity(p) for p in orm_products]

    def _get_order_column(self, order_by: str):
        """Get SQLAlchemy column for sorting."""
        if order_by == "name":
            return ProductORM.name
        elif order_by == "price":
            return ProductORM.price
        else:  # created_at
            return ProductORM.created_at

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
        search_pattern = f"%{query}%"

        q = (
            select(ProductORM)
            .where(
                (ProductORM.name.ilike(search_pattern))
                | (ProductORM.description.ilike(search_pattern))
            )
            .order_by(ProductORM.name)
            .limit(limit)
            .offset(offset)
        )

        result = await self._session.execute(q)
        orm_products = result.scalars().all()

        return [self._to_entity(p) for p in orm_products]

    async def count(
        self,
        category_id: Optional[UUID] = None,
        search_query: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        in_stock: bool = False,
    ) -> int:
        """
        Count products with optional filtering.

        Args:
            category_id: Filter by category ID
            search_query: Search by name or description
            price_min: Minimum price filter
            price_max: Maximum price filter
            in_stock: Only count in-stock items

        Returns:
            Number of products
        """
        query = select(func.count(ProductORM.id))

        # Apply filters (same as get_all)
        if category_id is not None:
            query = query.where(ProductORM.category_id == str(category_id))

        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.where(
                or_(
                    ProductORM.name.ilike(search_pattern),
                    ProductORM.description.ilike(search_pattern),
                )
            )

        if price_min is not None:
            min_cents = int(price_min * 100)
            query = query.where(ProductORM.price >= min_cents)

        if price_max is not None:
            max_cents = int(price_max * 100)
            query = query.where(ProductORM.price <= max_cents)

        if in_stock:
            query = query.where(ProductORM.stock > 0)

        result = await self._session.execute(query)
        return result.scalar() or 0

    def _to_entity(self, orm_product: ProductORM) -> Product:
        """
        Convert ORM model to domain entity.

        Args:
            orm_product: ProductORM instance

        Returns:
            Product domain entity
        """
        return Product(
            id=UUID(orm_product.id) if orm_product.id else None,
            name=orm_product.name,
            description=orm_product.description,
            price=Price.from_int(orm_product.price, orm_product.currency),
            category_id=UUID(orm_product.category_id) if orm_product.category_id else None,
            stock=orm_product.stock,
            created_at=orm_product.created_at,
            updated_at=orm_product.updated_at,
        )


class SQLAlchemyCategoryRepository(ICategoryRepository):
    """
    SQLAlchemy implementation of category repository.

    Implements ICategoryRepository using async SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        """
        Get category by ID.

        Args:
            category_id: Category UUID

        Returns:
            Category if found, None otherwise
        """
        result = await self._session.execute(
            select(CategoryORM)
            .options(selectinload(CategoryORM.children))
            .where(CategoryORM.id == str(category_id))
        )
        orm_category = result.scalar_one_or_none()

        if orm_category is None:
            return None

        return self._to_entity(orm_category)

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
        result = await self._session.execute(
            select(CategoryORM)
            .order_by(CategoryORM.name)
            .limit(limit)
            .offset(offset)
        )
        orm_categories = result.scalars().all()

        return [self._to_entity(c) for c in orm_categories]

    async def get_tree(self) -> list[Category]:
        """
        Get category hierarchy tree.

        Returns:
            List of root categories with their children
        """
        result = await self._session.execute(
            select(CategoryORM)
            .options(selectinload(CategoryORM.children))
            .where(CategoryORM.parent_id.is_(None))
            .order_by(CategoryORM.name)
        )
        orm_categories = result.scalars().all()

        return [self._to_entity(c, load_children=True) for c in orm_categories]

    async def get_children(self, parent_id: UUID) -> list[Category]:
        """
        Get child categories for a parent.

        Args:
            parent_id: Parent category ID

        Returns:
            List of child categories
        """
        result = await self._session.execute(
            select(CategoryORM)
            .where(CategoryORM.parent_id == str(parent_id))
            .order_by(CategoryORM.name)
        )
        orm_categories = result.scalars().all()

        return [self._to_entity(c) for c in orm_categories]

    def _to_entity(self, orm_category: CategoryORM, load_children: bool = False) -> Category:
        """
        Convert ORM model to domain entity.

        Args:
            orm_category: CategoryORM instance
            load_children: Whether to load children recursively

        Returns:
            Category domain entity
        """
        children = []
        if load_children and orm_category.children:
            for child in orm_category.children:
                children.append(self._to_entity(child, load_children=True))

        return Category(
            id=UUID(orm_category.id) if orm_category.id else None,
            name=orm_category.name,
            parent_id=UUID(orm_category.parent_id) if orm_category.parent_id else None,
            children=children,
            created_at=orm_category.created_at,
            updated_at=orm_category.updated_at,
        )
