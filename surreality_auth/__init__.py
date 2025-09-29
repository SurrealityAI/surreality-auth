"""
Surreality Auth - Shared authentication middleware for Surreality AI services
"""

from .middleware import AuthMiddleware, require_auth

__version__ = "1.0.0"
__all__ = ["AuthMiddleware", "require_auth"]