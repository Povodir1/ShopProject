"""
FastAPI application factory.

Creates and configures the FastAPI application.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from .config import get_settings
from .database import db_manager
from .middleware import setup_middleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    print("🚀 Starting application...")
    print(f"📦 Database: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    print(f"🌐 Debug mode: {settings.DEBUG}")

    yield

    # Shutdown
    print("🛑 Shutting down application...")
    await db_manager.close()


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        FastAPI: Configured application instance

    Example:
        app = create_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="E-commerce API with catalog and cart functionality",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Setup middleware
    setup_middleware(app)

    # Include routers
    from modules.catalog.presentation.api.routes import router as catalog_router
    from modules.cart.presentation.api.routes import router as cart_router

    app.include_router(catalog_router, prefix="/api", tags=["catalog"])
    app.include_router(cart_router, prefix="/api", tags=["cart"])

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok", "service": settings.APP_NAME}

    return app


# Create application instance
app = create_app()
