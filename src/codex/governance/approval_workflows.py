"""Approval workflow engine for the Codex governance layer.

This module provides a lightweight, in-process approval workflow engine that
integrates with the RBAC system to implement a human-in-the-loop gate for
sensitive operations.

Design goals
------------
- **<5 minute SLA**: Every ``ApprovalRequest`` carries an ``expires_at``
  timestamp (default 300 s / 5 min).  Requests not resolved before that
  deadline are automatically transitioned to ``EXPIRED`` on the next access.
- **RBAC auto-approval**: If the requester already holds a role that grants
  the ``approve`` action on the target resource, the request is
  auto-approved immediately without requiring additional approvers.
- **Full audit trail**: Every state transition (submit, approve, reject,
  expire) is recorded via the authz ``AuditLogger``.
- **Immutable history**: Resolved requests (APPROVED/REJECTED/EXPIRED) are
  kept in memory; their state cannot be mutated after resolution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from ..authz import AuditLogger

if TYPE_CHECKING:
    from .rbac import Action, RBACEnforcer, ResourceType


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ApprovalStatus(str, Enum):
    """Lifecycle states of an ``ApprovalRequest``."""

    PENDING = "pending"
    """Awaiting at least one approver action."""

    APPROVED = "approved"
    """All required approvers have approved; action may proceed."""

    REJECTED = "rejected"
    """At least one approver has rejected; action is blocked."""

    EXPIRED = "expired"
    """Approval window elapsed without resolution."""


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class ApprovalDecision:
    """A single approver decision on an ``ApprovalRequest``.

    Attributes:
        approver:   Identity of the person who made the decision.
        decision:   ``ApprovalStatus.APPROVED`` or ``ApprovalStatus.REJECTED``.
        reason:     Optional free-text rationale.
        decided_at: Unix timestamp of the decision.
    """

    approver: str
    decision: ApprovalStatus
    reason: str = ""
    decided_at: float = field(default_factory=time.time)


@dataclass
class ApprovalRequest:
    """An in-flight request for approval of a sensitive operation.

    Attributes:
        id:           UUID-based unique identifier.
        action:       The action being requested (e.g. ``"execute"``).
        resource:     The resource targeted (e.g. ``"agents"``).
        requester:    Identity of the user/agent that submitted the request.
        approvers:    Required approver identities (empty = auto-approve if
                      requester is privileged).
        status:       Current ``ApprovalStatus``.
        created_at:   Unix timestamp of submission.
        expires_at:   Unix timestamp after which the request is EXPIRED.
        decisions:    Ordered list of ``ApprovalDecision`` records.
        context:      Arbitrary metadata attached by the requester.
        auto_approved: Set to ``True`` when RBAC auto-approval was applied.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action: str = ""
    resource: str = ""
    requester: str = ""
    approvers: list[str] = field(default_factory=list)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 300.0)
    decisions: list[ApprovalDecision] = field(default_factory=list)
    context: dict[str, object] = field(default_factory=dict)
    auto_approved: bool = False

    # ------------------------------------------------------------------
    # Computed helpers (not persisted)
    # ------------------------------------------------------------------

    @property
    def is_expired(self) -> bool:
        """Return ``True`` if the approval window has elapsed."""
        return time.time() > self.expires_at

    @property
    def is_resolved(self) -> bool:
        """Return ``True`` if the request is no longer actionable."""
        return self.status in (
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
            ApprovalStatus.EXPIRED,
        )

    @property
    def age_seconds(self) -> float:
        """Elapsed time in seconds since the request was created."""
        return time.time() - self.created_at

    @property
    def remaining_seconds(self) -> float:
        """Seconds remaining before the request expires (0 if already expired)."""
        return max(0.0, self.expires_at - time.time())


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class ApprovalWorkflowEngine:
    """Multi-approver workflow engine with RBAC integration.

    Manages the full lifecycle of ``ApprovalRequest`` objects:
    submit → (approve | reject | expire).

    Parameters
    ----------
    rbac_enforcer:
        An ``RBACEnforcer`` instance used for auto-approval checks.  Pass
        ``None`` to disable RBAC auto-approval (all requests must be
        manually approved).
    default_timeout_seconds:
        Approval window in seconds.  Defaults to 300 (5 minutes) to satisfy
        the <5-minute SLA requirement.

    Example usage::

        engine = ApprovalWorkflowEngine(rbac_enforcer=enforcer)

        req = engine.submit_request(
            action="execute",
            resource="agents",
            requester="bob",
            required_approvers=["alice"],
            context={"agent_id": "my-agent"},
        )

        engine.approve(req.id, approver="alice")
        assert req.status == ApprovalStatus.APPROVED
    """

    def __init__(
        self,
        rbac_enforcer: RBACEnforcer | None = None,
        default_timeout_seconds: float = 300.0,
    ) -> None:
        self._enforcer = rbac_enforcer
        self._timeout = default_timeout_seconds
        self._requests: dict[str, ApprovalRequest] = {}
        self._audit = AuditLogger()

    # ------------------------------------------------------------------
    # Submit
    # ------------------------------------------------------------------

    def submit_request(
        self,
        action: str | Action,
        resource: str | ResourceType,
        requester: str,
        required_approvers: list[str] | None = None,
        context: dict[str, object] | None = None,
        timeout_seconds: float | None = None,
    ) -> ApprovalRequest:
        """Submit a new approval request.

        If *rbac_enforcer* was provided **and** the requester already holds a
        role that grants the ``approve`` action on *resource*, the request is
        immediately auto-approved.

        Args:
            action:             The action requiring approval.
            resource:           The resource type being acted on.
            requester:          Identity of the submitting user/agent.
            required_approvers: List of identities that must approve.  If
                                ``None`` or empty, any single approver suffices
                                unless auto-approval applies.
            context:            Arbitrary metadata (agent IDs, PR numbers, etc.)
            timeout_seconds:    Override the engine default timeout for this
                                request.

        Returns:
            The newly created ``ApprovalRequest``.
        """
        action_str = action.value if hasattr(action, "value") else str(action)
        resource_str = resource.value if hasattr(resource, "value") else str(resource)
        now = time.time()
        timeout = timeout_seconds if timeout_seconds is not None else self._timeout

        req = ApprovalRequest(
            action=action_str,
            resource=resource_str,
            requester=requester,
            approvers=list(required_approvers or []),
            status=ApprovalStatus.PENDING,
            created_at=now,
            expires_at=now + timeout,
            context=dict(context or {}),
        )

        self._requests[req.id] = req
        self._audit_event("submit", req)

        # Attempt RBAC auto-approval
        if self._enforcer is not None:
            try:
                permitted = self._enforcer.check_permission(
                    requester,
                    "approve",
                    resource_str,
                    raise_on_deny=False,
                )
            except Exception:  # pragma: no cover — defensive
                permitted = False

            if permitted:
                req.status = ApprovalStatus.APPROVED
                req.auto_approved = True
                req.decisions.append(
                    ApprovalDecision(
                        approver="__rbac_auto_approve__",
                        decision=ApprovalStatus.APPROVED,
                        reason=(
                            f"Requester '{requester}' holds approve permission "
                            f"on '{resource_str}' — auto-approved by RBAC."
                        ),
                    )
                )
                self._audit_event("auto_approve", req)

        return req

    # ------------------------------------------------------------------
    # Approve / Reject
    # ------------------------------------------------------------------

    def approve(
        self,
        request_id: str,
        approver: str,
        reason: str = "",
    ) -> ApprovalRequest:
        """Record an approval decision on the specified request.

        Args:
            request_id: UUID of the ``ApprovalRequest``.
            approver:   Identity of the approving user.
            reason:     Optional free-text rationale.

        Returns:
            The updated ``ApprovalRequest``.

        Raises:
            KeyError:      If *request_id* does not exist.
            ValueError:    If the request is already resolved (including expired).
        """
        req = self._get_and_validate(request_id, approver, operation="approve")

        req.decisions.append(
            ApprovalDecision(
                approver=approver,
                decision=ApprovalStatus.APPROVED,
                reason=reason,
            )
        )

        # Resolve immediately if no specific approver list, or all required
        # approvers have approved.
        if self._quorum_reached(req):
            req.status = ApprovalStatus.APPROVED
            self._audit_event("approve", req, extra={"approver": approver})

        return req

    def reject(
        self,
        request_id: str,
        approver: str,
        reason: str,
    ) -> ApprovalRequest:
        """Record a rejection decision on the specified request.

        A single rejection is sufficient to transition the request to
        ``REJECTED`` — unanimous approval is required; any veto blocks.

        Args:
            request_id: UUID of the ``ApprovalRequest``.
            approver:   Identity of the rejecting user.
            reason:     Mandatory rationale for audit trail.

        Returns:
            The updated ``ApprovalRequest``.

        Raises:
            KeyError:   If *request_id* does not exist.
            ValueError: If the request is already resolved or reason is empty.
        """
        if not reason or not reason.strip():
            raise ValueError("Rejection reason cannot be empty.")

        req = self._get_and_validate(request_id, approver, operation="reject")

        req.decisions.append(
            ApprovalDecision(
                approver=approver,
                decision=ApprovalStatus.REJECTED,
                reason=reason,
            )
        )
        req.status = ApprovalStatus.REJECTED
        self._audit_event("reject", req, extra={"approver": approver, "reason": reason})
        return req

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def get_request(self, request_id: str) -> ApprovalRequest:
        """Return an ``ApprovalRequest`` by ID, expiring it if past deadline.

        Args:
            request_id: UUID of the request.

        Returns:
            The ``ApprovalRequest`` (status may be updated to EXPIRED).

        Raises:
            KeyError: If *request_id* does not exist.
        """
        req = self._requests.get(request_id)
        if req is None:
            raise KeyError(f"No approval request with id '{request_id}'.")
        self._maybe_expire(req)
        return req

    def list_pending(self) -> list[ApprovalRequest]:
        """Return all non-expired pending requests, expiring stale ones."""
        results: list[ApprovalRequest] = []
        for req in list(self._requests.values()):
            self._maybe_expire(req)
            if req.status == ApprovalStatus.PENDING:
                results.append(req)
        return sorted(results, key=lambda r: r.created_at)

    def list_all(self) -> list[ApprovalRequest]:
        """Return all requests regardless of status."""
        for req in list(self._requests.values()):
            self._maybe_expire(req)
        return sorted(self._requests.values(), key=lambda r: r.created_at)

    def purge_resolved(self) -> int:
        """Remove all resolved requests from the in-memory store.

        Returns:
            Number of requests removed.
        """
        resolved_ids = [rid for rid, r in self._requests.items() if r.is_resolved]
        for rid in resolved_ids:
            del self._requests[rid]
        return len(resolved_ids)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_and_validate(
        self,
        request_id: str,
        actor: str,
        operation: str,
    ) -> ApprovalRequest:
        """Fetch a request and validate it can still be acted upon."""
        req = self._requests.get(request_id)
        if req is None:
            raise KeyError(f"No approval request with id '{request_id}'.")

        self._maybe_expire(req)

        if req.is_resolved:
            raise ValueError(
                f"Request '{request_id}' is already resolved "
                f"(status={req.status.value}); cannot perform '{operation}'."
            )

        # Validate actor permission for reject operations
        if operation == "reject" and req.approvers and actor not in req.approvers:
            raise PermissionError(
                f"Actor '{actor}' is not authorized to reject this request. "
                f"Required approvers: {', '.join(req.approvers)}"
            )

        return req

    def _maybe_expire(self, req: ApprovalRequest) -> None:
        """Transition *req* to EXPIRED if the deadline has passed."""
        if req.status == ApprovalStatus.PENDING and req.is_expired:
            req.status = ApprovalStatus.EXPIRED
            actual_timeout = req.expires_at - req.created_at
            req.decisions.append(
                ApprovalDecision(
                    approver="__system__",
                    decision=ApprovalStatus.EXPIRED,
                    reason=(f"Request expired after {actual_timeout:.0f}s without resolution."),
                )
            )
            self._audit_event("expire", req)

    def _quorum_reached(self, req: ApprovalRequest) -> bool:
        """Return True if sufficient approvals have been collected.

        If ``req.approvers`` is empty, a single approval suffices.
        Otherwise, all named approvers must have approved.
        """
        if not req.approvers:
            # Any one approval resolves it
            return any(d.decision == ApprovalStatus.APPROVED for d in req.decisions)

        approved_by = {d.approver for d in req.decisions if d.decision == ApprovalStatus.APPROVED}
        required = set(req.approvers)
        return required.issubset(approved_by)

    def _audit_event(
        self,
        event: str,
        req: ApprovalRequest,
        extra: dict[str, object] | None = None,
    ) -> None:
        """Write an audit record to the AuditLogger."""
        key = f"approval:{event}:{req.id}:{time.time()}"
        payload: dict[str, object] = {
            "event": event,
            "request_id": req.id,
            "action": req.action,
            "resource": req.resource,
            "requester": req.requester,
            "status": req.status.value,
        }
        if extra:
            payload.update(extra)
        self._audit._data[key] = payload
