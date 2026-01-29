"""
Unit tests for Catalog application services.

Tests ProductService and CategoryService with mocked dependencies.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock

from modules.catalog.application.services import ProductService, CategoryService
from modules.catalog.application.dto import ProductFilterDTO, ProductListDTO
from modules.catalog.domain.entities import Product, Category
from modules.catalog.domain.exceptions import ProductNotFoundException, CategoryNotFoundException
from modules.catalog.domain.value_objects import Price
from modules.catalog.tests.fixtures import create_test_product


# ============================================================================
# ProductService Unit Tests
# ============================================================================

class TestProductService:
    """Test suite for ProductService."""

    @pytest.mark.asyncio
    async def test_get_product_success(self, mock_product_repository):
        """Test successfully getting product by ID."""
        product_id = uuid4()
        product = create_test_product(
            name="Laptop",
            description="High-performance laptop",
            price=999.99,
            stock=50,
        )
        product.id = product_id

        mock_product_repository.get_by_id.return_value = product

        service = ProductService(mock_product_repository)
        product_dto = await service.get_product(product_id)

        mock_product_repository.get_by_id.assert_called_once_with(product_id)
        assert product_dto.id == str(product_id)
        assert product_dto.name == "Laptop"
        assert product_dto.price == 999.99

    @pytest.mark.asyncio
    async def test_get_product_not_found_raises_error(self, mock_product_repository):
        """Test getting non-existent product raises error."""
        product_id = uuid4()

        mock_product_repository.get_by_id.return_value = None

        service = ProductService(mock_product_repository)

        with pytest.raises(ProductNotFoundException):
            await service.get_product(product_id)

    @pytest.mark.asyncio
    async def test_list_products_with_filters(self, mock_product_repository):
        """Test listing products with filters."""
        # Create mock products
        products = [
            create_test_product(name=f"Product {i}", price=10.0 * (i + 1), stock=10 * (i + 1))
            for i in range(3)
        ]
        for i, p in enumerate(products):
            p.id = uuid4()

        mock_product_repository.get_all.return_value = products
        mock_product_repository.count.return_value = 3

        filters = ProductFilterDTO(
            price_min=10.0,
            price_max=50.0,
            in_stock=True,
            limit=10,
            offset=0,
        )

        service = ProductService(mock_product_repository)
        result = await service.list_products(filters)

        assert len(result.items) == 3
        assert result.total == 3
        assert result.limit == 10
        assert result.offset == 0
        mock_product_repository.get_all.assert_called_once()
        mock_product_repository.count.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_products_valid_query(self, mock_product_repository):
        """Test searching products with valid query."""
        products = [
            create_test_product(name="Laptop", price=999.99, stock=5),
            create_test_product(name="Laptop Case", price=29.99, stock=20),
        ]
        for p in products:
            p.id = uuid4()

        mock_product_repository.search.return_value = products

        service = ProductService(mock_product_repository)
        result = await service.search_products("laptop", limit=10, offset=0)

        assert len(result) == 2
        mock_product_repository.search.assert_called_once_with(query="laptop", limit=10, offset=0)

    @pytest.mark.asyncio
    async def test_search_products_short_query_returns_empty(self, mock_product_repository):
        """Test searching with short query returns empty list."""
        service = ProductService(mock_product_repository)
        result = await service.search_products("a", limit=10, offset=0)

        assert result == []
        mock_product_repository.search.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_products_empty_query_returns_empty(self, mock_product_repository):
        """Test searching with empty query returns empty list."""
        service = ProductService(mock_product_repository)
        result = await service.search_products("", limit=10, offset=0)

        assert result == []
        mock_product_repository.search.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_products_whitespace_query_returns_empty(self, mock_product_repository):
        """Test searching with whitespace query returns empty list."""
        service = ProductService(mock_product_repository)
        result = await service.search_products("   ", limit=10, offset=0)

        assert result == []
        mock_product_repository.search.assert_not_called()

    @pytest.mark.asyncio
    async def test_to_dto_conversion(self, mock_product_repository):
        """Test Product to DTO conversion."""
        product_id = uuid4()
        category_id = uuid4()

        product = Product(
            id=product_id,
            name="Test Laptop",
            description="Test description",
            price=Price.from_float(999.99, "USD"),
            category_id=category_id,
            stock=50,
        )

        mock_product_repository.get_by_id.return_value = product

        service = ProductService(mock_product_repository)
        product_dto = await service.get_product(product_id)

        assert product_dto.id == str(product_id)
        assert product_dto.name == "Test Laptop"
        assert product_dto.description == "Test description"
        assert product_dto.price == 999.99
        assert product_dto.currency == "USD"
        assert product_dto.category_id == str(category_id)
        assert product_dto.stock == 50
        assert product_dto.is_available is True

    @pytest.mark.asyncio
    async def test_to_dto_out_of_stock_product(self, mock_product_repository):
        """Test DTO conversion for out of stock product."""
        product_id = uuid4()

        product = create_test_product(stock=0)
        product.id = product_id

        mock_product_repository.get_by_id.return_value = product

        service = ProductService(mock_product_repository)
        product_dto = await service.get_product(product_id)

        assert product_dto.stock == 0
        assert product_dto.is_available is False


# ============================================================================
# CategoryService Unit Tests
# ============================================================================

class TestCategoryService:
    """Test suite for CategoryService."""

    @pytest.mark.asyncio
    async def test_get_category_success(self, mock_category_repository):
        """Test successfully getting category by ID."""
        category_id = uuid4()
        category = Category(id=category_id, name="Electronics")

        mock_category_repository.get_by_id.return_value = category

        service = CategoryService(mock_category_repository)
        category_dto = await service.get_category(category_id)

        mock_category_repository.get_by_id.assert_called_once_with(category_id)
        assert category_dto.id == str(category_id)
        assert category_dto.name == "Electronics"

    @pytest.mark.asyncio
    async def test_get_category_not_found_raises_error(self, mock_category_repository):
        """Test getting non-existent category raises error."""
        category_id = uuid4()

        mock_category_repository.get_by_id.return_value = None

        service = CategoryService(mock_category_repository)

        with pytest.raises(CategoryNotFoundException):
            await service.get_category(category_id)

    @pytest.mark.asyncio
    async def test_list_categories(self, mock_category_repository):
        """Test listing all categories."""
        categories = [
            Category(id=uuid4(), name="Electronics"),
            Category(id=uuid4(), name="Clothing"),
            Category(id=uuid4(), name="Books"),
        ]

        mock_category_repository.get_all.return_value = categories

        service = CategoryService(mock_category_repository)
        result = await service.list_categories(limit=10, offset=0)

        assert len(result) == 3
        assert result[0].name == "Electronics"
        assert result[1].name == "Clothing"
        assert result[2].name == "Books"
        mock_category_repository.get_all.assert_called_once_with(limit=10, offset=0)

    @pytest.mark.asyncio
    async def test_get_category_tree(self, mock_category_repository):
        """Test getting category hierarchy tree."""
        # Create category tree: Electronics -> Laptops, Phones
        electronics = Category(id=uuid4(), name="Electronics")
        laptops = Category(id=uuid4(), name="Laptops", parent_id=electronics.id)
        phones = Category(id=uuid4(), name="Phones", parent_id=electronics.id)

        electronics.add_child(laptops)
        electronics.add_child(phones)

        mock_category_repository.get_tree.return_value = [electronics]

        service = CategoryService(mock_category_repository)
        result = await service.get_category_tree()

        assert len(result) == 1
        assert result[0].name == "Electronics"
        assert len(result[0].children) == 2
        assert result[0].children[0].name == "Laptops"
        assert result[0].children[1].name == "Phones"

    @pytest.mark.asyncio
    async def test_to_dto_conversion(self, mock_category_repository):
        """Test Category to DTO conversion."""
        category_id = uuid4()
        parent_id = uuid4()

        category = Category(id=category_id, name="Laptops", parent_id=parent_id)

        mock_category_repository.get_by_id.return_value = category

        service = CategoryService(mock_category_repository)
        category_dto = await service.get_category(category_id)

        assert category_dto.id == str(category_id)
        assert category_dto.name == "Laptops"
        assert category_dto.parent_id == str(parent_id)

    @pytest.mark.asyncio
    async def test_to_tree_dto_conversion(self, mock_category_repository):
        """Test Category to tree DTO conversion with children."""
        parent_id = uuid4()
        child_id = uuid4()

        parent = Category(id=parent_id, name="Electronics")
        child = Category(id=child_id, name="Laptops", parent_id=parent_id)

        parent.add_child(child)

        mock_category_repository.get_tree.return_value = [parent]

        service = CategoryService(mock_category_repository)
        result = await service.get_category_tree()

        assert result[0].id == str(parent_id)
        assert result[0].name == "Electronics"
        assert len(result[0].children) == 1
        assert result[0].children[0].id == str(child_id)
        assert result[0].children[0].name == "Laptops"
        assert result[0].children[0].parent_id == str(parent_id)
