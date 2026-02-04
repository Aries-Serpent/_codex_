"""
Role Matrix Module

This module provides functionality for role matrix.

Usage:
    from dynamics.role_matrix import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from codex.dynamics.model.role import DynamicsRole
from codex.zendesk.model.role import Role as ZendeskRole
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_build_role_matrix__mutmut_orig(
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


def x_build_role_matrix__mutmut_1(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = None
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


def x_build_role_matrix__mutmut_2(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "XXTicket ManagementXX": ("tickets", "incident"),
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


def x_build_role_matrix__mutmut_3(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "ticket management": ("tickets", "incident"),
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


def x_build_role_matrix__mutmut_4(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "TICKET MANAGEMENT": ("tickets", "incident"),
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


def x_build_role_matrix__mutmut_5(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "Ticket Management": ("XXticketsXX", "incident"),
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


def x_build_role_matrix__mutmut_6(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "Ticket Management": ("TICKETS", "incident"),
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


def x_build_role_matrix__mutmut_7(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "Ticket Management": ("tickets", "XXincidentXX"),
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


def x_build_role_matrix__mutmut_8(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "Ticket Management": ("tickets", "INCIDENT"),
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


def x_build_role_matrix__mutmut_9(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "Ticket Management": ("tickets", "incident"),
        "XXUser ManagementXX": ("users", "account"),
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


def x_build_role_matrix__mutmut_10(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "Ticket Management": ("tickets", "incident"),
        "user management": ("users", "account"),
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


def x_build_role_matrix__mutmut_11(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "Ticket Management": ("tickets", "incident"),
        "USER MANAGEMENT": ("users", "account"),
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


def x_build_role_matrix__mutmut_12(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "Ticket Management": ("tickets", "incident"),
        "User Management": ("XXusersXX", "account"),
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


def x_build_role_matrix__mutmut_13(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "Ticket Management": ("tickets", "incident"),
        "User Management": ("USERS", "account"),
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


def x_build_role_matrix__mutmut_14(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "Ticket Management": ("tickets", "incident"),
        "User Management": ("users", "XXaccountXX"),
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


def x_build_role_matrix__mutmut_15(
    zendesk_roles: list[ZendeskRole],
    dynamics_roles: list[DynamicsRole],
) -> dict[str, dict[str, bool]]:
    """
    Build a matrix of permission categories for Zendesk and Dynamics roles.
    Each entry maps a role name to a boolean flag indicating category access.
    """

    category_map = {
        "Ticket Management": ("tickets", "incident"),
        "User Management": ("users", "ACCOUNT"),
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


def x_build_role_matrix__mutmut_16(
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
    matrix: dict[str, dict[str, bool]] = None

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


def x_build_role_matrix__mutmut_17(
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
            has_permission = None
            matrix[category][zendesk_role.name] = bool(has_permission)

    for dynamics_role in dynamics_roles:
        for category, (_, dynamics_entity) in category_map.items():
            has_privilege = any(
                privilege.entity.lower() == dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_18(
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
            has_permission = getattr(None, zendesk_flag, False)
            matrix[category][zendesk_role.name] = bool(has_permission)

    for dynamics_role in dynamics_roles:
        for category, (_, dynamics_entity) in category_map.items():
            has_privilege = any(
                privilege.entity.lower() == dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_19(
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
            has_permission = getattr(zendesk_role.permissions, None, False)
            matrix[category][zendesk_role.name] = bool(has_permission)

    for dynamics_role in dynamics_roles:
        for category, (_, dynamics_entity) in category_map.items():
            has_privilege = any(
                privilege.entity.lower() == dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_20(
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
            has_permission = getattr(zendesk_role.permissions, zendesk_flag, None)
            matrix[category][zendesk_role.name] = bool(has_permission)

    for dynamics_role in dynamics_roles:
        for category, (_, dynamics_entity) in category_map.items():
            has_privilege = any(
                privilege.entity.lower() == dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_21(
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
            has_permission = getattr(zendesk_flag, False)
            matrix[category][zendesk_role.name] = bool(has_permission)

    for dynamics_role in dynamics_roles:
        for category, (_, dynamics_entity) in category_map.items():
            has_privilege = any(
                privilege.entity.lower() == dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_22(
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
            has_permission = getattr(zendesk_role.permissions, False)
            matrix[category][zendesk_role.name] = bool(has_permission)

    for dynamics_role in dynamics_roles:
        for category, (_, dynamics_entity) in category_map.items():
            has_privilege = any(
                privilege.entity.lower() == dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_23(
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
            has_permission = getattr(zendesk_role.permissions, zendesk_flag, )
            matrix[category][zendesk_role.name] = bool(has_permission)

    for dynamics_role in dynamics_roles:
        for category, (_, dynamics_entity) in category_map.items():
            has_privilege = any(
                privilege.entity.lower() == dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_24(
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
            has_permission = getattr(zendesk_role.permissions, zendesk_flag, True)
            matrix[category][zendesk_role.name] = bool(has_permission)

    for dynamics_role in dynamics_roles:
        for category, (_, dynamics_entity) in category_map.items():
            has_privilege = any(
                privilege.entity.lower() == dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_25(
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
            matrix[category][zendesk_role.name] = None

    for dynamics_role in dynamics_roles:
        for category, (_, dynamics_entity) in category_map.items():
            has_privilege = any(
                privilege.entity.lower() == dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_26(
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
            matrix[category][zendesk_role.name] = bool(None)

    for dynamics_role in dynamics_roles:
        for category, (_, dynamics_entity) in category_map.items():
            has_privilege = any(
                privilege.entity.lower() == dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_27(
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
            has_privilege = None
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_28(
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
                None
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_29(
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
                privilege.entity.upper() == dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_30(
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
                privilege.entity.lower() != dynamics_entity.lower()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_31(
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
                privilege.entity.lower() == dynamics_entity.upper()
                for privilege in dynamics_role.privileges
            )
            matrix[category][dynamics_role.name] = bool(has_privilege)

    return matrix


def x_build_role_matrix__mutmut_32(
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
            matrix[category][dynamics_role.name] = None

    return matrix


def x_build_role_matrix__mutmut_33(
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
            matrix[category][dynamics_role.name] = bool(None)

    return matrix

x_build_role_matrix__mutmut_mutants : ClassVar[MutantDict] = {
'x_build_role_matrix__mutmut_1': x_build_role_matrix__mutmut_1, 
    'x_build_role_matrix__mutmut_2': x_build_role_matrix__mutmut_2, 
    'x_build_role_matrix__mutmut_3': x_build_role_matrix__mutmut_3, 
    'x_build_role_matrix__mutmut_4': x_build_role_matrix__mutmut_4, 
    'x_build_role_matrix__mutmut_5': x_build_role_matrix__mutmut_5, 
    'x_build_role_matrix__mutmut_6': x_build_role_matrix__mutmut_6, 
    'x_build_role_matrix__mutmut_7': x_build_role_matrix__mutmut_7, 
    'x_build_role_matrix__mutmut_8': x_build_role_matrix__mutmut_8, 
    'x_build_role_matrix__mutmut_9': x_build_role_matrix__mutmut_9, 
    'x_build_role_matrix__mutmut_10': x_build_role_matrix__mutmut_10, 
    'x_build_role_matrix__mutmut_11': x_build_role_matrix__mutmut_11, 
    'x_build_role_matrix__mutmut_12': x_build_role_matrix__mutmut_12, 
    'x_build_role_matrix__mutmut_13': x_build_role_matrix__mutmut_13, 
    'x_build_role_matrix__mutmut_14': x_build_role_matrix__mutmut_14, 
    'x_build_role_matrix__mutmut_15': x_build_role_matrix__mutmut_15, 
    'x_build_role_matrix__mutmut_16': x_build_role_matrix__mutmut_16, 
    'x_build_role_matrix__mutmut_17': x_build_role_matrix__mutmut_17, 
    'x_build_role_matrix__mutmut_18': x_build_role_matrix__mutmut_18, 
    'x_build_role_matrix__mutmut_19': x_build_role_matrix__mutmut_19, 
    'x_build_role_matrix__mutmut_20': x_build_role_matrix__mutmut_20, 
    'x_build_role_matrix__mutmut_21': x_build_role_matrix__mutmut_21, 
    'x_build_role_matrix__mutmut_22': x_build_role_matrix__mutmut_22, 
    'x_build_role_matrix__mutmut_23': x_build_role_matrix__mutmut_23, 
    'x_build_role_matrix__mutmut_24': x_build_role_matrix__mutmut_24, 
    'x_build_role_matrix__mutmut_25': x_build_role_matrix__mutmut_25, 
    'x_build_role_matrix__mutmut_26': x_build_role_matrix__mutmut_26, 
    'x_build_role_matrix__mutmut_27': x_build_role_matrix__mutmut_27, 
    'x_build_role_matrix__mutmut_28': x_build_role_matrix__mutmut_28, 
    'x_build_role_matrix__mutmut_29': x_build_role_matrix__mutmut_29, 
    'x_build_role_matrix__mutmut_30': x_build_role_matrix__mutmut_30, 
    'x_build_role_matrix__mutmut_31': x_build_role_matrix__mutmut_31, 
    'x_build_role_matrix__mutmut_32': x_build_role_matrix__mutmut_32, 
    'x_build_role_matrix__mutmut_33': x_build_role_matrix__mutmut_33
}

def build_role_matrix(*args, **kwargs):
    result = _mutmut_trampoline(x_build_role_matrix__mutmut_orig, x_build_role_matrix__mutmut_mutants, args, kwargs)
    return result 

build_role_matrix.__signature__ = _mutmut_signature(x_build_role_matrix__mutmut_orig)
x_build_role_matrix__mutmut_orig.__name__ = 'x_build_role_matrix'
