"""
Shared pytest fixtures for all backend tests.

Provides common fixtures for async database testing.
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker


# Test database URL (SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# ============================================================================
# Event Loop Fixture
# ============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Engine Fixtures
# ============================================================================

@pytest.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create async engine for testing.

    Creates all tables before tests and drops them after.
    """
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    # Create tables
    from modules.cart.infrastructure.orm import Base as CartBase
    from modules.catalog.infrastructure.orm import Base as CatalogBase

    async with engine.begin() as conn:
        await conn.run_sync(lambda _: CartBase.metadata.create_all(_))
        await conn.run_sync(lambda _: CatalogBase.metadata.create_all(_))

    yield engine

    # Cleanup
    await engine.dispose()


# ============================================================================
# Database Session Fixtures
# ============================================================================

@pytest.fixture
async def db_session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create async database session for testing.

    Each test gets a fresh session that's rolled back after the test.
    """
    async_session_maker = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def db_session_commit(db_session: AsyncSession) -> AsyncSession:
    """
    Create database session that commits instead of rolling back.

    Useful for tests that need to verify data persistence.
    Most tests should use db_session instead.
    """
    yield db_session
    await db_session.commit()
