"""Backward-compatibility shim — re-exports from permissions.py."""
from app.security.permissions import Role, Permission, has_permission, ROLE_PERMISSIONS

__all__ = ["Role", "Permission", "has_permission", "ROLE_PERMISSIONS"]
