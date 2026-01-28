#!/usr/bin/env python3
"""
Database seeding script.

Populates the database with sample categories and products.
"""

import asyncio
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.database import db_manager
from modules.catalog.domain.entities import Category, Product
from modules.catalog.domain.value_objects import Price
from modules.catalog.infrastructure.orm import CategoryORM, ProductORM
from sqlalchemy import select

settings = get_settings()


# Sample data
CATEGORIES = [
    {"name": "Electronics", "parent_id": None},
    {"name": "Phones", "parent_id": None},
    {"name": "Laptops", "parent_id": None},
    {"name": "Accessories", "parent_id": None},
    {"name": "Clothing", "parent_id": None},
    {"name": "Men", "parent_id": None},
    {"name": "Women", "parent_id": None},
    {"name": "Kids", "parent_id": None},
    {"name": "Food", "parent_id": None},
    {"name": "Beverages", "parent_id": None},
    {"name": "Snacks", "parent_id": None},
]

PRODUCTS = [
    # Electronics - Phones
    {
        "name": "iPhone 15 Pro",
        "description": "Latest iPhone with A17 Pro chip, titanium design, and advanced camera system.",
        "price": 1199.00,
        "stock": 50,
        "category_name": "Phones",
    },
    {
        "name": "Samsung Galaxy S24 Ultra",
        "description": "Premium Android smartphone with S Pen, 200MP camera, and AI features.",
        "price": 1299.00,
        "stock": 45,
        "category_name": "Phones",
    },
    {
        "name": "Google Pixel 8 Pro",
        "description": "Pure Android experience with advanced AI photography and 7 years of updates.",
        "price": 999.00,
        "stock": 60,
        "category_name": "Phones",
    },
    # Electronics - Laptops
    {
        "name": "MacBook Pro 16\"",
        "description": "Powerful laptop with M3 Max chip, stunning Liquid Retina XDR display.",
        "price": 2499.00,
        "stock": 30,
        "category_name": "Laptops",
    },
    {
        "name": "Dell XPS 15",
        "description": "Windows laptop with InfinityEdge display and powerful performance.",
        "price": 1899.00,
        "stock": 40,
        "category_name": "Laptops",
    },
    {
        "name": "ThinkPad X1 Carbon",
        "description": "Business laptop with legendary keyboard, lightweight, durable design.",
        "price": 1649.00,
        "stock": 35,
        "category_name": "Laptops",
    },
    # Electronics - Accessories
    {
        "name": "AirPods Pro 2",
        "description": "Premium wireless earbuds with active noise cancellation and spatial audio.",
        "price": 249.00,
        "stock": 100,
        "category_name": "Accessories",
    },
    {
        "name": "Sony WH-1000XM5",
        "description": "Best-in-class noise canceling headphones with exceptional sound quality.",
        "price": 399.00,
        "stock": 75,
        "category_name": "Accessories",
    },
    {
        "name": "MagSafe Charger",
        "description": "Wireless charger for iPhone with fast charging support.",
        "price": 39.00,
        "stock": 150,
        "category_name": "Accessories",
    },
    # Clothing - Men
    {
        "name": "Classic Fit T-Shirt",
        "description": "Comfortable 100% cotton t-shirt, available in multiple colors.",
        "price": 29.99,
        "stock": 200,
        "category_name": "Men",
    },
    {
        "name": "Slim Fit Jeans",
        "description": "Modern stretch denim jeans with comfortable fit.",
        "price": 79.99,
        "stock": 150,
        "category_name": "Men",
    },
    {
        "name": "Hooded Sweatshirt",
        "description": "Soft fleece hoodie with kangaroo pocket.",
        "price": 59.99,
        "stock": 120,
        "category_name": "Men",
    },
    # Clothing - Women
    {
        "name": "Floral Dress",
        "description": "Elegant summer dress with floral pattern.",
        "price": 89.99,
        "stock": 80,
        "category_name": "Women",
    },
    {
        "name": "Yoga Leggings",
        "description": "High-waisted leggings with 4-way stretch.",
        "price": 49.99,
        "stock": 180,
        "category_name": "Women",
    },
    {
        "name": "Cardigan Sweater",
        "description": "Cozy knit cardigan with button front.",
        "price": 69.99,
        "stock": 100,
        "category_name": "Women",
    },
    # Clothing - Kids
    {
        "name": "Kids Sneakers",
        "description": "Comfortable running shoes with non-slip soles.",
        "price": 39.99,
        "stock": 90,
        "category_name": "Kids",
    },
    {
        "name": "Cartoon T-Shirt",
        "description": "Fun graphic t-shirt with favorite characters.",
        "price": 19.99,
        "stock": 130,
        "category_name": "Kids",
    },
    # Food - Beverages
    {
        "name": "Premium Coffee Beans",
        "description": "100% Arabica coffee beans, medium roast, 1kg pack.",
        "price": 24.99,
        "stock": 250,
        "category_name": "Beverages",
    },
    {
        "name": "Green Tea Collection",
        "description": "Assorted green tea bags, 50 count.",
        "price": 14.99,
        "stock": 200,
        "category_name": "Beverages",
    },
    {
        "name": "Organic Juice Pack",
        "description": "Mixed fruit juice, 6 x 1L bottles.",
        "price": 18.99,
        "stock": 180,
        "category_name": "Beverages",
    },
    # Food - Snacks
    {
        "name": "Mixed Nuts",
        "description": "Premium roasted nuts assortment, 500g.",
        "price": 12.99,
        "stock": 220,
        "category_name": "Snacks",
    },
    {
        "name": "Dark Chocolate",
        "description": "Belgian dark chocolate 70% cocoa, 200g.",
        "price": 8.99,
        "stock": 300,
        "category_name": "Snacks",
    },
    {
        "name": "Protein Bars",
        "description": "Healthy protein bars, pack of 12.",
        "price": 29.99,
        "stock": 160,
        "category_name": "Snacks",
    },
]


async def seed_database() -> None:
    """Seed database with sample data."""
    print("🌱 Starting database seeding...")
    print()

    async for db in db_manager.get_session():
        # Check if data already exists
        result = await db.execute(select(CategoryORM).limit(1))
        if result.scalar_one_or_none():
            print("⚠️  Database already contains data. Skipping seeding.")
            return

        # Create categories
        print("📁 Creating categories...")
        category_map: dict[str, str] = {}

        for cat_data in CATEGORIES:
            category = CategoryORM(
                id=str(uuid4()),
                name=cat_data["name"],
                parent_id=cat_data["parent_id"],
            )
            db.add(category)
            category_map[cat_data["name"]] = category.id
            print(f"   ✓ {cat_data['name']}")

        await db.commit()
        print(f"   ✅ Created {len(CATEGORIES)} categories")
        print()

        # Create products
        print("📦 Creating products...")
        for prod_data in PRODUCTS:
            category_id = category_map.get(prod_data["category_name"])

            product = ProductORM(
                id=str(uuid4()),
                name=prod_data["name"],
                description=prod_data["description"],
                price=int(prod_data["price"] * 100),  # Convert to cents
                currency="USD",
                category_id=category_id,
                stock=prod_data["stock"],
            )
            db.add(product)
            print(f"   ✓ {prod_data['name']} (${prod_data['price']})")

        await db.commit()
        print(f"   ✅ Created {len(PRODUCTS)} products")
        print()

    print("✅ Database seeding complete!")
    print()
    print(f"Summary:")
    print(f"  - Categories: {len(CATEGORIES)}")
    print(f"  - Products: {len(PRODUCTS)}")


async def main() -> None:
    """Main entry point."""
    try:
        await seed_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
