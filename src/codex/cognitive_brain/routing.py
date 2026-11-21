"""Capability-aware, fail-closed routing plans for Cognitive Brain middleware."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping


class RouteDecision(str, Enum):
    """Outcome of route planning before any execution occurs."""

    ALLOW = "allow"
    DENY = "deny"
    DRY_RUN_ONLY = "dry_run_only"


class RouteState(str, Enum):
    """Normalized availability state for a route adapter."""

    VERIFIED = "verified"
    EXPOSED = "exposed"
    INSTALLED = "installed"
    DOCUMENTED = "documented"
    UNAVAILABLE = "unavailable"
    DENIED = "denied"


@dataclass(frozen=True, slots=True)
class RouteCandidate:
    """One ordered adapter candidate for an operation."""

    adapter: str
    state: RouteState
    reason: str = ""


@dataclass(frozen=True, slots=True)
class RouteRequest:
    """Execution-independent routing request consumed by the planner."""

    capability: str
    action: str
    target: str
    arguments: Mapping[str, Any] = field(default_factory=dict)
    idempotency_key: str = ""


@dataclass(frozen=True, slots=True)
class RoutePlan:
    """A serializable route plan produced without performing an external action."""

    decision: RouteDecision
    preferred_adapter: str | None
    candidates: tuple[RouteCandidate, ...]
    reasons: tuple[str, ...] = ()
    execution_enabled: bool = False
    permission_family: str = "unknown"
    risk: str = "unknown"
    rollback_class: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation for HTTP or MCP clients."""

        payload = asdict(self)
        payload["decision"] = self.decision.value
        for candidate in payload["candidates"]:
            candidate["state"] = candidate["state"].value
        return payload


_ROUTE_CHAINS: dict[str, tuple[str, ...]] = {
    "github.read": ("github_mcp", "vscode_github", "gh", "rest_graphql", "playwright"),
    "github.actions.read": (
        "github_mcp",
        "vscode_actions",
        "gh",
        "rest_graphql",
        "playwright",
    ),
    "github.write": ("github_mcp", "vscode_github", "gh", "rest_graphql", "playwright"),
    "git.local": ("vscode_scm", "git", "brain_cli"),
    "shell.read": ("vscode_terminal", "brain_cli", "shell"),
    "browser.read": ("playwright_mcp", "playwright_cli", "brain_proxy"),
    "brain.read": ("brain_api",),
    "maintainer.read": ("brain_api",),
}


@dataclass(frozen=True, slots=True)
class OperationDefinition:
    """Server-owned classification for a routable action."""

    capability: str
    action: str
    permission_family: str = "read"
    risk: str = "low"
    rollback_class: str = "none"
    mutating: bool = False


_OPERATION_REGISTRY: dict[tuple[str, str], OperationDefinition] = {
    ("github.read", "get_repository"): OperationDefinition("github.read", "get_repository"),
    ("github.read", "list_pull_requests"): OperationDefinition("github.read", "list_pull_requests"),
    ("github.read", "list_workflow_runs"): OperationDefinition("github.read", "list_workflow_runs"),
    ("github.read", "list_checks"): OperationDefinition("github.read", "list_checks"),
    ("github.actions.read", "list_workflow_runs"): OperationDefinition(
        "github.actions.read", "list_workflow_runs"
    ),
    ("github.write", "create_dangling_blob"): OperationDefinition(
        "github.write", "create_dangling_blob", "contents", "low", "unreferenced", True
    ),
    ("github.write", "create_pull_request"): OperationDefinition(
        "github.write", "create_pull_request", "pull_requests", "medium", "close", True
    ),
    ("github.write", "update_pull_request"): OperationDefinition(
        "github.write", "update_pull_request", "pull_requests", "medium", "restore", True
    ),
    ("github.write", "comment_pull_request"): OperationDefinition(
        "github.write", "comment_pull_request", "pull_requests", "medium", "audit_only", True
    ),
    ("github.write", "create_close_issue"): OperationDefinition(
        "github.write", "create_close_issue", "issues", "medium", "close", True
    ),
    ("github.write", "dispatch_workflow"): OperationDefinition(
        "github.write", "dispatch_workflow", "actions", "high", "cancel_or_reconcile", True
    ),
    ("github.write", "retry_workflow"): OperationDefinition(
        "github.write", "retry_workflow", "actions", "high", "cancel_or_reconcile", True
    ),
    ("github.write", "create_check_run"): OperationDefinition(
        "github.write", "create_check_run", "checks", "high", "terminal_state", True
    ),
    ("github.write", "set_commit_status"): OperationDefinition(
        "github.write", "set_commit_status", "statuses", "medium", "terminal_state", True
    ),
    ("github.write", "create_draft_release"): OperationDefinition(
        "github.write", "create_draft_release", "releases", "high", "delete", True
    ),
    ("github.write", "create_deployment"): OperationDefinition(
        "github.write", "create_deployment", "deployments", "high", "inactive", True
    ),
    ("github.write", "create_discussion"): OperationDefinition(
        "github.write", "create_discussion", "discussions", "high", "close", True
    ),
    ("github.write", "create_delete_variable"): OperationDefinition(
        "github.write", "create_delete_variable", "variables", "medium", "delete", True
    ),
    ("github.write", "create_delete_secret"): OperationDefinition(
        "github.write", "create_delete_secret", "secrets", "critical", "delete", True
    ),
    ("github.write", "create_delete_webhook"): OperationDefinition(
        "github.write", "create_delete_webhook", "webhooks", "critical", "delete", True
    ),
    ("github.write", "restore_security_alert"): OperationDefinition(
        "github.write", "restore_security_alert", "security_events", "critical", "restore", True
    ),
    ("github.write", "no_op_repository_setting"): OperationDefinition(
        "github.write", "no_op_repository_setting", "administration", "critical", "restore", True
    ),
    ("git.local", "status"): OperationDefinition("git.local", "status"),
    ("git.local", "log"): OperationDefinition("git.local", "log"),
    ("shell.read", "run_read_only"): OperationDefinition("shell.read", "run_read_only"),
    ("browser.read", "navigate"): OperationDefinition("browser.read", "navigate"),
    ("brain.read", "capabilities"): OperationDefinition("brain.read", "capabilities"),
    ("maintainer.read", "status"): OperationDefinition("maintainer.read", "status"),
    ("maintainer.read", "keepalive_status"): OperationDefinition(
        "maintainer.read", "keepalive_status"
    ),
}

