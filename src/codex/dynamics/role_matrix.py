"""Utilities for aligning Zendesk and Dynamics role permissions."""

from __future__ import annotations

from collections.abc import Iterable

from codex.dynamics.model.role import DynamicsRole
from codex.zendesk.model.role import Role as ZendeskRole


def build_role_matrix(
    zendesk_roles: Iterable[ZendeskRole],
    dynamics_roles: Iterable[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """Build a permission category matrix across Zendesk and Dynamics roles."""

    category_map = {
        "Ticket Management": ("tickets", "incident"),
        "User Management": ("users", "account"),
    }
    matrix: dict[str, dict[str, bool]] = {category: {} for category in category_map}

    for role in zendesk_roles:
        for category, (zendesk_flag, _) in category_map.items():
            has_permission = getattr(role.permissions, zendesk_flag, False)
            matrix[category][role.name] = bool(has_permission)

    for role in dynamics_roles:
        for category, (_, dynamics_entity) in category_map.items():
            has_privilege = any(
                privilege.entity.lower() == dynamics_entity.lower() for privilege in role.privileges
            )
            matrix[category][role.name] = bool(has_privilege)

    return matrix
