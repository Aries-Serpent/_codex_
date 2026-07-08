"""
Cognitive Brain - Objective Adjuster Module (Plan 3 Phase 3.2)

This module implements the Objective Adjustment Logic for autonomous
objective management based on metric analysis.

Features:
- Adjustment rules engine
- Priority management
- Objective queue management
- Adjustment constraints
"""

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from .objective_analyzer import (
    AlertSeverity,
    HealthReport,
    MetricType,
    ObjectiveAnalyzer,
    TrendDirection,
    create_analyzer,
)


class AdjustmentType(Enum):
    """Types of objective adjustments."""

    PRIORITY_INCREASE = "priority_increase"
    PRIORITY_DECREASE = "priority_decrease"
    ADD_OBJECTIVE = "add_objective"
    REMOVE_OBJECTIVE = "remove_objective"
    MODIFY_TARGET = "modify_target"
    PAUSE_OBJECTIVE = "pause_objective"
    RESUME_OBJECTIVE = "resume_objective"


class AdjustmentTrigger(Enum):
    """Triggers that can cause adjustments."""

    THRESHOLD_BREACH = "threshold_breach"
    TREND_DEGRADATION = "trend_degradation"
    TREND_IMPROVEMENT = "trend_improvement"
    SUSTAINED_EXCELLENCE = "sustained_excellence"
    ANOMALY_DETECTED = "anomaly_detected"
    MANUAL_REQUEST = "manual_request"
    SCHEDULED = "scheduled"


class ObjectivePriority(Enum):
    """Priority levels for objectives."""

    P0_CRITICAL = 0  # Security issues, blocking problems
    P1_HIGH = 1  # Core functionality, major bugs
    P2_MEDIUM = 2  # Improvements, non-blocking issues
    P3_LOW = 3  # Nice-to-have, optimizations
    P4_BACKLOG = 4  # Future consideration


@dataclass
class Objective:
    """A single objective in the system."""

    id: str
    title: str
    description: str
    priority: ObjectivePriority
    metric_type: MetricType | None
    target_value: float | None
    current_value: float | None
    status: str  # active, paused, completed, cancelled
    created_at: datetime
    updated_at: datetime
    deadline: datetime | None = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "metric_type": self.metric_type.value if self.metric_type else None,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Objective":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            priority=ObjectivePriority(data["priority"]),
            metric_type=MetricType(data["metric_type"]) if data.get("metric_type") else None,
            target_value=data.get("target_value"),
            current_value=data.get("current_value"),
            status=data["status"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            tags=data.get("tags", []),
        )


@dataclass
class AdjustmentRule:
    """A rule that defines when and how to adjust objectives."""

    id: str
    name: str
    trigger: AdjustmentTrigger
    condition: Callable[[HealthReport], bool]
    action: AdjustmentType
    parameters: dict[str, Any]
    priority: int = 0  # Higher priority rules evaluated first
    enabled: bool = True
    cooldown_hours: int = 24  # Minimum hours between applications
    last_applied: datetime | None = None

    def can_apply(self) -> bool:
        """Check if rule can be applied (respects cooldown)."""
        if not self.enabled:
            return False
        if self.last_applied is None:
            return True
        cooldown = timedelta(hours=self.cooldown_hours)
        return datetime.now(timezone.utc) - self.last_applied >= cooldown

    def check_condition(self, report: HealthReport) -> bool:
        """Check if the rule's condition is met."""
        if not self.can_apply():
            return False
        try:
            return self.condition(report)
        except Exception:
            return False


@dataclass
class Adjustment:
    """A proposed or applied adjustment."""

    id: str
    rule_id: str
    type: AdjustmentType
    objective_id: str | None
    description: str
    parameters: dict[str, Any]
    status: str  # proposed, approved, applied, rejected, rolled_back
    proposed_at: datetime
    applied_at: datetime | None = None
    applied_by: str | None = None  # "autonomous" or user identifier

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "type": self.type.value,
            "objective_id": self.objective_id,
            "description": self.description,
            "parameters": self.parameters,
            "status": self.status,
            "proposed_at": self.proposed_at.isoformat(),
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "applied_by": self.applied_by,
        }


