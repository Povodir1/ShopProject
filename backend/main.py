"""
Application entry point.

Initializes database and starts the FastAPI server.
"""

import asyncio
import subprocess

import uvicorn

from core.app import app
from core.config import get_settings
from core.database import db_manager

settings = get_settings()


async def init_database() -> None:
    """
    Initialize database: drop, create, and run migrations.

    This will DELETE all existing data!
    """
    print("🗑️  Dropping database if exists...")
    await db_manager.drop_database()

    print("📦 Creating new database...")
    await db_manager.create_database()

    print("📋 Running migrations...")
    # Run alembic migrations
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("   ✅ Migrations applied successfully")
    else:
        print(f"   ⚠️  Migration warning: {result.stderr}")

    print("✅ Database initialized successfully")


async def main() -> None:
    """Main application entry point."""
    # Initialize database (drop and recreate)
    await init_database()

    # Start server
    config = uvicorn.Config(
        app=app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
