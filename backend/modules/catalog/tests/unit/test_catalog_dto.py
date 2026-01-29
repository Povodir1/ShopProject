"""
Unit tests for Catalog DTOs.

Tests data transfer objects for validation and serialization.
"""

import pytest
from uuid import uuid4

from modules.catalog.application.dto import (
    ProductDTO,
    ProductListDTO,
    CategoryDTO,
    CategoryTreeDTO,
    ProductFilterDTO,
)


# ============================================================================
# ProductDTO Tests
# ============================================================================

class TestProductDTO:
    """Test suite for ProductDTO."""

    def test_create_product_dto(self):
        """Test creating product DTO."""
        product_id = str(uuid4())
        category_id = str(uuid4())

        dto = ProductDTO(
            id=product_id,
            name="Laptop",
            description="High-performance laptop",
            price=999.99,
            currency="USD",
            category_id=category_id,
            stock=50,
            is_available=True,
        )

        assert dto.id == product_id
        assert dto.name == "Laptop"
        assert dto.price == 999.99
        assert dto.currency == "USD"
        assert dto.stock == 50
        assert dto.is_available is True


# ============================================================================
# ProductListDTO Tests
# ============================================================================

class TestProductListDTO:
    """Test suite for ProductListDTO."""

    def test_create_product_list_dto(self):
        """Test creating product list DTO."""
        items = [
            ProductDTO(
                id=str(uuid4()),
                name=f"Product {i}",
                description=f"Description {i}",
                price=10.0 * (i + 1),
                currency="USD",
                category_id=str(uuid4()),
                stock=10 * (i + 1),
                is_available=True,
            )
            for i in range(3)
        ]

        dto = ProductListDTO(
            items=items,
            total=100,
            limit=10,
            offset=0,
        )

        assert len(dto.items) == 3
        assert dto.total == 100
        assert dto.limit == 10
        assert dto.offset == 0


# ============================================================================
# CategoryDTO Tests
# ============================================================================

class TestCategoryDTO:
    """Test suite for CategoryDTO."""

    def test_create_category_dto(self):
        """Test creating category DTO."""
        category_id = str(uuid4())
        parent_id = str(uuid4())

        dto = CategoryDTO(
            id=category_id,
            name="Electronics",
            parent_id=parent_id,
        )

        assert dto.id == category_id
        assert dto.name == "Electronics"
        assert dto.parent_id == parent_id

    def test_create_category_dto_without_parent(self):
        """Test creating category DTO without parent."""
        category_id = str(uuid4())

        dto = CategoryDTO(
            id=category_id,
            name="Electronics",
            parent_id=None,
        )

        assert dto.id == category_id
        assert dto.name == "Electronics"
        assert dto.parent_id is None


# ============================================================================
# CategoryTreeDTO Tests
# ============================================================================

class TestCategoryTreeDTO:
    """Test suite for CategoryTreeDTO."""

    def test_create_category_tree_dto(self):
        """Test creating category tree DTO with children."""
        parent_id = str(uuid4())
        child_id1 = str(uuid4())
        child_id2 = str(uuid4())

        children = [
            CategoryTreeDTO(
                id=child_id1,
                name="Laptops",
                parent_id=parent_id,
                children=[],
            ),
            CategoryTreeDTO(
                id=child_id2,
                name="Phones",
                parent_id=parent_id,
                children=[],
            ),
        ]

        dto = CategoryTreeDTO(
            id=parent_id,
            name="Electronics",
            parent_id=None,
            children=children,
        )

        assert dto.id == parent_id
        assert dto.name == "Electronics"
        assert len(dto.children) == 2
        assert dto.children[0].name == "Laptops"
        assert dto.children[1].name == "Phones"

    def test_create_nested_category_tree(self):
        """Test creating nested category tree."""
        root_id = str(uuid4())
        child_id = str(uuid4())
        grandchild_id = str(uuid4())

        grandchild = CategoryTreeDTO(
            id=grandchild_id,
            name="Gaming Laptops",
            parent_id=child_id,
            children=[],
        )

        child = CategoryTreeDTO(
            id=child_id,
            name="Laptops",
            parent_id=root_id,
            children=[grandchild],
        )

        root = CategoryTreeDTO(
            id=root_id,
            name="Electronics",
            parent_id=None,
            children=[child],
        )

        assert root.children[0].name == "Laptops"
        assert root.children[0].children[0].name == "Gaming Laptops"