class ObjectiveStore:
    """Persistent storage for objectives."""

    def __init__(self, store_path: Path | None = None):
        """Initialize the objective store."""
        if store_path is None:
            store_path = Path(".codex/cognitive_brain/objective_store.json")
        self.store_path = store_path
        self._objectives: dict[str, dict[str, Any]] = {}
        self._adjustments: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Load from file."""
        if self.store_path.exists():
            try:
                with open(self.store_path) as f:
                    data = json.load(f)
                    self._objectives = data.get("objectives", {})
                    self._adjustments = data.get("adjustments", [])
            except (OSError, json.JSONDecodeError):
                self._objectives = {}
                self._adjustments = []

    def _save(self) -> None:
        """Save to file."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.store_path, "w") as f:
            json.dump(
                {"objectives": self._objectives, "adjustments": self._adjustments},
                f,
                indent=2,
            )

    def add_objective(self, objective: Objective) -> None:
        """Add or update an objective."""
        self._objectives[objective.id] = objective.to_dict()
        self._save()

    def get_objective(self, objective_id: str) -> Objective | None:
        """Get an objective by ID."""
        data = self._objectives.get(objective_id)
        return Objective.from_dict(data) if data else None

    def get_all_objectives(self, status: str | None = None) -> list[Objective]:
        """Get all objectives, optionally filtered by status."""
        objectives = [Objective.from_dict(d) for d in self._objectives.values()]
        if status:
            objectives = [o for o in objectives if o.status == status]
        return sorted(objectives, key=lambda o: (o.priority.value, o.created_at))

    def remove_objective(self, objective_id: str) -> bool:
        """Remove an objective."""
        if objective_id in self._objectives:
            del self._objectives[objective_id]
            self._save()
            return True
        return False

    def add_adjustment(self, adjustment: Adjustment) -> None:
        """Add an adjustment record."""
        self._adjustments.append(adjustment.to_dict())
        # Keep only last 1000 adjustments
        if len(self._adjustments) > 1000:
            self._adjustments = self._adjustments[-1000:]
        self._save()

    def get_adjustments(self, limit: int = 100) -> list[Adjustment]:
        """Get recent adjustments."""
        return [
            Adjustment(
                id=d["id"],
                rule_id=d["rule_id"],
                type=AdjustmentType(d["type"]),
                objective_id=d.get("objective_id"),
                description=d["description"],
                parameters=d["parameters"],
                status=d["status"],
                proposed_at=datetime.fromisoformat(d["proposed_at"]),
                applied_at=datetime.fromisoformat(d["applied_at"]) if d.get("applied_at") else None,
                applied_by=d.get("applied_by"),
            )
            for d in self._adjustments[-limit:]
        ]


