from __future__ import annotations

from codex.dynamics.model.role import DynamicsRole
from codex.zendesk.model.role import Role as ZendeskRole


def build_role_matrix(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "Ticket Management": ("tickets", "incident"),
        "User Management": ("users", "account"),
    }
    matrix: dict[str, dict[str, bool]] = {category: {} for category in category_map}

    for zendesk_role in zendesk_roles:
        for category, (zendesk_flag, _) in category_map.items():
            has_permission = getattr(zendesk_role.permissions, zendesk_flag, False)
            matrix[category][zendesk_role.name] = bool(has_permission)

    for dynamics_role in dynamics_roles:
        for category, (_, dynamics_entity) in category_map.items():
            has_privilege = any(
                privilege.entity.lower() == dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix
