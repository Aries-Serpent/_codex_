"""Role-Based Access Control (RBAC) engine for the Codex agent ecosystem.

This module defines Codex-specific roles, the permission matrix mapping
roles to allowed (action, resource) pairs, and the ``RBACEnforcer`` class
that wraps primitives from ``src/codex/authz/`` to provide a clean, typed
enforcement surface.

Design constraints
------------------
- Zero unauthorized actions: every permission check that fails raises
  ``PermissionDeniedError``; callers must never silently succeed.
- All enforcement calls are delegated to ``src/codex/authz/`` — this
  module adds Codex-domain knowledge on top of the authz primitives.
- Python >=3.12 compatible; ``from __future__ import annotations`` used
  throughout for forward-reference safety.
"""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..authz import AuditLogger, PermissionValidator, RoleManager

# ---------------------------------------------------------------------------
# Domain enumerations
# ---------------------------------------------------------------------------


class CodexRole(str, Enum):
    """Exhaustive set of roles in the Codex ecosystem.

    Roles follow a loose hierarchy from broadest to most restricted:
    ``system_admin`` > ``agent_operator`` > ``ci_operator`` >
    ``security_reviewer`` > ``doc_maintainer`` > ``agent_reader`` >
    ``guest``.
    """

    SYSTEM_ADMIN = "system_admin"
    """Full control over all resources and can manage all other roles."""

    AGENT_OPERATOR = "agent_operator"
    """Can deploy, configure and execute agents; read/write workflows."""

    AGENT_READER = "agent_reader"
    """Read-only access to agent state, logs, and reports."""

    CI_OPERATOR = "ci_operator"
    """Can trigger CI workflows, read workflow runs, and approve CI gates."""

    SECURITY_REVIEWER = "security_reviewer"
    """Can read and approve security-sensitive changes and secrets rotations."""

    DOC_MAINTAINER = "doc_maintainer"
    """Can create, update, and delete documentation resources."""

    GUEST = "guest"
    """Minimal read-only access to public reports and documentation."""


class ResourceType(str, Enum):
    """Resource types protected by RBAC."""

    AGENTS = "agents"
    WORKFLOWS = "workflows"
    SECRETS = "secrets"  # pragma: allowlist secret
    DOCS = "docs"
    CODE = "code"
    REPORTS = "reports"
    ROLES = "roles"
    AUDIT_LOGS = "audit_logs"