class ObjectiveAdjuster:
    """
    Main class for managing and adjusting objectives based on metrics.

    This is the core component of Plan 3 Phase 3.2: Objective Adjustment Logic.
    """

    def __init__(
        self,
        analyzer: ObjectiveAnalyzer | None = None,
        store: ObjectiveStore | None = None,
    ):
        """Initialize the objective adjuster."""
        self.analyzer = analyzer or create_analyzer()
        self.store = store or ObjectiveStore()
        self.rules: list[AdjustmentRule] = []
        self._setup_default_rules()
        self._adjustment_counter = 0

    def _setup_default_rules(self) -> None:
        """Set up the default adjustment rules."""
        # Rule: Coverage below target
        self.rules.append(
            AdjustmentRule(
                id="coverage_below_target",
                name="Coverage Below Target",
                trigger=AdjustmentTrigger.THRESHOLD_BREACH,
                condition=lambda r: any(a.metric_type == MetricType.COVERAGE for a in r.alerts),
                action=AdjustmentType.ADD_OBJECTIVE,
                parameters={
                    "objective_template": {
                        "title": "Coverage Sprint",
                        "description": "Increase test coverage to meet target",
                        "priority": ObjectivePriority.P1_HIGH.value,
                        "metric_type": MetricType.COVERAGE.value,
                        "tags": ["coverage", "sprint", "auto-generated"],
                    }
                },
                priority=10,
            )
        )

        # Rule: Security regression
        self.rules.append(
            AdjustmentRule(
                id="security_regression",
                name="Security Regression",
                trigger=AdjustmentTrigger.THRESHOLD_BREACH,
                condition=lambda r: any(
                    a.metric_type == MetricType.SECURITY and a.severity == AlertSeverity.CRITICAL
                    for a in r.alerts
                ),
                action=AdjustmentType.ADD_OBJECTIVE,
                parameters={
                    "objective_template": {
                        "title": "Security Remediation",
                        "description": "Address security vulnerabilities immediately",
                        "priority": ObjectivePriority.P0_CRITICAL.value,
                        "metric_type": MetricType.SECURITY.value,
                        "tags": ["security", "critical", "auto-generated"],
                    }
                },
                priority=100,  # Highest priority
            )
        )

        # Rule: CI/CD degradation
        self.rules.append(
            AdjustmentRule(
                id="ci_degradation",
                name="CI/CD Degradation",
                trigger=AdjustmentTrigger.TREND_DEGRADATION,
                condition=lambda r: any(
                    t.metric_type == MetricType.CI_CD
                    and t.direction == TrendDirection.DEGRADING
                    and t.change_percent < -5
                    for t in r.trends
                ),
                action=AdjustmentType.ADD_OBJECTIVE,
                parameters={
                    "objective_template": {
                        "title": "CI Health Sprint",
                        "description": "Improve CI/CD pass rate",
                        "priority": ObjectivePriority.P1_HIGH.value,
                        "metric_type": MetricType.CI_CD.value,
                        "tags": ["ci-cd", "sprint", "auto-generated"],
                    }
                },
                priority=20,
            )
        )

        # Rule: Sustained excellence
        self.rules.append(
            AdjustmentRule(
                id="sustained_excellence",
                name="Sustained Excellence",
                trigger=AdjustmentTrigger.SUSTAINED_EXCELLENCE,
                condition=lambda r: (
                    r.overall_status == "healthy"
                    and len(r.alerts) == 0
                    and all(t.direction != TrendDirection.DEGRADING for t in r.trends)
                ),
                action=AdjustmentType.MODIFY_TARGET,
                parameters={
                    "target_increase_percent": 5,
                    "message": "All metrics healthy - raising targets",
                },
                priority=1,
                cooldown_hours=168,  # Once per week
            )
        )

    def add_rule(self, rule: AdjustmentRule) -> None:
        """Add a custom adjustment rule."""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: -r.priority)

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID."""
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                del self.rules[i]
                return True
        return False

    def evaluate_rules(self) -> list[Adjustment]:
        """
        Evaluate all rules against current health report.

        Returns list of proposed adjustments.
        """
        report = self.analyzer.generate_health_report()
        proposed: list[Adjustment] = []

        for rule in sorted(self.rules, key=lambda r: -r.priority):
            if rule.check_condition(report):
                adjustment = self._create_adjustment(rule)
                proposed.append(adjustment)

        return proposed

    def _create_adjustment(self, rule: AdjustmentRule) -> Adjustment:
        """Create an adjustment from a rule."""
        self._adjustment_counter += 1
        adjustment_id = f"ADJ-{self._adjustment_counter:05d}"

        return Adjustment(
            id=adjustment_id,
            rule_id=rule.id,
            type=rule.action,
            objective_id=None,  # Set when applied
            description=f"Triggered by rule: {rule.name}",
            parameters=rule.parameters.copy(),
            status="proposed",
            proposed_at=datetime.now(timezone.utc),
        )

    def apply_adjustment(
        self, adjustment: Adjustment, applied_by: str = "autonomous"
    ) -> Objective | None:
        """
        Apply an adjustment.

        Returns the affected objective if applicable.
        """
        now = datetime.now(timezone.utc)

        if adjustment.type == AdjustmentType.ADD_OBJECTIVE:
            objective = self._create_objective_from_template(
                adjustment.parameters.get("objective_template", {})
            )
            self.store.add_objective(objective)
            adjustment.objective_id = objective.id
            adjustment.status = "applied"
            adjustment.applied_at = now
            adjustment.applied_by = applied_by
            self.store.add_adjustment(adjustment)

            # Update rule's last_applied
            for rule in self.rules:
                if rule.id == adjustment.rule_id:
                    rule.last_applied = now
                    break

            return objective

        if adjustment.type == AdjustmentType.PRIORITY_INCREASE:
            objective_id = adjustment.parameters.get("objective_id")
            if objective_id:
                objective = self.store.get_objective(objective_id)  # type: ignore[assignment]
                if objective and objective.priority.value > 0:
                    objective.priority = ObjectivePriority(objective.priority.value - 1)
                    objective.updated_at = now
                    self.store.add_objective(objective)
                    adjustment.objective_id = objective.id
                    adjustment.status = "applied"
                    adjustment.applied_at = now
                    adjustment.applied_by = applied_by
                    self.store.add_adjustment(adjustment)
                    return objective

        elif adjustment.type == AdjustmentType.PAUSE_OBJECTIVE:
            objective_id = adjustment.parameters.get("objective_id")
            if objective_id:
                objective = self.store.get_objective(objective_id)  # type: ignore[assignment]
                if objective:
                    objective.status = "paused"
                    objective.updated_at = now
                    self.store.add_objective(objective)
                    adjustment.objective_id = objective.id
                    adjustment.status = "applied"
                    adjustment.applied_at = now
                    adjustment.applied_by = applied_by
                    self.store.add_adjustment(adjustment)
                    return objective

        return None

    def _create_objective_from_template(self, template: dict[str, Any]) -> Objective:
        """Create an objective from a template."""
        now = datetime.now(timezone.utc)
        objective_id = f"OBJ-{int(now.timestamp())}"

        return Objective(
            id=objective_id,
            title=template.get("title", "Untitled Objective"),
            description=template.get("description", ""),
            priority=ObjectivePriority(template.get("priority", 2)),
            metric_type=(
                MetricType(template["metric_type"]) if template.get("metric_type") else None
            ),
            target_value=template.get("target_value"),
            current_value=template.get("current_value"),
            status="active",
            created_at=now,
            updated_at=now,
            deadline=None,
            tags=template.get("tags", []),
        )

    def get_active_objectives(self) -> list[Objective]:
        """Get all active objectives sorted by priority."""
        return self.store.get_all_objectives(status="active")

    def complete_objective(self, objective_id: str) -> bool:
        """Mark an objective as completed."""
        objective = self.store.get_objective(objective_id)
        if objective:
            objective.status = "completed"
            objective.updated_at = datetime.now(timezone.utc)
            self.store.add_objective(objective)
            return True
        return False

    def create_objective(
        self,
        title: str,
        description: str,
        priority: ObjectivePriority = ObjectivePriority.P2_MEDIUM,
        metric_type: MetricType | None = None,
        target_value: float | None = None,
        tags: list[str] | None = None,
    ) -> Objective:
        """Manually create a new objective."""
        now = datetime.now(timezone.utc)
        objective = Objective(
            id=f"OBJ-{int(now.timestamp())}",
            title=title,
            description=description,
            priority=priority,
            metric_type=metric_type,
            target_value=target_value,
            current_value=None,
            status="active",
            created_at=now,
            updated_at=now,
            tags=tags or [],
        )
        self.store.add_objective(objective)
        return objective

    def get_adjustment_summary(self) -> dict[str, Any]:
        """Get a summary of recent adjustments."""
        adjustments = self.store.get_adjustments(limit=50)

        by_status: dict[str, Any] = {}
        by_type: dict[str, Any] = {}

        for adj in adjustments:
            by_status[adj.status] = by_status.get(adj.status, 0) + 1
            by_type[adj.type.value] = by_type.get(adj.type.value, 0) + 1

        return {
            "total_adjustments": len(adjustments),
            "by_status": by_status,
            "by_type": by_type,
            "recent": [a.to_dict() for a in adjustments[-5:]],
        }


def create_adjuster() -> ObjectiveAdjuster:
    """Factory function to create an ObjectiveAdjuster."""
    return ObjectiveAdjuster()


# Convenience functions
def evaluate_and_propose() -> list[Adjustment]:
    """Evaluate rules and return proposed adjustments."""
    adjuster = create_adjuster()
    return adjuster.evaluate_rules()


def get_active_objectives() -> list[Objective]:
    """Get all active objectives."""
    adjuster = create_adjuster()
    return adjuster.get_active_objectives()


def create_sprint_objective(
    metric_type: MetricType, target_value: float, title: str | None = None
) -> Objective:
    """Create a sprint objective for a metric."""
    adjuster = create_adjuster()
    return adjuster.create_objective(
        title=title or f"{metric_type.value.title()} Sprint",
        description=f"Improve {metric_type.value} to reach target of {target_value}",
        priority=ObjectivePriority.P1_HIGH,
        metric_type=metric_type,
        target_value=target_value,
        tags=["sprint", "auto-generated"],
    )