_AVAILABLE_STATES = frozenset({RouteState.VERIFIED, RouteState.EXPOSED, RouteState.INSTALLED})
_EXECUTABLE_STATES = frozenset({RouteState.VERIFIED})


def normalize_route_state(value: object) -> RouteState:
    """Coerce external capability states to the normalized route enum."""

    if isinstance(value, RouteState):
        return value
    try:
        return RouteState(str(value))
    except ValueError:
        return RouteState.UNAVAILABLE


def plan_route(
    request: RouteRequest,
    adapter_states: Mapping[str, RouteState | str | bool],
    *,
    allow_writes: bool = False,
) -> RoutePlan:
    """Build a deterministic route plan without executing any adapter.

    Write planning is dry-run-only unless a later policy layer explicitly enables
    it. Planning never treats documented capability as executable and never
    returns a fallback after an earlier verified or exposed adapter is selected.
    """

    chain = _ROUTE_CHAINS.get(request.capability)
    if chain is None:
        return RoutePlan(
            decision=RouteDecision.DENY,
            preferred_adapter=None,
            candidates=(),
            reasons=(f"unknown capability: {request.capability}",),
        )

    candidates: list[RouteCandidate] = []
    selected: str | None = None
    selected_state: RouteState | None = None
    dry_run_adapter: str | None = None
    dry_run_state: RouteState | None = None
    for adapter in chain:
        raw_state = adapter_states.get(adapter, RouteState.UNAVAILABLE)
        state = (
            RouteState.VERIFIED
            if raw_state is True
            else RouteState.UNAVAILABLE if raw_state is False else normalize_route_state(raw_state)
        )
        candidate = RouteCandidate(adapter=adapter, state=state)
        if selected is None and state in _EXECUTABLE_STATES:
            selected = adapter
            selected_state = state
        elif dry_run_adapter is None and state in _AVAILABLE_STATES:
            dry_run_adapter = adapter
            dry_run_state = state
        candidates.append(candidate)

    if selected is None:
        selected = dry_run_adapter
        selected_state = dry_run_state

    operation = _OPERATION_REGISTRY.get((request.capability, request.action))
    if operation is None:
        return RoutePlan(
            decision=RouteDecision.DENY,
            preferred_adapter=None,
            candidates=tuple(candidates),
            reasons=(f"unsupported action for capability: {request.capability}/{request.action}",),
        )

    if selected is None:
        return RoutePlan(
            decision=RouteDecision.DENY,
            preferred_adapter=None,
            candidates=tuple(candidates),
            reasons=("no verified or exposed route is currently available",),
        )

    if operation.mutating and not allow_writes:
        return RoutePlan(
            decision=RouteDecision.DRY_RUN_ONLY,
            preferred_adapter=selected,
            candidates=tuple(candidates),
            reasons=("write execution is disabled for this planning phase",),
            permission_family=operation.permission_family,
            risk=operation.risk,
            rollback_class=operation.rollback_class,
        )

    if selected_state not in _EXECUTABLE_STATES:
        return RoutePlan(
            decision=RouteDecision.DRY_RUN_ONLY,
            preferred_adapter=selected,
            candidates=tuple(candidates),
            reasons=(f"route is not operation-verified: {selected_state.value}",),
            permission_family=operation.permission_family,
            risk=operation.risk,
            rollback_class=operation.rollback_class,
        )

    return RoutePlan(
        decision=RouteDecision.ALLOW,
        preferred_adapter=selected,
        candidates=tuple(candidates),
        permission_family=operation.permission_family,
        risk=operation.risk,
        rollback_class=operation.rollback_class,
    )


def capability_catalog() -> dict[str, tuple[str, ...]]:
    """Return the currently supported capability-to-adapter mapping."""

    return dict(_ROUTE_CHAINS)


__all__ = [
    "RouteCandidate",
    "RouteDecision",
    "RoutePlan",
    "RouteRequest",
    "RouteState",
    "capability_catalog",
    "normalize_route_state",
    "plan_route",
]
