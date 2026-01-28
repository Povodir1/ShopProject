"""
Core module - Infrastructure layer.

Contains database configuration, dependencies, middleware,
and application factory.
"""

from .config import settings, get_settings

__all__ = ["settings", "get_settings"]
