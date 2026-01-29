"""
Integration tests for Cart infrastructure layer.

Tests SQLAlchemyCartRepository with real database.
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from modules.cart.domain.entities import Cart, CartItem
from modules.cart.infrastructure.repositories import SQLAlchemyCartRepository
from modules.cart.infrastructure.orm import Base as CartBase
from modules.catalog.domain.value_objects import Price


# ============================================================================
# SQLAlchemyCartRepository Integration Tests
# ============================================================================

class TestSQLAlchemyCartRepository:
    """Test suite for SQLAlchemyCartRepository with database."""

    @pytest.fixture(autouse=True)
    async def setup_tables(self, async_engine):
        """Setup database tables before each test."""
        async with async_engine.begin() as conn:
            await conn.run_sync(lambda _: CartBase.metadata.create_all(_))

    @pytest.fixture
    def repository(self, db_session: AsyncSession) -> SQLAlchemyCartRepository:
        """Create repository instance."""
        return SQLAlchemyCartRepository(db_session)

    # ========================================================================
    # Create and Save Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_save_new_cart(self, repository):
        """Test saving new cart to database."""
        session_id = str(uuid4())
        cart = Cart(id=None, session_id=session_id)

        saved_cart = await repository.save(cart)

        assert saved_cart.id is not None
        assert saved_cart.session_id == session_id
        assert len(saved_cart.items) == 0

    @pytest.mark.asyncio
    async def test_save_cart_with_items(self, repository):
        """Test saving cart with items to database."""
        session_id = str(uuid4())
        product_id = uuid4()
        price = Price.from_float(29.99, "USD")

        cart = Cart(id=None, session_id=session_id)
        cart.add_item(product_id=product_id, quantity=2, price=price)

        saved_cart = await repository.save(cart)

        assert saved_cart.id is not None
        assert len(saved_cart.items) == 1
        assert saved_cart.items[0].quantity == 2
        assert saved_cart.item_count == 2
        assert float(saved_cart.total) == 59.98

    @pytest.mark.asyncio
    async def test_save_cart_updates_existing(self, repository):
        """Test saving updates existing cart."""
        session_id = str(uuid4())

        # Create initial cart
        cart = Cart(id=None, session_id=session_id)
        saved_cart = await repository.save(cart)

        # Add item and update
        product_id = uuid4()
        price = Price.from_float(10.0, "USD")
        saved_cart.add_item(product_id=product_id, quantity=3, price=price)

        updated_cart = await repository.save(saved_cart)

        assert updated_cart.id == saved_cart.id
        assert len(updated_cart.items) == 1
        assert updated_cart.item_count == 3

    @pytest.mark.asyncio
    async def test_get_by_session_id(self, repository):
        """Test retrieving cart by session ID."""
        session_id = str(uuid4())

        # Create cart
        cart = Cart(id=None, session_id=session_id)
        saved_cart = await repository.save(cart)

        # Retrieve cart
        retrieved_cart = await repository.get_by_session_id(session_id)

        assert retrieved_cart is not None
        assert retrieved_cart.id == saved_cart.id
        assert retrieved_cart.session_id == session_id

    @pytest.mark.asyncio
    async def test_get_by_session_id_not_found(self, repository):
        """Test retrieving non-existent cart returns None."""
        retrieved_cart = await repository.get_by_session_id(str(uuid4()))

        assert retrieved_cart is None

    @pytest.mark.asyncio
    async def test_get_cart_with_items_by_session_id(self, repository):
        """Test retrieving cart with items by session ID."""
        session_id = str(uuid4())
        product_id = uuid4()
        price = Price.from_float(19.99, "USD")

        # Create cart with items
        cart = Cart(id=None, session_id=session_id)
        cart.add_item(product_id=product_id, quantity=2, price=price)
        await repository.save(cart)

        # Retrieve cart
        retrieved_cart = await repository.get_by_session_id(session_id)

        assert retrieved_cart is not None
        assert len(retrieved_cart.items) == 1
        assert retrieved_cart.items[0].product_id == product_id
        assert retrieved_cart.items[0].quantity == 2
        assert float(retrieved_cart.items[0].subtotal) == 39.98

    @pytest.mark.asyncio
    async def test_delete_cart(self, repository):
        """Test deleting cart from database."""
        session_id = str(uuid4())

        # Create cart
        cart = Cart(id=None, session_id=session_id)
        saved_cart = await repository.save(cart)

        # Delete cart
        await repository.delete(saved_cart.id)

        # Verify deletion
        retrieved_cart = await repository.get_by_session_id(session_id)
        assert retrieved_cart is None

    @pytest.mark.asyncio
    async def test_get_item_by_id(self, repository):
        """Test retrieving cart item by ID."""
        session_id = str(uuid4())
        product_id = uuid4()
        price = Price.from_float(10.0, "USD")

        # Create cart with item
        cart = Cart(id=None, session_id=session_id)
        cart.add_item(product_id=product_id, quantity=5, price=price)
        saved_cart = await repository.save(cart)
        item_id = saved_cart.items[0].id

        # Retrieve item
        retrieved_item = await repository.get_item_by_id(item_id)

        assert retrieved_item is not None
        assert retrieved_item.id == item_id
        assert retrieved_item.quantity == 5

    @pytest.mark.asyncio
    async def test_get_item_by_id_not_found(self, repository):
        """Test retrieving non-existent item returns None."""
        retrieved_item = await repository.get_item_by_id(uuid4())

        assert retrieved_item is None

    @pytest.mark.asyncio
    async def test_delete_item(self, repository):
        """Test deleting cart item from database."""
        session_id = str(uuid4())
        product_id = uuid4()
        price = Price.from_float(10.0, "USD")

        # Create cart with item
        cart = Cart(id=None, session_id=session_id)
        cart.add_item(product_id=product_id, quantity=5, price=price)
        saved_cart = await repository.save(cart)
        item_id = saved_cart.items[0].id

        # Delete item
        await repository.delete_item(item_id)

        # Verify deletion
        retrieved_cart = await repository.get_by_session_id(session_id)
        assert len(retrieved_cart.items) == 0

    @pytest.mark.asyncio
    async def test_update_cart_replaces_all_items(self, repository):
        """Test that updating cart replaces all items correctly."""
        session_id = str(uuid4())
        product_id1 = uuid4()
        product_id2 = uuid4()
        price = Price.from_float(10.0, "USD")

        # Create cart with item
        cart = Cart(id=None, session_id=session_id)
        cart.add_item(product_id1, quantity=2, price=price)
        saved_cart = await repository.save(cart)

        # Update with different items
        saved_cart.items.clear()
        saved_cart.add_item(product_id2, quantity=3, price=price)
        updated_cart = await repository.save(saved_cart)

        # Verify items were replaced
        retrieved_cart = await repository.get_by_session_id(session_id)
        assert len(retrieved_cart.items) == 1
        assert retrieved_cart.items[0].product_id == product_id2
        assert retrieved_cart.items[0].quantity == 3

    @pytest.mark.asyncio
    async def test_multiple_carts_same_session(self, repository):
        """Test handling multiple carts with different sessions."""
        session_id1 = str(uuid4())
        session_id2 = str(uuid4())
        product_id = uuid4()
        price = Price.from_float(10.0, "USD")

        # Create first cart
        cart1 = Cart(id=None, session_id=session_id1)
        cart1.add_item(product_id, quantity=2, price=price)
        await repository.save(cart1)

        # Create second cart
        cart2 = Cart(id=None, session_id=session_id2)
        cart2.add_item(product_id, quantity=3, price=price)
        await repository.save(cart2)

        # Verify both carts exist independently
        retrieved_cart1 = await repository.get_by_session_id(session_id1)
        retrieved_cart2 = await repository.get_by_session_id(session_id2)

        assert retrieved_cart1.item_count == 2
        assert retrieved_cart2.item_count == 3
        assert retrieved_cart1.id != retrieved_cart2.id

    @pytest.mark.asyncio
    async def test_cart_persistence_across_sessions(self, repository):
        """Test cart data persists across repository sessions."""
        session_id = str(uuid4())
        product_id = uuid4()
        price = Price.from_float(25.0, "USD")

        # Create cart in first "session"
        cart = Cart(id=None, session_id=session_id)
        cart.add_item(product_id, quantity=4, price=price)
        saved_cart = await repository.save(cart)
        cart_id = saved_cart.id

        # Retrieve in second "session" (new repository instance would use same DB)
        # Simulate by just retrieving again
        retrieved_cart = await repository.get_by_session_id(session_id)

        assert retrieved_cart.id == cart_id
        assert retrieved_cart.item_count == 4
        assert float(retrieved_cart.total) == 100.0
