"""Error Budget System — Enforce 99% SLO with lane-based allocation and budget enforcement.

This module implements:
- Error budget definition: 99% SLO = 3.6 days downtime/year (52,560 minutes)
- Lane-based allocation: High-risk lanes consume more budget
- Budget enforcement: If budget exhausted, revert to classical fallback
- Real-time tracking: Consume budget on incidents, recover on successful operations
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class LaneRiskProfile(str, Enum):
    """Risk profile for lanes to determine budget allocation."""

    CRITICAL = "critical"  # 40% of budget (high-complexity operations)
    HIGH = "high"  # 30% of budget
    MEDIUM = "medium"  # 20% of budget
    LOW = "low"  # 10% of budget


@dataclass
class BudgetAllocation:
    """Budget allocation for a lane."""

    lane_id: str
    risk_profile: LaneRiskProfile
    total_budget_minutes: float
    consumed_minutes: float = 0.0
    remaining_minutes: float = field(init=False)
    burn_rate_per_hour: float = 0.0  # minutes consumed per hour

    def __post_init__(self):
        """Compute remaining budget after init."""
        self.remaining_minutes = self.total_budget_minutes - self.consumed_minutes

    @property
    def budget_exhausted(self) -> bool:
        """Check if budget is exhausted."""
        return self.remaining_minutes <= 0

    @property
    def utilization_pct(self) -> float:
        """Percentage of budget consumed."""
        if self.total_budget_minutes == 0:
            return 0.0
        return (self.consumed_minutes / self.total_budget_minutes) * 100

    def consume_budget(self, duration_minutes: float) -> None:
        """Consume budget for an incident."""
        self.consumed_minutes += duration_minutes
        self.remaining_minutes = max(0, self.total_budget_minutes - self.consumed_minutes)
        logger.info(
            f"Lane {self.lane_id} consumed {duration_minutes:.2f} min. "
            f"Remaining: {self.remaining_minutes:.2f} min ({self.utilization_pct:.1f}% utilized)"
        )

    def recover_budget(self, duration_minutes: float) -> None:
        """Recover budget after successful operation (reduce consumed)."""
        self.consumed_minutes = max(0, self.consumed_minutes - duration_minutes)
        self.remaining_minutes = self.total_budget_minutes - self.consumed_minutes
        logger.info(
            f"Lane {self.lane_id} recovered {duration_minutes:.2f} min. "
            f"Remaining: {self.remaining_minutes:.2f} min ({self.utilization_pct:.1f}% utilized)"
        )


@dataclass
class BudgetIncident:
    """Record of a budget consumption event."""

    lane_id: str
    incident_type: str  # "test_failure", "timeout", "deployment_failure", etc.
    duration_minutes: float
    timestamp: datetime
    severity: str  # "critical", "high", "medium", "low"
    description: str = ""
    recovered: bool = False


@dataclass
class ErrorBudgetReport:
    """Report of error budget status."""

    timestamp: datetime
    total_budget_minutes: float
    total_consumed_minutes: float
    total_remaining_minutes: float
    overall_utilization_pct: float
    lane_allocations: Dict[str, BudgetAllocation]
    recent_incidents: List[BudgetIncident]
    burn_rate_per_hour: float
    lanes_exhausted: List[str]
    estimated_recovery_hours: Optional[float] = None


class ErrorBudgetSystem:
    """Manages error budget for 99% SLO compliance."""

    # 99% SLO = 0.99 uptime = 9.9 hours downtime per year
    # = 3.6 days downtime per year = 86400 * 3.6 minutes
    ANNUAL_BUDGET_MINUTES = 52560  # (100 - 99) * 525600 / 100

    def __init__(self):
        """Initialize error budget system with default lane allocations."""
        self.allocations: Dict[str, BudgetAllocation] = {}
        self.incidents: List[BudgetIncident] = []
        self.created_at = datetime.now(timezone.utc)
        self.year_start = datetime.now(timezone.utc).replace(month=1, day=1, hour=0, minute=0, second=0)
        self._initialize_lanes()

    def _initialize_lanes(self) -> None:
        """Initialize budget allocations for all lanes."""
        lane_configs = {
            "A": (LaneRiskProfile.CRITICAL, 0.40),
            "B": (LaneRiskProfile.CRITICAL, 0.40),
            "C": (LaneRiskProfile.HIGH, 0.30),
            "D": (LaneRiskProfile.MEDIUM, 0.20),
            "E": (LaneRiskProfile.MEDIUM, 0.20),
            "F": (LaneRiskProfile.LOW, 0.10),
            "G": (LaneRiskProfile.LOW, 0.10),
            "H": (LaneRiskProfile.HIGH, 0.30),  # SRE lane
            "I": (LaneRiskProfile.HIGH, 0.30),  # Quality gates
            "J": (LaneRiskProfile.LOW, 0.10),
            "K": (LaneRiskProfile.LOW, 0.10),
        }

        for lane_id, (risk_profile, allocation_pct) in lane_configs.items():
            budget = self.ANNUAL_BUDGET_MINUTES * allocation_pct
            self.allocations[lane_id] = BudgetAllocation(
                lane_id=lane_id,
                risk_profile=risk_profile,
                total_budget_minutes=budget,
            )
            logger.info(f"Lane {lane_id} ({risk_profile.value}): {budget:.2f} min allocated")

    def consume_budget(
        self, lane_id: str, duration_minutes: float, incident_type: str, severity: str, description: str = ""
    ) -> Tuple[bool, str]:
        """
        Consume budget for an incident.

        Args:
            lane_id: Lane identifier
            duration_minutes: Duration of incident in minutes
            incident_type: Type of incident (test_failure, timeout, etc.)
            severity: Severity level (critical, high, medium, low)
            description: Optional description of incident

        Returns:
            Tuple of (success, message)
            - If budget available: (True, "Budget consumed")
            - If budget exhausted: (False, "Budget exhausted - reverting to classical fallback")
        """
        if lane_id not in self.allocations:
            return False, f"Unknown lane: {lane_id}"

        allocation = self.allocations[lane_id]
        incident = BudgetIncident(
            lane_id=lane_id,
            incident_type=incident_type,
            duration_minutes=duration_minutes,
            timestamp=datetime.now(timezone.utc),
            severity=severity,
            description=description,
        )

        if allocation.budget_exhausted:
            incident.recovered = True  # Mark as requiring fallback
            self.incidents.append(incident)
            return False, f"Lane {lane_id} budget exhausted - reverting to classical fallback"

        allocation.consume_budget(duration_minutes)
        allocation.burn_rate_per_hour += duration_minutes / (duration_minutes / 60) if duration_minutes > 0 else 0
        self.incidents.append(incident)

        return True, f"Budget consumed: {duration_minutes:.2f} min from lane {lane_id}"

    def recover_budget(self, lane_id: str, duration_minutes: float) -> Tuple[bool, str]:
        """
        Recover budget after successful operation.

        Args:
            lane_id: Lane identifier
            duration_minutes: Duration to recover in minutes

        Returns:
            Tuple of (success, message)
        """
        if lane_id not in self.allocations:
            return False, f"Unknown lane: {lane_id}"

        allocation = self.allocations[lane_id]
        allocation.recover_budget(duration_minutes)

        return True, f"Budget recovered: {duration_minutes:.2f} min for lane {lane_id}"

    def get_budget_report(self) -> ErrorBudgetReport:
        """Generate comprehensive error budget report."""
        total_consumed = sum(alloc.consumed_minutes for alloc in self.allocations.values())
        total_budget = sum(alloc.total_budget_minutes for alloc in self.allocations.values())
        total_remaining = total_budget - total_consumed
        overall_utilization = (total_consumed / total_budget * 100) if total_budget > 0 else 0.0

        # Calculate burn rate
        time_elapsed_minutes = (datetime.now(timezone.utc) - self.created_at).total_seconds() / 60
        burn_rate_per_hour = (total_consumed / time_elapsed_minutes * 60) if time_elapsed_minutes > 0 else 0

        # Find exhausted lanes
        exhausted_lanes = [lane_id for lane_id, alloc in self.allocations.items() if alloc.budget_exhausted]

        # Estimate recovery time
        estimated_recovery_hours = None
        if burn_rate_per_hour > 0 and total_remaining < total_budget:
            recovery_rate_per_hour = -0.5  # Assume 0.5 min recovery per hour (conservative)
            if recovery_rate_per_hour != 0:
                estimated_recovery_hours = abs(total_remaining / recovery_rate_per_hour)

        return ErrorBudgetReport(
            timestamp=datetime.now(timezone.utc),
            total_budget_minutes=total_budget,
            total_consumed_minutes=total_consumed,
            total_remaining_minutes=total_remaining,
            overall_utilization_pct=overall_utilization,
            lane_allocations=self.allocations.copy(),
            recent_incidents=self.incidents[-50:] if len(self.incidents) > 50 else self.incidents,
            burn_rate_per_hour=burn_rate_per_hour,
            lanes_exhausted=exhausted_lanes,
            estimated_recovery_hours=estimated_recovery_hours,
        )

    def should_fallback_to_classical(self) -> bool:
        """Check if any lane budget is exhausted, triggering fallback to classical mode."""
        return any(alloc.budget_exhausted for alloc in self.allocations.values())

    def reset_annual_budget(self) -> None:
        """Reset budget at year boundary (typically at year start)."""
        logger.warning("Resetting annual error budget at year boundary")
        for allocation in self.allocations.values():
            allocation.consumed_minutes = 0.0
            allocation.remaining_minutes = allocation.total_budget_minutes
            allocation.burn_rate_per_hour = 0.0
        self.incidents.clear()
        self.created_at = datetime.now(timezone.utc)
