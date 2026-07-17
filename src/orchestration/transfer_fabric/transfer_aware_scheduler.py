"""Transfer-Aware Scheduler (v2): Enhanced lane scheduling with latency awareness.

Builds on LaneSchedulerV1 with:
- Latency-aware routing (p99 <5s target)
- Resource contention arbitration
- Transfer priority handling
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class LaneState(Enum):
    """Possible states for a lane."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"


@dataclass
class LatencyEstimate:
    """Latency estimate for a route."""

    route_id: str
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "route_id": self.route_id,
            "p50_ms": self.p50_ms,
            "p95_ms": self.p95_ms,
            "p99_ms": self.p99_ms,
        }


@dataclass
class ResourceContention:
    """Represents resource contention between lanes."""

    lane_id: str
    resource_type: str
    utilization_percent: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "lane_id": self.lane_id,
            "resource_type": self.resource_type,
            "utilization_percent": self.utilization_percent,
        }


@dataclass
class Schedule:
    """Transfer-aware schedule output."""

    lanes_ordered: List[str] = field(default_factory=list)
    latency_estimates: List[LatencyEstimate] = field(default_factory=list)
    contentions: List[ResourceContention] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "lanes_ordered": self.lanes_ordered,
            "latency_estimates": [le.to_dict() for le in self.latency_estimates],
            "contentions": [c.to_dict() for c in self.contentions],
        }


class TransferAwareSchedulerV2:
    """Enhanced lane scheduler with latency awareness (v2)."""

    LATENCY_TARGET_MS = 5000
    CONTENTION_THRESHOLD = 80.0

    def __init__(self):
        """Initialize transfer-aware scheduler."""
        self.lanes: Dict[str, Dict[str, Any]] = {}
        self.transfer_priorities: Dict[str, int] = {}
        self.latency_measurements: Dict[str, List[float]] = {}
        self.resource_utilization: Dict[str, float] = {}
        self.execution_history: List[Schedule] = []

    def register_lane(
        self,
        lane_id: str,
        name: str,
        upstream_dependencies: Optional[List[str]] = None,
    ) -> None:
        """Register a lane."""
        if upstream_dependencies is None:
            upstream_dependencies = []

        self.lanes[lane_id] = {
            "name": name,
            "upstream_dependencies": upstream_dependencies,
            "state": LaneState.PENDING.value,
        }
        logger.info(f"Lane registered: {lane_id}")

    def set_transfer_priority(self, lane_id: str, priority: int) -> None:
        """Set transfer priority for a lane (higher = more important)."""
        self.transfer_priorities[lane_id] = priority
        logger.info(f"Transfer priority set: {lane_id}={priority}")

    def record_latency(self, route_id: str, latency_ms: float) -> None:
        """Record latency measurement for a route."""
        if route_id not in self.latency_measurements:
            self.latency_measurements[route_id] = []

        self.latency_measurements[route_id].append(latency_ms)

    def get_latency_estimate(self, route_id: str) -> LatencyEstimate:
        """Calculate latency percentiles for a route."""
        measurements = self.latency_measurements.get(route_id, [100.0])

        sorted_latencies = sorted(measurements)
        n = len(sorted_latencies)

        p50_idx = max(0, int(n * 0.5) - 1)
        p95_idx = max(0, int(n * 0.95) - 1)
        p99_idx = max(0, int(n * 0.99) - 1)

        return LatencyEstimate(
            route_id=route_id,
            p50_ms=float(sorted_latencies[p50_idx]),
            p95_ms=float(sorted_latencies[p95_idx]),
            p99_ms=float(sorted_latencies[p99_idx]),
        )

    def set_resource_utilization(self, resource_id: str, percent: float) -> None:
        """Set resource utilization percentage."""
        self.resource_utilization[resource_id] = max(0.0, min(100.0, percent))

    def detect_contention(self) -> List[ResourceContention]:
        """Detect resource contention."""
        contentions = []

        for resource_id, utilization in self.resource_utilization.items():
            if utilization >= self.CONTENTION_THRESHOLD:
                contentions.append(
                    ResourceContention(
                        lane_id=resource_id,
                        resource_type="compute",
                        utilization_percent=utilization,
                    )
                )

        logger.info(f"Contention detected: {len(contentions)} resources")
        return contentions

    def order_lanes(self) -> List[str]:
        """Order lanes respecting dependencies and transfer priorities."""
        ordered = []
        visited: Set[str] = set()
        visiting: Set[str] = set()

        def dfs(lane_id: str) -> None:
            if lane_id in visited:
                return
            if lane_id in visiting:
                logger.warning(f"Circular dependency detected: {lane_id}")
                return

            visiting.add(lane_id)

            lane = self.lanes.get(lane_id)
            if lane:
                for dep in lane.get("upstream_dependencies", []):
                    dfs(dep)

            visiting.remove(lane_id)
            visited.add(lane_id)
            ordered.append(lane_id)

        for lane_id in self.lanes:
            dfs(lane_id)

        ordered.sort(
            key=lambda x: self.transfer_priorities.get(x, 0),
            reverse=True,
        )

        logger.info(f"Lanes ordered: {ordered}")
        return ordered

    def schedule_transfers(self) -> Schedule:
        """Generate transfer-aware schedule."""
        schedule = Schedule()

        schedule.lanes_ordered = self.order_lanes()

        for lane_id in schedule.lanes_ordered:
            latency_est = self.get_latency_estimate(lane_id)
            schedule.latency_estimates.append(latency_est)

            if latency_est.p99_ms > self.LATENCY_TARGET_MS:
                logger.warning(
                    f"Latency warning for {lane_id}: "
                    f"p99={latency_est.p99_ms}ms > {self.LATENCY_TARGET_MS}ms"
                )

        schedule.contentions = self.detect_contention()

        self.execution_history.append(schedule)
        logger.info(f"Schedule generated: {len(schedule.lanes_ordered)} lanes")

        return schedule

    def arbitrate_contention(self, contentions: List[ResourceContention]) -> Dict[str, int]:
        """Arbitrate between lanes for shared resources."""
        arbitration = {}

        for contention in contentions:
            priority = self.transfer_priorities.get(contention.lane_id, 0)
            arbitration[contention.lane_id] = priority

        logger.info(f"Contention arbitration: {len(arbitration)} resources")
        return arbitration

    def estimate_total_time(self) -> float:
        """Estimate total execution time based on latencies."""
        total_ms = 0.0

        for lane_id in self.lanes:
            estimate = self.get_latency_estimate(lane_id)
            total_ms += estimate.p99_ms

        logger.info(f"Total execution time estimate: {total_ms}ms")
        return total_ms

    def get_schedule_history(self) -> List[Schedule]:
        """Get schedule execution history."""
        return self.execution_history.copy()

    def validate_latency_sla(self) -> bool:
        """Validate if all lanes meet latency SLA."""
        all_meet_sla = True

        for lane_id in self.lanes:
            estimate = self.get_latency_estimate(lane_id)
            if estimate.p99_ms > self.LATENCY_TARGET_MS:
                all_meet_sla = False
                logger.warning(f"Lane {lane_id} exceeds latency SLA")

        return all_meet_sla
