"""
Cognitive Brain - Autonomous Executor Module (Plan 3 Phase 3.3)

This module implements autonomous execution capabilities for objective
adjustments with multiple automation levels.

Automation Levels:
- Level 1 (Advisory): Recommend adjustments, await human approval
- Level 2 (Semi-autonomous): Auto-adjust minor items, human approval for major
- Level 3 (Fully autonomous): Full authority within guardrails

Default: Level 2 (Semi-autonomous)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from .objective_adjuster import (
    Adjustment,
    AdjustmentType,
    Objective,
    ObjectiveAdjuster,
    create_adjuster,
)


class AutomationLevel(Enum):
    """Levels of automation for objective adjustments."""

    LEVEL_1_ADVISORY = 1
    LEVEL_2_SEMI_AUTONOMOUS = 2
    LEVEL_3_FULLY_AUTONOMOUS = 3


class ApprovalStatus(Enum):
    """Status of approval for an adjustment."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """A request for approval of an adjustment."""

    id: str
    adjustment: Adjustment
    automation_level: AutomationLevel
    status: ApprovalStatus
    reason: str
    created_at: datetime
    expires_at: datetime | None
    approved_by: str | None = None
    approved_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "adjustment": self.adjustment.to_dict(),
            "automation_level": self.automation_level.value,
            "status": self.status.value,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }


@dataclass
class ExecutionResult:
    """Result of executing an adjustment."""

    success: bool
    adjustment_id: str
    objective: Objective | None
    message: str
    executed_at: datetime
    automation_level: AutomationLevel
    required_approval: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "adjustment_id": self.adjustment_id,
            "objective_id": self.objective.id if self.objective else None,
            "message": self.message,
            "executed_at": self.executed_at.isoformat(),
            "automation_level": self.automation_level.value,
            "required_approval": self.required_approval,
        }


class ExecutionPolicy:
    """Policy that determines what can be auto-executed."""

    def __init__(
        self,
        automation_level: AutomationLevel = AutomationLevel.LEVEL_2_SEMI_AUTONOMOUS,
    ):
        """Initialize the execution policy."""
        self.automation_level = automation_level

        # Define what's auto-approvable at each level
        self._level_2_auto_approve = {
            AdjustmentType.PRIORITY_INCREASE,
            AdjustmentType.PRIORITY_DECREASE,
            AdjustmentType.PAUSE_OBJECTIVE,
            AdjustmentType.RESUME_OBJECTIVE,
        }

        self._level_2_require_approval = {
            AdjustmentType.ADD_OBJECTIVE,
            AdjustmentType.REMOVE_OBJECTIVE,
            AdjustmentType.MODIFY_TARGET,
        }

        # Thresholds for auto-approval
        self.max_priority_change = 1  # Can only change priority by 1 level
        self.max_objectives_per_day = 3  # Max auto-created objectives per day

    def can_auto_execute(self, adjustment: Adjustment) -> tuple[bool, str]:
        """
        Check if an adjustment can be auto-executed.

        Returns (can_execute, reason)
        """
        if self.automation_level == AutomationLevel.LEVEL_1_ADVISORY:
            return False, "Advisory mode - all adjustments require approval"

        if self.automation_level == AutomationLevel.LEVEL_3_FULLY_AUTONOMOUS:
            return True, "Fully autonomous mode - auto-executing"

        # Level 2: Semi-autonomous
        if adjustment.type in self._level_2_auto_approve:
            return (
                True,
                f"{adjustment.type.value} is auto-approvable in semi-autonomous mode",
            )

        if adjustment.type in self._level_2_require_approval:
            return (
                False,
                f"{adjustment.type.value} requires approval in semi-autonomous mode",
            )

        return False, "Unknown adjustment type"

    def get_approval_timeout_hours(self, adjustment: Adjustment) -> int:
        """Get the timeout for approval in hours."""
        if adjustment.type == AdjustmentType.ADD_OBJECTIVE:
            # Critical objectives need faster approval
            template = adjustment.parameters.get("objective_template", {})
            priority = template.get("priority", 2)
            if priority == 0:  # P0 Critical
                return 4
            if priority == 1:  # P1 High
                return 24
            return 72
        return 48  # Default 48 hours


class AutonomousExecutor:
    """
    Main class for autonomous execution of objective adjustments.

    This is the core component of Plan 3 Phase 3.3: Autonomous Execution.
    """

    def __init__(
        self,
        adjuster: ObjectiveAdjuster | None = None,
        policy: ExecutionPolicy | None = None,
    ):
        """Initialize the autonomous executor."""
        self.adjuster = adjuster or create_adjuster()
        self.policy = policy or ExecutionPolicy()
        self._pending_approvals: dict[str, ApprovalRequest] = {}
        self._execution_history: list[ExecutionResult] = []
        self._approval_counter = 0

    @property
    def automation_level(self) -> AutomationLevel:
        """Get the current automation level."""
        return self.policy.automation_level

    @automation_level.setter
    def automation_level(self, level: AutomationLevel) -> None:
        """Set the automation level."""
        self.policy.automation_level = level

    def process_adjustments(
        self, adjustments: list[Adjustment] | None = None
    ) -> list[ExecutionResult]:
        """
        Process a list of adjustments according to the automation policy.

        If no adjustments provided, evaluates rules automatically.
        """
        if adjustments is None:
            adjustments = self.adjuster.evaluate_rules()

        results: list[ExecutionResult] = []

        for adjustment in adjustments:
            result = self._process_single_adjustment(adjustment)
            results.append(result)
            self._execution_history.append(result)

        return results

    def _process_single_adjustment(self, adjustment: Adjustment) -> ExecutionResult:
        """Process a single adjustment."""
        now = datetime.now(timezone.utc)

        can_auto, reason = self.policy.can_auto_execute(adjustment)

        if can_auto:
            # Auto-execute
            objective = self.adjuster.apply_adjustment(adjustment, "autonomous")
            return ExecutionResult(
                success=objective is not None,
                adjustment_id=adjustment.id,
                objective=objective,
                message=f"Auto-executed: {reason}",
                executed_at=now,
                automation_level=self.automation_level,
                required_approval=False,
            )
        # Request approval
        approval = self._create_approval_request(adjustment, reason)
        self._pending_approvals[approval.id] = approval

        return ExecutionResult(
            success=False,
            adjustment_id=adjustment.id,
            objective=None,
            message=f"Awaiting approval: {reason}. Request ID: {approval.id}",
            executed_at=now,
            automation_level=self.automation_level,
            required_approval=True,
        )

    def _create_approval_request(self, adjustment: Adjustment, reason: str) -> ApprovalRequest:
        """Create an approval request."""
        self._approval_counter += 1
        now = datetime.now(timezone.utc)
        timeout_hours = self.policy.get_approval_timeout_hours(adjustment)

        expires_at = now + timedelta(hours=timeout_hours)

        return ApprovalRequest(
            id=f"APR-{self._approval_counter:05d}",
            adjustment=adjustment,
            automation_level=self.automation_level,
            status=ApprovalStatus.PENDING,
            reason=reason,
            created_at=now,
            expires_at=expires_at,
        )

    def approve(self, request_id: str, approved_by: str) -> ExecutionResult | None:
        """Approve a pending request."""
        if request_id not in self._pending_approvals:
            return None

        request = self._pending_approvals[request_id]
        now = datetime.now(timezone.utc)

        # Check if expired
        if request.expires_at and now > request.expires_at:
            request.status = ApprovalStatus.EXPIRED
            return ExecutionResult(
                success=False,
                adjustment_id=request.adjustment.id,
                objective=None,
                message="Approval request expired",
                executed_at=now,
                automation_level=self.automation_level,
                required_approval=True,
            )

        # Approve and execute
        request.status = ApprovalStatus.APPROVED
        request.approved_by = approved_by
        request.approved_at = now

        objective = self.adjuster.apply_adjustment(request.adjustment, approved_by)

        del self._pending_approvals[request_id]

        result = ExecutionResult(
            success=objective is not None,
            adjustment_id=request.adjustment.id,
            objective=objective,
            message=f"Approved by {approved_by} and executed",
            executed_at=now,
            automation_level=self.automation_level,
            required_approval=True,
        )
        self._execution_history.append(result)
        return result

    def reject(self, request_id: str, rejected_by: str) -> bool:
        """Reject a pending request."""
        if request_id not in self._pending_approvals:
            return False

        request = self._pending_approvals[request_id]
        request.status = ApprovalStatus.REJECTED
        request.approved_by = rejected_by  # Record who rejected
        request.approved_at = datetime.now(timezone.utc)

        del self._pending_approvals[request_id]
        return True

    def get_pending_approvals(self) -> list[ApprovalRequest]:
        """Get all pending approval requests."""
        now = datetime.now(timezone.utc)

        # Check for expired requests
        expired = []
        for request_id, request in self._pending_approvals.items():
            if request.expires_at and now > request.expires_at:
                request.status = ApprovalStatus.EXPIRED
                expired.append(request_id)

        # Remove expired requests
        for request_id in expired:
            del self._pending_approvals[request_id]

        return list(self._pending_approvals.values())

    def get_execution_history(self, limit: int = 50) -> list[ExecutionResult]:
        """Get recent execution history."""
        return self._execution_history[-limit:]

    def run_evaluation_cycle(self) -> dict[str, Any]:
        """
        Run a complete evaluation cycle.

        Returns a summary of actions taken.
        """
        # Evaluate rules
        adjustments = self.adjuster.evaluate_rules()

        if not adjustments:
            return {
                "cycle_time": datetime.now(timezone.utc).isoformat(),
                "adjustments_proposed": 0,
                "adjustments_executed": 0,
                "approvals_pending": len(self._pending_approvals),
                "message": "No adjustments triggered",
            }

        # Process adjustments
        results = self.process_adjustments(adjustments)

        executed = sum(1 for r in results if r.success)
        pending = sum(1 for r in results if r.required_approval and not r.success)

        return {
            "cycle_time": datetime.now(timezone.utc).isoformat(),
            "adjustments_proposed": len(adjustments),
            "adjustments_executed": executed,
            "adjustments_pending_approval": pending,
            "approvals_pending": len(self._pending_approvals),
            "results": [r.to_dict() for r in results],
        }

    def get_status(self) -> dict[str, Any]:
        """Get the current executor status."""
        return {
            "automation_level": self.automation_level.name,
            "pending_approvals": len(self._pending_approvals),
            "execution_count": len(self._execution_history),
            "active_objectives": len(self.adjuster.get_active_objectives()),
            "policy": {
                "max_priority_change": self.policy.max_priority_change,
                "max_objectives_per_day": self.policy.max_objectives_per_day,
            },
        }


def create_executor(
    automation_level: AutomationLevel = AutomationLevel.LEVEL_2_SEMI_AUTONOMOUS,
) -> AutonomousExecutor:
    """Factory function to create an AutonomousExecutor."""
    policy = ExecutionPolicy(automation_level)
    return AutonomousExecutor(policy=policy)


# Convenience functions
def run_advisory_mode() -> dict[str, Any]:
    """Run in advisory mode (Level 1)."""
    executor = create_executor(AutomationLevel.LEVEL_1_ADVISORY)
    return executor.run_evaluation_cycle()


def run_semi_autonomous() -> dict[str, Any]:
    """Run in semi-autonomous mode (Level 2)."""
    executor = create_executor(AutomationLevel.LEVEL_2_SEMI_AUTONOMOUS)
    return executor.run_evaluation_cycle()


def run_fully_autonomous() -> dict[str, Any]:
    """Run in fully autonomous mode (Level 3)."""
    executor = create_executor(AutomationLevel.LEVEL_3_FULLY_AUTONOMOUS)
    return executor.run_evaluation_cycle()
