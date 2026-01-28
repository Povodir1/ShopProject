#!/usr/bin/env python3
"""
Database reset script.

Drops and recreates the database, then applies migrations.

WARNING: This will DELETE all data!
"""

import asyncio

from core.config import get_settings
from core.database import db_manager

settings = get_settings()


async def reset_database() -> None:
    """
    Reset database: drop, create, and run migrations.

    This will DELETE all existing data!
    """
    print("🗑️  Starting database reset...")
    print(f"   Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    print()

    # Step 1: Drop database
    print("📦 Step 1/3: Dropping database if exists...")
    await db_manager.drop_database()
    print("   ✅ Database dropped")
    print()

    # Step 2: Create database
    print("📦 Step 2/3: Creating new database...")
    await db_manager.create_database()
    print("   ✅ Database created")
    print()

    # Step 3: Run migrations
    print("📦 Step 3/3: Running migrations...")
    print("   ⚠️  Please run: alembic upgrade head")
    print()

    print("✅ Database reset complete!")
    print()
    print("Next steps:")
    print("  1. Run migrations: alembic upgrade head")
    print("  2. (Optional) Seed data: python scripts/seed_db.py")


async def main() -> None:
    """Main entry point."""
    try:
        await reset_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
