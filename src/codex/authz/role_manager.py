"""Role management for authorization system."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Role:
    """Represents a user role with associated permissions."""

    name: str
    description: str = ""
    permissions: set[str] = field(default_factory=set)
    created_at: float = 0.0
    updated_at: float = 0.0


class RoleManager:
    """Manages roles and their associations with permissions."""

    def __init__(self) -> None:
        """Initialize the role manager."""
        self._roles: dict[str, Role] = {}
        self._user_roles: dict[str, set[str]] = {}

    def create_role(
        self, name: str, description: str = "", permissions: Optional[set[str]] = None
    ) -> Role:
        """Create a new role.

        Args:
            name: Role name
            description: Role description
            permissions: Initial permissions

        Returns:
            Created Role object

        Raises:
            ValueError: If role already exists
        """
        if name in self._roles:
            raise ValueError(f"Role '{name}' already exists")

        role = Role(name=name, description=description, permissions=permissions or set())
        self._roles[name] = role
        return role

    def get_role(self, name: str) -> Optional[Role]:
        """Get a role by name.

        Args:
            name: Role name

        Returns:
            Role object or None if not found
        """
        return self._roles.get(name)

    def delete_role(self, name: str) -> bool:
        """Delete a role.

        Args:
            name: Role name

        Returns:
            True if deleted, False if not found
        """
        if name in self._roles:
            del self._roles[name]
            return True
        return False

    def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign a role to a user.

        Args:
            user_id: User ID
            role_name: Role name

        Returns:
            True if assigned, False if role doesn't exist
        """
        if role_name not in self._roles:
            return False

        if user_id not in self._user_roles:
            self._user_roles[user_id] = set()

        self._user_roles[user_id].add(role_name)
        return True

    def revoke_role(self, user_id: str, role_name: str) -> bool:
        """Revoke a role from a user.

        Args:
            user_id: User ID
            role_name: Role name

        Returns:
            True if revoked, False if not assigned
        """
        if user_id in self._user_roles and role_name in self._user_roles[user_id]:
            self._user_roles[user_id].remove(role_name)
            return True
        return False

    def get_user_roles(self, user_id: str) -> set[str]:
        """Get all roles for a user.

        Args:
            user_id: User ID

        Returns:
            Set of role names
        """
        return self._user_roles.get(user_id, set())

    def add_permission_to_role(self, role_name: str, permission: str) -> bool:
        """Add a permission to a role.

        Args:
            role_name: Role name
            permission: Permission to add

        Returns:
            True if added, False if role doesn't exist
        """
        if role_name not in self._roles:
            return False

        self._roles[role_name].permissions.add(permission)
        return True

    def remove_permission_from_role(self, role_name: str, permission: str) -> bool:
        """Remove a permission from a role.

        Args:
            role_name: Role name
            permission: Permission to remove

        Returns:
            True if removed, False if not found
        """
        if role_name not in self._roles:
            return False

        self._roles[role_name].permissions.discard(permission)
        return True

    def get_role_permissions(self, role_name: str) -> Optional[set[str]]:
        """Get all permissions for a role.

        Args:
            role_name: Role name

        Returns:
            Set of permissions or None if role doesn't exist
        """
        if role_name not in self._roles:
            return None

        return self._roles[role_name].permissions.copy()
