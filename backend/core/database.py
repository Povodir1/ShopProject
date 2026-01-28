"""
Database configuration and session management.

Provides async engine, session factory, and database utilities.
"""

from collections.abc import AsyncGenerator
from typing import Optional

import asyncpg
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class DatabaseManager:
    """
    Manages database connections and sessions.

    Implements Singleton pattern for engine and session maker.
    """

    def __init__(self) -> None:
        """Initialize database manager (lazy initialization)."""
        self._engine: Optional[AsyncEngine] = None
        self._session_maker: Optional[async_sessionmaker[AsyncSession]] = None

    @property
    def engine(self) -> AsyncEngine:
        """Get or create async engine."""
        if self._engine is None:
            self._engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DEBUG,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )
        return self._engine

    @property
    def session_maker(self) -> async_sessionmaker[AsyncSession]:
        """Get or create session maker."""
        if self._session_maker is None:
            self._session_maker = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
        return self._session_maker

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get async database session.

        Yields:
            AsyncSession: Database session

        Example:
            async with db_manager.get_session() as session:
                await session.execute(query)
        """
        async with self.session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def create_database(self) -> None:
        """
        Create database if it doesn't exist.

        Raises:
            asyncpg.PostgresError: If database creation fails
        """
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database="postgres",  # Connect to default database
        )

        try:
            # Check if database exists
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = $1)",
                settings.DB_NAME,
            )

            if not exists:
                await conn.execute(f'CREATE DATABASE "{settings.DB_NAME}"')
        finally:
            await conn.close()

    async def drop_database(self) -> None:
        """
        Drop database if it exists.

        WARNING: This will delete all data!

        Raises:
            asyncpg.PostgresError: If database drop fails
        """
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database="postgres",
        )

        try:
            # Terminate all connections to the database
            await conn.execute(
                f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{settings.DB_NAME}'
                AND pid <> pg_backend_pid()
            """
            )

            # Drop database
            await conn.execute(f'DROP DATABASE IF EXISTS "{settings.DB_NAME}"')
        finally:
            await conn.close()

    async def init_models(self) -> None:
        """Create all tables (use only for development/testing)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        """Close database connections."""
        if self._engine is not None:
            await self._engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session.

    Yields:
        AsyncSession: Database session

    Example:
        @app.get("/products")
        async def get_products(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Product))
            return result.scalars().all()
    """
    async for session in db_manager.get_session():
        yield session
