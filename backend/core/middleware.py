"""
Middleware configuration.

Provides error handling and CORS middleware.
"""

import logging
from typing import Any

from fastapi import Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .config import get_settings
from .exceptions import AppException

settings = get_settings()
logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware.

    Catches all exceptions and returns formatted JSON responses.
    """

    def __init__(self, app: ASGIApp) -> None:
        """Initialize error handling middleware."""
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """
        Process request and handle exceptions.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response: HTTP response with error details if exception occurred
        """
        try:
            response = await call_next(request)
            return response
        except AppException as e:
            # Handle custom application exceptions
            logger.warning(f"Application exception: {e.message}")
            return Response(
                content=str(e.to_dict()),
                status_code=e.status_code,
                media_type="application/json",
            )
        except ValueError as e:
            # Handle validation errors
            logger.warning(f"Validation error: {str(e)}")
            return Response(
                content='{"error": "Validation error", "details": {"message": "' + str(e) + '"}, "status_code": 422}',
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                media_type="application/json",
            )
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                content='{"error": "Internal server error", "status_code": 500}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="application/json",
            )


def setup_cors_middleware(app: Any) -> None:
    """
    Setup CORS middleware for the application.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_error_middleware(app: Any) -> None:
    """
    Setup error handling middleware for the application.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(ErrorHandlingMiddleware)


def setup_middleware(app: Any) -> None:
    """
    Setup all middleware for the application.

    Args:
        app: FastAPI application instance
    """
    setup_cors_middleware(app)
    setup_error_middleware(app)