class Action(str, Enum):
    """Actions that can be performed on a resource."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    ASSIGN = "assign"


# ---------------------------------------------------------------------------
# Permission matrix
# ---------------------------------------------------------------------------

# Format: {CodexRole: {ResourceType: set[Action]}}
# This is the single source-of-truth for all RBAC decisions in Codex.
_ROLE_PERMISSION_MATRIX: dict[CodexRole, dict[ResourceType, set[Action]]] = {
    CodexRole.SYSTEM_ADMIN: {
        ResourceType.AGENTS: {
            Action.CREATE,
            Action.READ,
            Action.UPDATE,
            Action.DELETE,
            Action.EXECUTE,
            Action.APPROVE,
        },
        ResourceType.WORKFLOWS: {
            Action.CREATE,
            Action.READ,
            Action.UPDATE,
            Action.DELETE,
            Action.EXECUTE,
            Action.APPROVE,
        },
        ResourceType.SECRETS: {
            Action.CREATE,
            Action.READ,
            Action.UPDATE,
            Action.DELETE,
            Action.APPROVE,
        },
        ResourceType.DOCS: {
            Action.CREATE,
            Action.READ,
            Action.UPDATE,
            Action.DELETE,
            Action.APPROVE,
        },
        ResourceType.CODE: {
            Action.CREATE,
            Action.READ,
            Action.UPDATE,
            Action.DELETE,
            Action.APPROVE,
        },
        ResourceType.REPORTS: {
            Action.CREATE,
            Action.READ,
            Action.UPDATE,
            Action.DELETE,
        },
        ResourceType.ROLES: {
            Action.CREATE,
            Action.READ,
            Action.UPDATE,
            Action.DELETE,
            Action.ASSIGN,
        },
        ResourceType.AUDIT_LOGS: {Action.READ},
    },
    CodexRole.AGENT_OPERATOR: {
        ResourceType.AGENTS: {
            Action.CREATE,
            Action.READ,
            Action.UPDATE,
            Action.EXECUTE,
        },
        ResourceType.WORKFLOWS: {
            Action.CREATE,
            Action.READ,
            Action.UPDATE,
            Action.EXECUTE,
        },
        ResourceType.SECRETS: {Action.READ},
        ResourceType.DOCS: {Action.READ},
        ResourceType.CODE: {Action.READ, Action.UPDATE},
        ResourceType.REPORTS: {Action.CREATE, Action.READ},
        ResourceType.ROLES: {Action.READ},
        ResourceType.AUDIT_LOGS: {Action.READ},
    },
    CodexRole.CI_OPERATOR: {
        ResourceType.AGENTS: {Action.READ, Action.EXECUTE},
        ResourceType.WORKFLOWS: {
            Action.READ,
            Action.EXECUTE,
            Action.APPROVE,
        },
        ResourceType.SECRETS: set(),
        ResourceType.DOCS: {Action.READ},
        ResourceType.CODE: {Action.READ},
        ResourceType.REPORTS: {Action.CREATE, Action.READ},
        ResourceType.ROLES: {Action.READ},
        ResourceType.AUDIT_LOGS: {Action.READ},
    },
    CodexRole.SECURITY_REVIEWER: {
        ResourceType.AGENTS: {Action.READ},
        ResourceType.WORKFLOWS: {Action.READ, Action.APPROVE},
        ResourceType.SECRETS: {Action.READ, Action.APPROVE},
        ResourceType.DOCS: {Action.READ},
        ResourceType.CODE: {Action.READ, Action.APPROVE},
        ResourceType.REPORTS: {Action.READ},
        ResourceType.ROLES: {Action.READ},
        ResourceType.AUDIT_LOGS: {Action.READ},
    },
    CodexRole.DOC_MAINTAINER: {
        ResourceType.AGENTS: {Action.READ},
        ResourceType.WORKFLOWS: {Action.READ},
        ResourceType.SECRETS: set(),
        ResourceType.DOCS: {
            Action.CREATE,
            Action.READ,
            Action.UPDATE,
            Action.DELETE,
        },
        ResourceType.CODE: {Action.READ},
        ResourceType.REPORTS: {Action.READ},
        ResourceType.ROLES: {Action.READ},
        ResourceType.AUDIT_LOGS: set(),
    },
    CodexRole.AGENT_READER: {
        ResourceType.AGENTS: {Action.READ},
        ResourceType.WORKFLOWS: {Action.READ},
        ResourceType.SECRETS: set(),
        ResourceType.DOCS: {Action.READ},
        ResourceType.CODE: {Action.READ},
        ResourceType.REPORTS: {Action.READ},
        ResourceType.ROLES: {Action.READ},
        ResourceType.AUDIT_LOGS: set(),
    },
    CodexRole.GUEST: {
        ResourceType.AGENTS: set(),
        ResourceType.WORKFLOWS: set(),
        ResourceType.SECRETS: set(),
        ResourceType.DOCS: {Action.READ},
        ResourceType.CODE: set(),
        ResourceType.REPORTS: {Action.READ},
        ResourceType.ROLES: set(),
        ResourceType.AUDIT_LOGS: set(),
    },
}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class PermissionDeniedError(PermissionError):
    """Raised when a user lacks the required permission for an action.

    Attributes:
        user_id:  Identity that was denied.
        action:   Action that was attempted.
        resource: Resource target of the action.
    """

    def __init__(self, user_id: str, action: str, resource: str) -> None:
        self.user_id = user_id
        self.action = action
        self.resource = resource
        super().__init__(
            f"User '{user_id}' is not permitted to perform '{action}' on resource '{resource}'."
        )


# ---------------------------------------------------------------------------
# Policy dataclass
# ---------------------------------------------------------------------------


@dataclass
class RBACPolicy:
    """Declarative RBAC policy definition.

    Attributes:
        name:           Human-readable policy name.
        role:           The ``CodexRole`` this policy applies to.
        resource:       The ``ResourceType`` being protected.
        allowed_actions: Set of ``Action`` values permitted by this policy.
        description:    Optional free-text description for documentation.
        created_at:     Unix timestamp of policy creation.
    """

    name: str
    role: CodexRole
    resource: ResourceType
    allowed_actions: set[Action] = field(default_factory=set)
    description: str = ""
    created_at: float = field(default_factory=time.time)

    def permits(self, action: Action) -> bool:
        """Return True if *action* is in the allowed set."""
        return action in self.allowed_actions


# ---------------------------------------------------------------------------
# Core enforcer
# ---------------------------------------------------------------------------


class RBACEnforcer:
    """Codex RBAC enforcement engine.

    Wraps ``RoleManager`` and ``PermissionValidator`` from
    ``src/codex/authz/`` and applies the Codex permission matrix on top.

    All checks are forwarded to the underlying authz primitives so that the
    authz layer remains the authoritative source; this class provides the
    Codex-domain permission matrix and typed API surface.

    Thread-safety: This class maintains in-memory role assignments.  In a
    multi-process environment, back the ``RoleManager`` with a shared store.

    Example usage::

        enforcer = RBACEnforcer()
        enforcer.assign_role("alice", CodexRole.AGENT_OPERATOR)
        enforcer.check_permission("alice", Action.EXECUTE, ResourceType.AGENTS)
        # → True

        enforcer.check_permission("alice", Action.DELETE, ResourceType.SECRETS)
        # → raises PermissionDeniedError
    """

    def __init__(self) -> None:
        """Initialise the enforcer and register built-in Codex roles."""
        self._role_manager = RoleManager()
        self._permission_validator = PermissionValidator()
        self._audit_logger = AuditLogger()

        self._bootstrap_roles()

    # ------------------------------------------------------------------
    # Bootstrap
    # ------------------------------------------------------------------

    def _bootstrap_roles(self) -> None:
        """Register all Codex roles and their permissions in the authz layer."""
        for role in CodexRole:
            role_permissions = self._build_permission_set(role)
            self._role_manager.create_role(
                name=role.value,
                description=f"Codex built-in role: {role.value}",
                permissions=role_permissions,
            )
            for perm_str in role_permissions:
                self._permission_validator.grant_permission(role.value, perm_str)

    @staticmethod
    def _build_permission_set(role: CodexRole) -> set[str]:
        """Convert the permission matrix entry for *role* to permission strings.

        Permission strings have the format ``"<resource>:<action>"``, e.g.
        ``"agents:execute"``.
        """
        perms: set[str] = set()
        resource_map = _ROLE_PERMISSION_MATRIX.get(role, {})
        for resource, actions in resource_map.items():
            for action in actions:
                perms.add(f"{resource.value}:{action.value}")
        return perms

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def assign_role(self, user_id: str, role: CodexRole | str) -> None:
        """Assign *role* to *user_id*.

        Args:
            user_id: Unique user or agent identifier.
            role:    A ``CodexRole`` enum member or its string value.

        Raises:
            ValueError: If *role* is not a recognised Codex role.
        """
        role_value = role.value if isinstance(role, CodexRole) else role
        if role_value not in {r.value for r in CodexRole}:
            raise ValueError(f"Unknown Codex role: '{role_value}'")

        assigned = self._role_manager.assign_role(user_id, role_value)
        if not assigned:
            raise ValueError(
                f"Role '{role_value}' not found in RoleManager. "
                "This is a bootstrap inconsistency — please report."
            )
        self._audit_logger._data[f"assign:{user_id}:{role_value}:{int(time.time() * 1000)}"] = (
            time.time()
        )

    def revoke_role(self, user_id: str, role: CodexRole | str) -> None:
        """Revoke *role* from *user_id*.

        Args:
            user_id: Unique user or agent identifier.
            role:    A ``CodexRole`` enum member or its string value.

        Raises:
            ValueError: If the role was not assigned to the user.
        """
        role_value = role.value if isinstance(role, CodexRole) else role
        revoked = self._role_manager.revoke_role(user_id, role_value)
        if not revoked:
            raise ValueError(f"Role '{role_value}' was not assigned to user '{user_id}'.")
        self._audit_logger._data[f"revoke:{user_id}:{role_value}:{int(time.time() * 1000)}"] = (
            time.time()
        )

    def get_user_roles(self, user_id: str) -> list[str]:
        """Return the list of role names currently assigned to *user_id*.

        Args:
            user_id: Unique user or agent identifier.

        Returns:
            Sorted list of role name strings (empty if none assigned).
        """
        return sorted(self._role_manager.get_user_roles(user_id))

    def check_permission(
        self,
        user_id: str,
        action: Action | str,
        resource: ResourceType | str,
        *,
        raise_on_deny: bool = True,
    ) -> bool:
        """Determine whether *user_id* may perform *action* on *resource*.

        Iterates over all roles assigned to *user_id* and returns ``True``
        as soon as one role grants the requested permission.

        Args:
            user_id:       Unique user or agent identifier.
            action:        The ``Action`` (or its string value) to authorise.
            resource:      The ``ResourceType`` (or its string value) target.
            raise_on_deny: When ``True`` (default) raise ``PermissionDeniedError``
                           instead of returning ``False``.

        Returns:
            ``True`` if the user is authorised.

        Raises:
            PermissionDeniedError: When *raise_on_deny* is ``True`` and the
                                   user lacks the required permission.
        """
        action_value = action.value if isinstance(action, Action) else action
        resource_value = resource.value if isinstance(resource, ResourceType) else resource
        perm_str = f"{resource_value}:{action_value}"

        user_roles = self._role_manager.get_user_roles(user_id)
        for role_name in user_roles:
            if self._permission_validator.has_permission(role_name, perm_str):
                self._audit_logger._data[f"allow:{user_id}:{perm_str}:{time.time()}"] = True
                return True

        # Permission denied
        self._audit_logger._data[f"deny:{user_id}:{perm_str}:{time.time()}"] = False

        if raise_on_deny:
            raise PermissionDeniedError(user_id, action_value, resource_value)
        return False

    def get_policies(self) -> list[RBACPolicy]:
        """Return all built-in RBAC policies derived from the permission matrix.

        Returns:
            List of ``RBACPolicy`` objects, one per (role, resource) pair.
        """
        policies: list[RBACPolicy] = []
        for role, resource_map in _ROLE_PERMISSION_MATRIX.items():
            for resource, actions in resource_map.items():
                if actions:
                    policies.append(
                        RBACPolicy(
                            name=f"{role.value}:{resource.value}",
                            role=role,
                            resource=resource,
                            allowed_actions=set(actions),
                            description=(
                                f"Built-in policy granting {role.value} "
                                f"{', '.join(a.value for a in actions)} "
                                f"on {resource.value}."
                            ),
                        )
                    )
        return policies

    def user_has_role(self, user_id: str, role: CodexRole | str) -> bool:
        """Return True if *user_id* currently holds *role*.

        Args:
            user_id: Unique user or agent identifier.
            role:    A ``CodexRole`` enum member or its string value.
        """
        role_value = role.value if isinstance(role, CodexRole) else role
        return role_value in self._role_manager.get_user_roles(user_id)


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------

_DEFAULT_ENFORCER: RBACEnforcer | None = None


def _get_default_enforcer() -> RBACEnforcer:
    """Return (and lazily initialise) the module-level default enforcer."""
    global _DEFAULT_ENFORCER  # noqa: PLW0603
    if _DEFAULT_ENFORCER is None:
        _DEFAULT_ENFORCER = RBACEnforcer()
    return _DEFAULT_ENFORCER


def require_permission(
    action: Action | str,
    resource: ResourceType | str,
    *,
    enforcer: RBACEnforcer | None = None,
    user_id_kwarg: str = "user_id",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that guards a callable with an RBAC permission check.

    The decorated function **must** accept a ``user_id`` keyword argument
    (name configurable via *user_id_kwarg*).  The check is performed before
    the wrapped function executes; ``PermissionDeniedError`` propagates
    unmodified on failure.

    Args:
        action:         Required ``Action`` (or string value).
        resource:       Required ``ResourceType`` (or string value).
        enforcer:       Custom ``RBACEnforcer`` instance; defaults to the
                        module-level singleton.
        user_id_kwarg:  Name of the keyword argument carrying the user ID in
                        the decorated function's signature.

    Returns:
        Decorator that wraps the target callable.

    Example::

        @require_permission(Action.EXECUTE, ResourceType.AGENTS)
        def deploy_agent(agent_id: str, *, user_id: str) -> None:
            ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _enforcer = enforcer or _get_default_enforcer()
            uid = kwargs.get(user_id_kwarg)
            if uid is None:
                raise TypeError(
                    f"@require_permission: '{user_id_kwarg}' keyword argument "
                    f"not found in call to '{func.__qualname__}'."
                )
            _enforcer.check_permission(uid, action, resource)
            return func(*args, **kwargs)

        return wrapper

    return decorator