# ============================================================================
# ProductFilterDTO Tests
# ============================================================================

class TestProductFilterDTO:
    """Test suite for ProductFilterDTO."""

    def test_create_default_filter(self):
        """Test creating filter with default values."""
        dto = ProductFilterDTO()

        assert dto.category_id is None
        assert dto.search_query is None
        assert dto.price_min is None
        assert dto.price_max is None
        assert dto.in_stock is False
        assert dto.order_by == "created_at"
        assert dto.order_dir == "desc"
        assert dto.limit == 100
        assert dto.offset == 0

    def test_create_filter_with_all_parameters(self):
        """Test creating filter with all parameters."""
        category_id = uuid4()

        dto = ProductFilterDTO(
            category_id=category_id,
            search_query="laptop",
            price_min=100.0,
            price_max=1000.0,
            in_stock=True,
            order_by="price",
            order_dir="asc",
            limit=20,
            offset=40,
        )

        assert dto.category_id == category_id
        assert dto.search_query == "laptop"
        assert dto.price_min == 100.0
        assert dto.price_max == 1000.0
        assert dto.in_stock is True
        assert dto.order_by == "price"
        assert dto.order_dir == "asc"
        assert dto.limit == 20
        assert dto.offset == 40

    def test_validate_limit_too_low_gets_default(self):
        """Test limit below minimum gets set to default."""
        dto = ProductFilterDTO(limit=0)

        assert dto.limit == 100

    def test_validate_limit_negative_gets_default(self):
        """Test negative limit gets set to default."""
        dto = ProductFilterDTO(limit=-10)

        assert dto.limit == 100

    def test_validate_limit_too_high_gets_capped(self):
        """Test limit above maximum gets capped."""
        dto = ProductFilterDTO(limit=2000)

        assert dto.limit == 1000

    def test_validate_offset_negative_gets_zero(self):
        """Test negative offset gets set to zero."""
        dto = ProductFilterDTO(offset=-10)

        assert dto.offset == 0

    def test_validate_invalid_order_by_gets_default(self):
        """Test invalid order_by gets set to default."""
        dto = ProductFilterDTO(order_by="invalid_field")

        assert dto.order_by == "created_at"

    def test_validate_valid_order_by_fields(self):
        """Test valid order_by fields are accepted."""
        for field in ["name", "price", "created_at"]:
            dto = ProductFilterDTO(order_by=field)
            assert dto.order_by == field

    def test_validate_invalid_order_dir_gets_default(self):
        """Test invalid order_dir gets set to default."""
        dto = ProductFilterDTO(order_dir="invalid")

        assert dto.order_dir == "desc"

    def test_validate_valid_order_dir_values(self):
        """Test valid order_dir values are accepted."""
        for direction in ["asc", "desc"]:
            dto = ProductFilterDTO(order_dir=direction)
            assert dto.order_dir == direction

    def test_validate_negative_price_min_gets_none(self):
        """Test negative price_min gets set to None."""
        dto = ProductFilterDTO(price_min=-10.0)

        assert dto.price_min is None

    def test_validate_negative_price_max_gets_none(self):
        """Test negative price_max gets set to None."""
        dto = ProductFilterDTO(price_max=-10.0)

        assert dto.price_max is None

    def test_validate_swapped_price_range_gets_corrected(self):
        """Test price range with min > max gets swapped."""
        dto = ProductFilterDTO(price_min=1000.0, price_max=100.0)

        assert dto.price_min == 100.0
        assert dto.price_max == 1000.0

    def test_validate_equal_price_range_unchanged(self):
        """Test equal price range remains unchanged."""
        dto = ProductFilterDTO(price_min=100.0, price_max=100.0)

        assert dto.price_min == 100.0
        assert dto.price_max == 100.0

    def test_validate_partial_price_range_unchanged(self):
        """Test partial price range (only min or only max) remains unchanged."""
        dto1 = ProductFilterDTO(price_min=100.0)
        assert dto1.price_min == 100.0
        assert dto1.price_max is None

        dto2 = ProductFilterDTO(price_max=500.0)
        assert dto2.price_min is None
        assert dto2.price_max == 500.0
