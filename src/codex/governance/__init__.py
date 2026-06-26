"""Governance package for the Codex agent ecosystem.

Provides Role-Based Access Control (RBAC) enforcement, approval workflow
management, and policy-gating for all agent operations.

Exports:
    RBACEnforcer         — Core RBAC enforcement engine
    RBACPolicy           — Dataclass for policy definitions
    PermissionDeniedError — Raised on unauthorised access
    require_permission   — Decorator for RBAC-guarded callables
    ApprovalWorkflowEngine — Multi-approver workflow engine
    ApprovalRequest      — Dataclass for in-flight approval requests
    ApprovalStatus       — Enum of approval lifecycle states
    CodexRole            — Enum of all Codex-specific roles
"""

from __future__ import annotations

from .approval_workflows import (
    ApprovalRequest,
    ApprovalStatus,
    ApprovalWorkflowEngine,
)
from .rbac import (
    CodexRole,
    PermissionDeniedError,
    RBACEnforcer,
    RBACPolicy,
    require_permission,
)

__all__ = [
    # RBAC
    "RBACEnforcer",
    "RBACPolicy",
    "PermissionDeniedError",
    "require_permission",
    "CodexRole",
    # Approval workflows
    "ApprovalWorkflowEngine",
    "ApprovalRequest",
    "ApprovalStatus",
]
