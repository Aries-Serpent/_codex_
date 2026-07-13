"""Lane Scheduler Foundation (v1) — Basic lane execution coordinator.

Implements lane state tracking and upstream dependency enforcement
with deterministic ordering.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)


class LaneState(Enum):
    """Possible states for a lane."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"


class ExecutionMode(Enum):
    """Supported execution modes."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    SHARDED = "sharded"


class LaneSchedulerError(Exception):
    """Raised when lane scheduling fails."""

    pass


@dataclass
class Lane:
    """Represents a single lane with its configuration."""

    lane_id: str
    name: str
    upstream_dependencies: List[str] = field(default_factory=list)
    state: LaneState = LaneState.PENDING
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    deterministic_seed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "lane_id": self.lane_id,
            "name": self.name,
            "upstream_dependencies": self.upstream_dependencies,
            "state": self.state.value,
            "execution_mode": self.execution_mode.value,
            "deterministic_seed": self.deterministic_seed,
        }


@dataclass
class ScheduleResult:
    """Result of lane scheduling and execution."""

    lane_id: str
    state: LaneState
    execution_order: List[str] = field(default_factory=list)
    start_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    end_time: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "lane_id": self.lane_id,
            "state": self.state.value,
            "execution_order": self.execution_order,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error_message": self.error_message,
        }


class LaneSchedulerV1:
    """Basic lane execution coordinator (v1).

    v1 features:
    - Track lane states
    - Enforce upstream dependencies
    - Deterministic ordering
    - Support sequential/parallel/sharded modes
    """

    def __init__(self):
        """Initialize the scheduler."""
        self.lanes: Dict[str, Lane] = {}
        self.execution_history: List[ScheduleResult] = []

    def register_lane(self, lane: Lane) -> None:
        """Register a lane with the scheduler.

        Args:
            lane: Lane to register

        Raises:
            LaneSchedulerError: If lane is already registered
        """
        if lane.lane_id in self.lanes:
            raise LaneSchedulerError(f"Lane {lane.lane_id} already registered")

        self.lanes[lane.lane_id] = lane
        logger.info(f"Registered lane: {lane.lane_id}")

    def register_lanes(self, lanes: List[Lane]) -> None:
        """Register multiple lanes at once.

        Args:
            lanes: List of lanes to register
        """
        for lane in lanes:
            self.register_lane(lane)

    def _validate_dependencies(self) -> bool:
        """Validate that all dependencies are registered.

        Returns:
            True if all dependencies valid

        Raises:
            LaneSchedulerError: If dependencies invalid
        """
        for lane_id, lane in self.lanes.items():
            for dep in lane.upstream_dependencies:
                if dep not in self.lanes:
                    raise LaneSchedulerError(
                        f"Lane {lane_id} depends on unregistered lane {dep}"
                    )

        return True

    def _get_execution_order(self) -> List[str]:
        """Compute deterministic execution order based on dependencies.

        Returns:
            List of lane IDs in execution order

        Raises:
            LaneSchedulerError: If circular dependency detected
        """
        visited = set()
        visiting = set()
        order = []

        def visit(lane_id: str) -> None:
            if lane_id in visited:
                return

            if lane_id in visiting:
                raise LaneSchedulerError(f"Circular dependency detected at {lane_id}")

            visiting.add(lane_id)
            lane = self.lanes[lane_id]

            # Visit upstream dependencies first
            for dep in sorted(lane.upstream_dependencies):  # Sort for determinism
                visit(dep)

            visiting.remove(lane_id)
            visited.add(lane_id)
            order.append(lane_id)

        # Process lanes in sorted order for deterministic traversal
        for lane_id in sorted(self.lanes.keys()):
            visit(lane_id)

        return order

    def _check_dependencies_ready(self, lane_id: str) -> bool:
        """Check if all upstream dependencies of a lane have passed.

        Args:
            lane_id: ID of lane to check

        Returns:
            True if all dependencies have passed
        """
        lane = self.lanes[lane_id]

        for dep_id in lane.upstream_dependencies:
            dep_lane = self.lanes[dep_id]
            if dep_lane.state != LaneState.PASSED:
                return False

        return True

    def schedule_lane(self, lane_id: str) -> ScheduleResult:
        """Schedule execution of a single lane.

        Checks that upstream dependencies have passed before scheduling.

        Args:
            lane_id: ID of lane to schedule

        Returns:
            ScheduleResult with execution status

        Raises:
            LaneSchedulerError: If lane not found or dependencies not ready
        """
        if lane_id not in self.lanes:
            raise LaneSchedulerError(f"Lane {lane_id} not found")

        lane = self.lanes[lane_id]

        # Check dependencies
        if not self._check_dependencies_ready(lane_id):
            failed_deps = [
                d
                for d in lane.upstream_dependencies
                if self.lanes[d].state != LaneState.PASSED
            ]
            error_msg = f"Upstream dependencies not ready: {failed_deps}"

            result = ScheduleResult(
                lane_id=lane_id,
                state=LaneState.PENDING,
                error_message=error_msg,
            )
            logger.warning(f"Lane {lane_id} scheduling blocked: {error_msg}")
            return result

        # Simulate lane execution
        lane.state = LaneState.RUNNING
        logger.info(f"Lane {lane_id} scheduled for execution")

        # Simulate successful execution
        lane.state = LaneState.PASSED

        execution_order = self._get_execution_order()
        result = ScheduleResult(
            lane_id=lane_id,
            state=LaneState.PASSED,
            execution_order=execution_order,
            end_time=datetime.now(timezone.utc).isoformat(),
        )

        self.execution_history.append(result)
        logger.info(f"Lane {lane_id} passed")

        return result

    def schedule_all_lanes(self, mode: ExecutionMode = ExecutionMode.SEQUENTIAL) -> Dict[str, ScheduleResult]:
        """Schedule all lanes with dependency enforcement.

        Args:
            mode: Execution mode (sequential, parallel, or sharded)

        Returns:
            Dict mapping lane_id to ScheduleResult

        Raises:
            LaneSchedulerError: If scheduling fails
        """
        try:
            self._validate_dependencies()
            execution_order = self._get_execution_order()

            results = {}

            logger.info(
                f"Scheduling {len(execution_order)} lanes in {mode.value} mode: {execution_order}"
            )

            for lane_id in execution_order:
                result = self.schedule_lane(lane_id)
                results[lane_id] = result

                if result.state == LaneState.PENDING:
                    logger.warning(f"Lane {lane_id} could not be scheduled")

            return results
        except Exception as e:
            raise LaneSchedulerError(f"Failed to schedule lanes: {e}")

    def get_lane_state(self, lane_id: str) -> LaneState:
        """Get current state of a lane.

        Args:
            lane_id: ID of lane

        Returns:
            Current LaneState

        Raises:
            LaneSchedulerError: If lane not found
        """
        if lane_id not in self.lanes:
            raise LaneSchedulerError(f"Lane {lane_id} not found")

        return self.lanes[lane_id].state

    def get_all_lane_states(self) -> Dict[str, str]:
        """Get states of all lanes.

        Returns:
            Dict mapping lane_id to state value
        """
        return {lane_id: lane.state.value for lane_id, lane in self.lanes.items()}

    def reset_lane(self, lane_id: str) -> None:
        """Reset a lane to pending state.

        Args:
            lane_id: ID of lane to reset

        Raises:
            LaneSchedulerError: If lane not found
        """
        if lane_id not in self.lanes:
            raise LaneSchedulerError(f"Lane {lane_id} not found")

        self.lanes[lane_id].state = LaneState.PENDING
        logger.info(f"Lane {lane_id} reset to pending")

    def reset_all_lanes(self) -> None:
        """Reset all lanes to pending state."""
        for lane in self.lanes.values():
            lane.state = LaneState.PENDING
        logger.info("All lanes reset to pending")

    def export_schedule(self) -> Dict[str, Any]:
        """Export full schedule as dictionary.

        Returns:
            Dict with lanes, execution order, and history
        """
        try:
            execution_order = self._get_execution_order()
        except Exception:
            execution_order = []

        return {
            "lanes": {lane_id: lane.to_dict() for lane_id, lane in self.lanes.items()},
            "execution_order": execution_order,
            "execution_history": [r.to_dict() for r in self.execution_history],
            "execution_mode": ExecutionMode.SEQUENTIAL.value,
        }
