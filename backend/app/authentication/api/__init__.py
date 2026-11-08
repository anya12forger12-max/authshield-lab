"""Authentication API package."""

from .routes import router, configure_dependencies

__all__ = ["router", "configure_dependencies"]
