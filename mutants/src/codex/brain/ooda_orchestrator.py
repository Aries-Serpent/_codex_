"""OODA Orchestrator: Main loop orchestration and cycle management.

This module:
- Orchestrates complete OODA cycles
- Manages loop closure and feedback
- Supports parallel cycles (5+ concurrent)
- Maintains monitoring dashboard
- Persists cycle records

Output: Continuous OODA loop execution with metrics
"""

import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from codex.logging.structured_logger import logger

from .ooda_actor import ExecutionReport, OODAactor
from .ooda_decider import DecisionDirective, OODADecider
from .ooda_observer import Observable, OODAObserver
from .ooda_orienter import OODAOrienter, Orientation


@dataclass
class CycleMetrics:
    """Metrics for a single OODA cycle."""

    phase_latencies: dict[str, float]  # ms per phase
    decision_confidence: float
    execution_success_rate: float
    total_agents_involved: int
    side_effects_count: int


@dataclass
class CycleRecord:
    """Complete record of a single OODA cycle."""

    cycle_id: str
    timestamp: datetime
    observable: Observable
    orientation: Orientation
    decision: DecisionDirective
    execution_report: ExecutionReport
    duration_ms: float
    success: bool
    metrics: CycleMetrics


@dataclass
class OODAMetrics:
    """Aggregated metrics for all cycles."""

    total_cycles: int
    successful_cycles: int
    failed_cycles: int
    avg_cycle_latency_ms: float
    p95_cycle_latency_ms: float
    p99_cycle_latency_ms: float
    avg_decision_confidence: float
    avg_execution_success_rate: float
    total_agents_invoked: int
    total_side_effects: int
    uptime_percent: float


