"""Permission validation for authorization system."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Permission:
    """Represents a permission with scope and constraints."""

    name: str
    resource: str
    action: str
    scope: str = "global"
    constraints: Optional[dict[str, Any]] = None


class PermissionValidator:
    """Validates permissions and access rights."""

    def __init__(self) -> None:
        """Initialize permission validator."""
        self._permissions: set[str] = set()
        self._role_permissions: dict[str, Any] = {}

    def register_permission(self, permission: Permission) -> bool:
        """Register a permission.

        Args:
            permission: Permission object

        Returns:
            True if registered, False if already exists
        """
        perm_key = f"{permission.resource}:{permission.action}"
        if perm_key in self._permissions:
            return False

        self._permissions.add(perm_key)
        return True

    def validate_permission(self, user_id: str, permission: str, resource: str) -> bool:
        """Validate if user has permission for resource.

        Args:
            user_id: User ID
            permission: Permission name (read, write, delete, etc.)
            resource: Resource identifier

        Returns:
            True if user has permission
        """
        perm_key = f"{resource}:{permission}"
        return perm_key in self._permissions

    def grant_permission(self, role: str, permission: str) -> bool:
        """Grant permission to role.

        Args:
            role: Role name
            permission: Permission string

        Returns:
            True if granted
        """
        if role not in self._role_permissions:
            self._role_permissions[role] = set()

        self._role_permissions[role].add(permission)
        return True

    def has_permission(self, role: str, permission: str) -> bool:
        """Check if role has permission.

        Args:
            role: Role name
            permission: Permission string

        Returns:
            True if role has permission
        """
        if role not in self._role_permissions:
            return False

        return permission in self._role_permissions[role]
