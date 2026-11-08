"""Authorization framework with RBAC/ABAC/PBAC architecture."""

from .permission_registry import (
    PermissionCategory,
    PermissionDefinition,
    PermissionRegistry,
    get_permission_registry,
)
from .authorization_engine import (
    AuthorizationDecision,
    AuthorizationEngine,
    AuthorizationRequest,
    AuthorizationResult,
    IAuthorizationPolicy,
    RBACPolicy,
    get_authorization_engine,
)

__all__ = [
    "AuthorizationDecision",
    "AuthorizationEngine",
    "AuthorizationRequest",
    "AuthorizationResult",
    "IAuthorizationPolicy",
    "PermissionCategory",
    "PermissionDefinition",
    "PermissionRegistry",
    "RBACPolicy",
    "get_authorization_engine",
    "get_permission_registry",
]