class CycleRecorder:
    """Records and retrieves OODA cycle records."""

    def __init__(self, db_path: Path = Path(".codex/ooda_cycles.jsonl")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.in_memory_buffer: list[CycleRecord] = []

    def record_cycle(self, cycle: CycleRecord) -> None:
        """Record a cycle to persistent storage."""
        try:
            # Store in memory buffer
            self.in_memory_buffer.append(cycle)

            # Persist to JSONL (append-only)
            with open(self.db_path, "a") as f:
                # Convert dataclasses to dict, handling datetime serialization
                cycle_dict = self._to_serializable_dict(cycle)
                f.write(json.dumps(cycle_dict) + "\n")
        except Exception as e:
            logger.error(f"Failed to record cycle: {e}")

    def get_recent_cycles(self, limit: int = 100) -> list[CycleRecord]:
        """Get recent cycles from buffer."""
        return self.in_memory_buffer[-limit:]

    def get_cycle_metrics(self, limit: int = 100) -> OODAMetrics:
        """Compute metrics from recent cycles."""
        try:
            recent = self.get_recent_cycles(limit)
            if not recent:
                return self._empty_metrics()

            successful = [c for c in recent if c.success]
            latencies = [c.duration_ms for c in recent]
            confidences = [c.decision.confidence for c in recent]
            success_rates = [c.execution_report.success_rate for c in recent if c.execution_report]

            # Calculate percentiles
            sorted_latencies = sorted(latencies)
            p95_idx = int(len(sorted_latencies) * 0.95)
            p99_idx = int(len(sorted_latencies) * 0.99)

            return OODAMetrics(
                total_cycles=len(recent),
                successful_cycles=len(successful),
                failed_cycles=len(recent) - len(successful),
                avg_cycle_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
                p95_cycle_latency_ms=(
                    sorted_latencies[p95_idx] if p95_idx < len(sorted_latencies) else 0
                ),
                p99_cycle_latency_ms=(
                    sorted_latencies[p99_idx] if p99_idx < len(sorted_latencies) else 0
                ),
                avg_decision_confidence=sum(confidences) / len(confidences) if confidences else 0,
                avg_execution_success_rate=(
                    sum(success_rates) / len(success_rates) if success_rates else 0
                ),
                total_agents_invoked=sum(len(c.execution_report.agents_executed) for c in recent),
                total_side_effects=sum(len(c.execution_report.side_effects) for c in recent),
                uptime_percent=len(successful) / len(recent) * 100 if recent else 0,
            )
        except Exception as e:
            logger.error(f"Failed to compute metrics: {e}")
            return self._empty_metrics()

    def _to_serializable_dict(self, obj: Any) -> Any:
        """Convert object to JSON-serializable dict."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, (list, tuple)):
            return [self._to_serializable_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._to_serializable_dict(v) for k, v in obj.items()}
        elif hasattr(obj, "__dataclass_fields__"):
            return self._to_serializable_dict(asdict(obj))
        else:
            return obj

    @staticmethod
    def _empty_metrics() -> OODAMetrics:
        """Return empty metrics."""
        return OODAMetrics(
            total_cycles=0,
            successful_cycles=0,
            failed_cycles=0,
            avg_cycle_latency_ms=0,
            p95_cycle_latency_ms=0,
            p99_cycle_latency_ms=0,
            avg_decision_confidence=0,
            avg_execution_success_rate=0,
            total_agents_invoked=0,
            total_side_effects=0,
            uptime_percent=0,
        )


class OODAOrchestrator:
    """Main orchestrator: manages complete OODA cycles."""

    def __init__(self, repo_path: Path = Path(".")):
        self.repo_path = repo_path
        self.observer = OODAObserver(repo_path)
        self.orienter = OODAOrienter()
        self.decider = OODADecider()
        self.actor = OODAactor()
        self.recorder = CycleRecorder()
        self.previous_execution_report: Optional[ExecutionReport] = None
        self.max_iterations = 5  # Anti-loop guard

    def run_cycle(self, context: Optional[Any] = None) -> CycleRecord:
        """Execute one complete OODA cycle."""
        cycle_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        phase_latencies = {}  # type: ignore[var-annotated]

        try:
            # Execute OODA phases
            observable = self._execute_observe_phase(phase_latencies)
            orientation = self._execute_orient_phase(observable, phase_latencies)
            decision = self._execute_decide_phase(observable, orientation, phase_latencies)
            execution_report = self._execute_act_phase(decision, phase_latencies)

            # Store execution report for loop closure
            self.previous_execution_report = execution_report

            # Create successful cycle record
            return self._create_cycle_record(
                cycle_id,
                start_time,
                phase_latencies,
                observable,
                orientation,
                decision,
                execution_report,
            )

        except Exception as e:
            logger.error(f"Cycle {cycle_id} failed: {e}")
            duration_ms = (time.time() - start_time) * 1000
            return self._create_error_cycle(cycle_id, duration_ms, phase_latencies)

    def _execute_observe_phase(self, phase_latencies: dict[str, Any]) -> Observable:
        """Execute OBSERVE phase."""
        observe_start = time.time()
        observable = self.observer.observe()
        phase_latencies["observe"] = (time.time() - observe_start) * 1000
        return observable

    def _execute_orient_phase(
        self,
        observable: Observable,
        phase_latencies: dict[str, Any],
    ) -> Orientation:
        """Execute ORIENT phase."""
        orient_start = time.time()
        orientation = self.orienter.orient(observable)
        phase_latencies["orient"] = (time.time() - orient_start) * 1000
        return orientation

    def _execute_decide_phase(
        self,
        observable: Observable,
        orientation: Orientation,
        phase_latencies: dict[str, Any],
    ) -> DecisionDirective:
        """Execute DECIDE phase."""
        decide_start = time.time()
        decision = self.decider.decide(
            observable,
            orientation,
            d_mode_authority=True,  # Full authority
        )
        phase_latencies["decide"] = (time.time() - decide_start) * 1000
        return decision

    def _execute_act_phase(
        self,
        decision: DecisionDirective,
        phase_latencies: dict[str, Any],
    ) -> ExecutionReport:
        """Execute ACT phase."""
        act_start = time.time()
        execution_report = self.actor.act(decision, timeout_seconds=60)
        phase_latencies["act"] = (time.time() - act_start) * 1000
        return execution_report

    def _create_cycle_record(
        self,
        cycle_id: str,
        start_time: float,
        phase_latencies: dict[str, Any],
        observable: Observable,
        orientation: Orientation,
        decision: DecisionDirective,
        execution_report: ExecutionReport,
    ) -> CycleRecord:
        """Create a successful cycle record."""
        duration_ms = (time.time() - start_time) * 1000
        success = execution_report.success_rate > 0

        metrics = CycleMetrics(
            phase_latencies=phase_latencies,
            decision_confidence=decision.confidence,
            execution_success_rate=execution_report.success_rate,
            total_agents_involved=len(execution_report.agents_executed),
            side_effects_count=len(execution_report.side_effects),
        )

        cycle = CycleRecord(
            cycle_id=cycle_id,
            timestamp=datetime.now(),
            observable=observable,
            orientation=orientation,
            decision=decision,
            execution_report=execution_report,
            duration_ms=duration_ms,
            success=success,
            metrics=metrics,
        )

        # Record cycle
        self.recorder.record_cycle(cycle)

        logger.info(
            f"Cycle {cycle_id}: {duration_ms:.0f}ms, "
            f"confidence={decision.confidence:.2%}, "
            f"success={execution_report.success_rate:.2%}"
        )

        return cycle

    def _create_error_cycle(
        self,
        cycle_id: str,
        duration_ms: float,
        phase_latencies: dict[str, Any],
    ) -> CycleRecord:
        """Create an error cycle record."""
        return CycleRecord(
            cycle_id=cycle_id,
            timestamp=datetime.now(),
            observable=Observable(
                timestamp=datetime.now(),
                repository=None,  # type: ignore[arg-type]
                agents=None,  # type: ignore[arg-type]
                tasks=None,  # type: ignore[arg-type]
                environment=None,  # type: ignore[arg-type]
                events=[],
                metadata=None,  # type: ignore[arg-type]
            ),
            orientation=Orientation(
                timestamp=datetime.now(),
                relevant_patterns=[],
                decision_precedents=[],
                agent_candidates=[],
                risk_assessment=None,  # type: ignore[arg-type]
                opportunities=[],
                context_summary="Error",
                confidence_baseline=0.0,
            ),
            decision=DecisionDirective(
                decision_id="error",
                timestamp=datetime.now(),
                action=None,  # type: ignore[arg-type]
                candidates=[],
                confidence=0.0,
                assigned_agents=[],
                parallel_execution=False,
                guardrail_checks=[],
                audit_id="",
                decision_rationale="Cycle error occurred",
                requires_approval=True,
            ),
            execution_report=ExecutionReport(
                timestamp=datetime.now(),
                decision_id="error",
                agents_executed=[],
                results=[],
                outcomes_matched=False,
                side_effects=[],
                duration_ms=0,
                success_rate=0.0,
                impact_score=0.0,
                next_observable_delta={},
            ),
            duration_ms=duration_ms,
            success=False,
            metrics=CycleMetrics(
                phase_latencies=phase_latencies,
                decision_confidence=0.0,
                execution_success_rate=0.0,
                total_agents_involved=0,
                side_effects_count=0,
            ),
        )

    def run_continuous(
        self,
        frequency_seconds: int = 10,
        max_cycles: Optional[int] = None,
    ) -> None:
        """Run OODA loops continuously."""
        cycle_count = 0

        while max_cycles is None or cycle_count < max_cycles:
            try:
                # Loop closure: use previous execution report as context
                context = self.previous_execution_report if cycle_count > 0 else None

                self.run_cycle(context)
                cycle_count += 1

                # Enforce frequency
                time.sleep(frequency_seconds)

            except KeyboardInterrupt:
                logger.info("OODA loop interrupted by user")
                break
            except Exception as e:
                logger.error(f"Cycle {cycle_count} failed: {e}")
                time.sleep(frequency_seconds)

        logger.info(f"OODA loop completed: {cycle_count} cycles")

    def get_metrics(self) -> OODAMetrics:
        """Get current metrics."""
        return self.recorder.get_cycle_metrics()

    def get_recent_cycles(self, limit: int = 10) -> list[CycleRecord]:
        """Get recent cycle records."""
        return self.recorder.get_recent_cycles(limit)

    def print_metrics_dashboard(self) -> None:
        """Print a metrics dashboard."""
        metrics = self.get_metrics()

        logger.info("\n" + "=" * 60)
        logger.info("OODA LOOP ORCHESTRATION METRICS")
        logger.info("=" * 60)
        logger.info(
            f"Cycles: {metrics.total_cycles} "
            f"(✓{metrics.successful_cycles} ✗{metrics.failed_cycles})"
        )
        logger.info(f"Uptime: {metrics.uptime_percent:.1f}%")
        logger.info("\nLatency (ms):")
        logger.info(f"  Average: {metrics.avg_cycle_latency_ms:.0f}")
        logger.info(f"  p95: {metrics.p95_cycle_latency_ms:.0f}")
        logger.info(f"  p99: {metrics.p99_cycle_latency_ms:.0f}")
        logger.info("\nQuality:")
        logger.info(f"  Avg Confidence: {metrics.avg_decision_confidence:.2%}")
        logger.info(f"  Avg Success Rate: {metrics.avg_execution_success_rate:.2%}")
        logger.info("\nResources:")
        logger.info(f"  Agents Involved: {metrics.total_agents_invoked}")
        logger.info(f"  Side Effects: {metrics.total_side_effects}")
        logger.info("=" * 60 + "\n")


class ParallelOODAOrchestrator(OODAOrchestrator):
    """Support for parallel OODA cycles."""

    def __init__(self, repo_path: Path = Path("."), max_concurrent_cycles: int = 5):
        super().__init__(repo_path)
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_cycles)
        self.cycles: dict[str, Any] = {}

    def start_cycle(self, context: Optional[Any] = None) -> str:
        """Start a new cycle (non-blocking)."""
        future = self.executor.submit(self.run_cycle, context)
        cycle_id = str(uuid.uuid4())[:8]
        self.cycles[cycle_id] = future
        return cycle_id

    def get_cycle_result(self, cycle_id: str) -> Optional[CycleRecord]:
        """Get result of a cycle (blocking if not done)."""
        if cycle_id not in self.cycles:
            return None
        try:
            return self.cycles[cycle_id].result()
        except Exception as e:
            logger.error(f"Failed to get cycle result {cycle_id}: {e}")
            return None

    def get_completed_cycles(self) -> dict[str, CycleRecord]:
        """Get all completed cycles."""
        completed = {}
        for cycle_id, future in self.cycles.items():
            if future.done():
                try:
                    completed[cycle_id] = future.result()
                except Exception as e:
                    logger.error(f"Failed to get result for {cycle_id}: {e}")
        return completed

    def shutdown(self) -> None:
        """Shutdown the executor."""
        self.executor.shutdown(wait=True)
