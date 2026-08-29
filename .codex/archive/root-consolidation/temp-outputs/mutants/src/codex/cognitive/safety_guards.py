"""
Cognitive Brain - Safety Guards Module (Plan 3 Phase 3.4)

This module implements safety mechanisms and governance for autonomous
objective adjustments.

Safety Mechanisms:
- Adjustment audit log
- Rollback capability
- Human override priority
- Rate limiting
- Scope restrictions

Governance:
- Weekly adjustment review
- Monthly objective audit
- Quarterly goal alignment
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from .objective_adjuster import (
    Adjustment,
    AdjustmentType,
)


class AuditEventType(Enum):
    """Types of audit events."""

    ADJUSTMENT_PROPOSED = "adjustment_proposed"
    ADJUSTMENT_APPROVED = "adjustment_approved"
    ADJUSTMENT_REJECTED = "adjustment_rejected"
    ADJUSTMENT_EXECUTED = "adjustment_executed"
    ADJUSTMENT_ROLLED_BACK = "adjustment_rolled_back"
    OBJECTIVE_CREATED = "objective_created"
    OBJECTIVE_COMPLETED = "objective_completed"
    OBJECTIVE_CANCELLED = "objective_cancelled"
    LEVEL_CHANGED = "level_changed"
    OVERRIDE_APPLIED = "override_applied"
    RATE_LIMIT_HIT = "rate_limit_hit"
    SCOPE_VIOLATION = "scope_violation"


class OverrideType(Enum):
    """Types of human overrides."""

    PAUSE_AUTOMATION = "pause_automation"
    RESUME_AUTOMATION = "resume_automation"
    FORCE_ADJUSTMENT = "force_adjustment"
    BLOCK_RULE = "block_rule"
    UNBLOCK_RULE = "unblock_rule"
    RESET_RATE_LIMITS = "reset_rate_limits"


@dataclass
class AuditEvent:
    """An audit event for tracking changes."""

    id: str
    event_type: AuditEventType
    timestamp: datetime
    actor: str  # "autonomous" or user identifier
    details: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "actor": self.actor,
            "details": self.details,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuditEvent":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            event_type=AuditEventType(data["event_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            actor=data["actor"],
            details=data["details"],
            context=data.get("context", {}),
        )


@dataclass
class RollbackRecord:
    """Record of a rollback action."""

    id: str
    original_adjustment_id: str
    original_state: dict[str, Any]
    rolled_back_at: datetime
    rolled_back_by: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "original_adjustment_id": self.original_adjustment_id,
            "original_state": self.original_state,
            "rolled_back_at": self.rolled_back_at.isoformat(),
            "rolled_back_by": self.rolled_back_by,
            "reason": self.reason,
        }


@dataclass
class RateLimit:
    """Rate limit configuration."""

    action_type: str
    max_count: int
    window_hours: int
    current_count: int = 0
    window_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def check_and_increment(self) -> tuple[bool, str]:
        """
        Check if action is allowed and increment counter.
        Returns (allowed, message)
        """
        now = datetime.now(timezone.utc)
        window_delta = timedelta(hours=self.window_hours)

        # Reset window if expired
        if now - self.window_start > window_delta:
            self.current_count = 0
            self.window_start = now

        # Check limit
        if self.current_count >= self.max_count:
            return (
                False,
                f"Rate limit exceeded: {self.action_type} ({self.current_count}/{self.max_count} in {self.window_hours}h)",  # noqa: E501
            )

        self.current_count += 1
        return True, f"Allowed ({self.current_count}/{self.max_count})"

    def reset(self) -> None:
        """Reset the rate limit."""
        self.current_count = 0
        self.window_start = datetime.now(timezone.utc)


@dataclass
class ScopeRestriction:
    """Restriction on what autonomous actions can affect."""

    name: str
    description: str
    blocked_metric_types: list[str] = field(default_factory=list)
    blocked_priorities: list[int] = field(default_factory=list)
    blocked_adjustment_types: list[str] = field(default_factory=list)
    blocked_rules: list[str] = field(default_factory=list)
    max_priority_change: int = 2

    def check_adjustment(self, adjustment: Adjustment) -> tuple[bool, str]:
        """
        Check if an adjustment is within scope.
        Returns (allowed, reason)
        """
        # Check adjustment type
        if adjustment.type.value in self.blocked_adjustment_types:
            return False, f"Adjustment type {adjustment.type.value} is blocked"

        # Check rule
        if adjustment.rule_id in self.blocked_rules:
            return False, f"Rule {adjustment.rule_id} is blocked"

        # Check metric type in template
        template = adjustment.parameters.get("objective_template", {})
        metric_type = template.get("metric_type")
        if metric_type and metric_type in self.blocked_metric_types:
            return False, f"Metric type {metric_type} is blocked"

        # Check priority in template
        priority = template.get("priority")
        if priority is not None and priority in self.blocked_priorities:
            return False, f"Priority {priority} is blocked"

        return True, "Within scope"


class AuditLog:
    """Persistent audit log for all autonomous actions."""

    def __init__(self, log_path: Path | None = None):
        """Initialize the audit log."""
        if log_path is None:
            log_path = Path(".codex/cognitive_brain/audit_log.json")
        self.log_path = log_path
        self._events: list[dict[str, Any]] = []
        self._event_counter = 0
        self._load()

    def _load(self) -> None:
        """Load events from file."""
        if self.log_path.exists():
            try:
                with open(self.log_path) as f:
                    data = json.load(f)
                    self._events = data.get("events", [])
                    self._event_counter = data.get("counter", 0)
            except (OSError, json.JSONDecodeError):
                self._events = []

    def _save(self) -> None:
        """Save events to file."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "w") as f:
            json.dump({"events": self._events, "counter": self._event_counter}, f, indent=2)

    def log_event(
        self,
        event_type: AuditEventType,
        actor: str,
        details: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Log an audit event."""
        self._event_counter += 1
        event = AuditEvent(
            id=f"AUD-{self._event_counter:06d}",
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            actor=actor,
            details=details,
            context=context or {},
        )
        self._events.append(event.to_dict())

        # Keep only last 10000 events
        if len(self._events) > 10000:
            self._events = self._events[-10000:]

        self._save()
        return event

    def get_events(
        self,
        event_type: AuditEventType | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Get audit events with optional filtering."""
        events = [AuditEvent.from_dict(e) for e in self._events]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if since:
            events = [e for e in events if e.timestamp >= since]

        return events[-limit:]

    def get_events_for_adjustment(self, adjustment_id: str) -> list[AuditEvent]:
        """Get all events related to a specific adjustment."""
        events = [AuditEvent.from_dict(e) for e in self._events]
        return [e for e in events if e.details.get("adjustment_id") == adjustment_id]


class SafetyGuard:
    """
    Main class for enforcing safety and governance on autonomous actions.

    This is the core component of Plan 3 Phase 3.4: Safety & Governance.
    """

    # Default rate limits
    DEFAULT_RATE_LIMITS = [
        RateLimit("objective_creation", max_count=5, window_hours=24),
        RateLimit("priority_change", max_count=10, window_hours=24),
        RateLimit("automation_level_change", max_count=2, window_hours=24),
    ]

    def __init__(
        self,
        audit_log: AuditLog | None = None,
        scope: ScopeRestriction | None = None,
        rate_limits: list[RateLimit] | None = None,
    ):
        """Initialize the safety guard."""
        self.audit_log = audit_log or AuditLog()
        self.scope = scope or ScopeRestriction(
            name="default", description="Default scope restrictions"
        )
        self.rate_limits = {r.action_type: r for r in (rate_limits or self.DEFAULT_RATE_LIMITS)}
        self._paused = False
        self._rollback_history: list[RollbackRecord] = []
        self._rollback_counter = 0

    @property
    def is_paused(self) -> bool:
        """Check if automation is paused."""
        return self._paused

    def pause_automation(self, by: str, reason: str = "") -> None:
        """Pause all automation."""
        self._paused = True
        self.audit_log.log_event(
            AuditEventType.OVERRIDE_APPLIED,
            by,
            {"override_type": OverrideType.PAUSE_AUTOMATION.value, "reason": reason},
        )

    def resume_automation(self, by: str) -> None:
        """Resume automation."""
        self._paused = False
        self.audit_log.log_event(
            AuditEventType.OVERRIDE_APPLIED,
            by,
            {"override_type": OverrideType.RESUME_AUTOMATION.value},
        )

    def block_rule(self, rule_id: str, by: str, reason: str = "") -> None:
        """Block a specific rule from executing."""
        # Use scope.blocked_rules as single source of truth
        if rule_id not in self.scope.blocked_rules:
            self.scope.blocked_rules.append(rule_id)
        self.audit_log.log_event(
            AuditEventType.OVERRIDE_APPLIED,
            by,
            {
                "override_type": OverrideType.BLOCK_RULE.value,
                "rule_id": rule_id,
                "reason": reason,
            },
        )

    def unblock_rule(self, rule_id: str, by: str) -> None:
        """Unblock a rule."""
        if rule_id in self.scope.blocked_rules:
            self.scope.blocked_rules.remove(rule_id)
        self.audit_log.log_event(
            AuditEventType.OVERRIDE_APPLIED,
            by,
            {"override_type": OverrideType.UNBLOCK_RULE.value, "rule_id": rule_id},
        )

    def check_adjustment(self, adjustment: Adjustment) -> tuple[bool, str]:
        """
        Check if an adjustment passes all safety checks.
        Returns (allowed, reason)
        """
        # Check if paused
        if self._paused:
            return False, "Automation is paused"

        # Check scope restrictions
        scope_ok, scope_reason = self.scope.check_adjustment(adjustment)
        if not scope_ok:
            self.audit_log.log_event(
                AuditEventType.SCOPE_VIOLATION,
                "system",
                {"adjustment_id": adjustment.id, "reason": scope_reason},
            )
            return False, scope_reason

        # Check rate limits
        rate_limit_type = self._get_rate_limit_type(adjustment)
        if rate_limit_type and rate_limit_type in self.rate_limits:
            limit = self.rate_limits[rate_limit_type]
            allowed, limit_reason = limit.check_and_increment()
            if not allowed:
                self.audit_log.log_event(
                    AuditEventType.RATE_LIMIT_HIT,
                    "system",
                    {
                        "adjustment_id": adjustment.id,
                        "rate_limit": rate_limit_type,
                        "reason": limit_reason,
                    },
                )
                return False, limit_reason

        return True, "All safety checks passed"

    def _get_rate_limit_type(self, adjustment: Adjustment) -> str | None:
        """Get the rate limit type for an adjustment."""
        if adjustment.type == AdjustmentType.ADD_OBJECTIVE:
            return "objective_creation"
        if adjustment.type in (
            AdjustmentType.PRIORITY_INCREASE,
            AdjustmentType.PRIORITY_DECREASE,
        ):
            return "priority_change"
        return None

    def record_rollback(
        self, adjustment_id: str, original_state: dict[str, Any], rolled_back_by: str, reason: str
    ) -> RollbackRecord:
        """Record a rollback action."""
        self._rollback_counter += 1
        record = RollbackRecord(
            id=f"RB-{self._rollback_counter:05d}",
            original_adjustment_id=adjustment_id,
            original_state=original_state,
            rolled_back_at=datetime.now(timezone.utc),
            rolled_back_by=rolled_back_by,
            reason=reason,
        )
        self._rollback_history.append(record)

        self.audit_log.log_event(
            AuditEventType.ADJUSTMENT_ROLLED_BACK,
            rolled_back_by,
            {
                "rollback_id": record.id,
                "adjustment_id": adjustment_id,
                "reason": reason,
            },
        )

        return record

    def get_rollback_history(self, limit: int = 50) -> list[RollbackRecord]:
        """Get rollback history."""
        return self._rollback_history[-limit:]

    def reset_rate_limits(self, by: str) -> None:
        """Reset all rate limits."""
        for limit in self.rate_limits.values():
            limit.reset()
        self.audit_log.log_event(
            AuditEventType.OVERRIDE_APPLIED,
            by,
            {"override_type": OverrideType.RESET_RATE_LIMITS.value},
        )

    def get_safety_status(self) -> dict[str, Any]:
        """Get the current safety status."""
        return {
            "is_paused": self._paused,
            "blocked_rules": self.scope.blocked_rules.copy(),
            "rate_limits": {
                k: {"current": v.current_count, "max": v.max_count}
                for k, v in self.rate_limits.items()
            },
            "recent_events": len(self.audit_log.get_events(limit=100)),
            "rollback_count": len(self._rollback_history),
        }

    def generate_governance_report(self, period_days: int = 7) -> dict[str, Any]:
        """Generate a governance report for the specified period."""
        since = datetime.now(timezone.utc) - timedelta(days=period_days)
        events = self.audit_log.get_events(since=since, limit=1000)

        # Count events by type
        by_type: dict[str, int] = {}
        for event in events:
            key = event.event_type.value
            by_type[key] = by_type.get(key, 0) + 1

        # Count by actor
        by_actor: dict[str, int] = {}
        for event in events:
            by_actor[event.actor] = by_actor.get(event.actor, 0) + 1

        return {
            "period_days": period_days,
            "total_events": len(events),
            "events_by_type": by_type,
            "events_by_actor": by_actor,
            "rate_limit_hits": by_type.get("rate_limit_hit", 0),
            "scope_violations": by_type.get("scope_violation", 0),
            "rollbacks": by_type.get("adjustment_rolled_back", 0),
            "overrides": by_type.get("override_applied", 0),
            "safety_status": self.get_safety_status(),
        }


def create_safety_guard() -> SafetyGuard:
    """Factory function to create a SafetyGuard."""
    return SafetyGuard()


# Convenience functions
def get_governance_report(days: int = 7) -> dict[str, Any]:
    """Get a governance report."""
    guard = create_safety_guard()
    return guard.generate_governance_report(days)


def pause_all_automation(by: str, reason: str = "") -> None:
    """Pause all automation."""
    guard = create_safety_guard()
    guard.pause_automation(by, reason)


def resume_all_automation(by: str) -> None:
    """Resume all automation."""
    guard = create_safety_guard()
    guard.resume_automation(by)
