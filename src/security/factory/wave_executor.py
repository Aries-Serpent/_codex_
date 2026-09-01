"""
S4: Parallel Wave Executor

Executes findings in waves while respecting resource limits.

For each finding: dispatch to appropriate remediation agent
Tracks: execution status, time, success/failure, rollback trigger

Success metric: Wave completion time <2x sequential
"""

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .scoring import ScoredFamily, WavePlan


class ExecutionStatus(str, Enum):
    """Execution status for a finding."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class ExecutionResult:
    """Result of executing a single finding."""
    family_id: str
    status: ExecutionStatus
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_time: Optional[str] = None
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    rollback_triggered: bool = False

    def mark_success(self) -> None:
        """Mark as successful."""
        self.status = ExecutionStatus.SUCCESS
        self.end_time = datetime.utcnow().isoformat()
        self.duration_seconds = self._compute_duration()

    def mark_failed(self, error: str) -> None:
        """Mark as failed."""
        self.status = ExecutionStatus.FAILED
        self.error_message = error
        self.end_time = datetime.utcnow().isoformat()
        self.duration_seconds = self._compute_duration()

    def _compute_duration(self) -> float:
        """Compute duration in seconds."""
        if self.end_time is None:
            return 0.0
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        return (end - start).total_seconds()


@dataclass
class WaveExecutionReport:
    """Report for a complete wave execution."""
    wave_number: int
    total_findings: int
    completed: int = 0
    failed: int = 0
    rolled_back: int = 0
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_time: Optional[str] = None
    duration_seconds: float = 0.0
    results: List[ExecutionResult] = field(default_factory=list)

    def completion_percentage(self) -> float:
        """Get completion percentage."""
        if self.total_findings == 0:
            return 0.0
        return (self.completed / self.total_findings) * 100

    def failure_rate(self) -> float:
        """Get failure rate."""
        if self.total_findings == 0:
            return 0.0
        return (self.failed / self.total_findings) * 100


class WaveExecutor:
    """Executes finding remediation in parallel waves."""

    def __init__(self, max_workers: int = 4, fail_fast: bool = False):
        """Initialize executor."""
        self.max_workers = max_workers
        self.fail_fast = fail_fast
        self.remediation_handler: Optional[Callable] = None
        self.reports: List[WaveExecutionReport] = []

    def set_remediation_handler(
        self,
        handler: Callable[[ScoredFamily], ExecutionResult],
    ) -> None:
        """Set the remediation handler function."""
        self.remediation_handler = handler

    def execute_wave(self, wave: List[ScoredFamily]) -> WaveExecutionReport:
        """Execute a single wave."""
        if not self.remediation_handler:
            raise RuntimeError("Remediation handler not set")

        wave_num = wave[0].wave if wave else 0
        report = WaveExecutionReport(wave_number=wave_num, total_findings=len(wave))

        if not wave:
            report.end_time = datetime.utcnow().isoformat()
            return report

        # Execute in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures: Dict[Future, ScoredFamily] = {}

            for family in wave:
                future = executor.submit(self.remediation_handler, family)
                futures[future] = family

            # Collect results
            for future in futures:
                try:
                    result = future.result(timeout=300)  # 5 min timeout per finding
                    report.results.append(result)

                    if result.status == ExecutionStatus.SUCCESS:
                        report.completed += 1
                    elif result.status == ExecutionStatus.FAILED:
                        report.failed += 1
                        if self.fail_fast:
                            executor.shutdown(wait=False)
                            break
                    elif result.status == ExecutionStatus.ROLLED_BACK:
                        report.rolled_back += 1

                except Exception as e:
                    report.failed += 1
                    family = futures[future]
                    family_id = getattr(family, "family_id", None)
                    if family_id is None and hasattr(family, "family"):
                        family_id = getattr(family.family, "family_id", "unknown")
                    if family_id is None:
                        family_id = "unknown"
                    result = ExecutionResult(
                        family_id=family_id,
                        status=ExecutionStatus.FAILED,
                        error_message=str(e),
                    )
                    report.results.append(result)

        report.end_time = datetime.utcnow().isoformat()
        self.reports.append(report)
        return report

    def execute_plan(self, plan: WavePlan) -> List[WaveExecutionReport]:
        """Execute complete wave plan."""
        reports = []

        for wave in [plan.wave_1, plan.wave_2, plan.wave_3]:
            if not wave:
                continue
            report = self.execute_wave(wave)
            reports.append(report)

        return reports

    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        if not self.reports:
            return {
                "total_waves": 0,
                "total_completed": 0,
                "total_failed": 0,
                "total_rolled_back": 0,
            }

        return {
            "total_waves": len(self.reports),
            "total_completed": sum(r.completed for r in self.reports),
            "total_failed": sum(r.failed for r in self.reports),
            "total_rolled_back": sum(r.rolled_back for r in self.reports),
            "avg_completion_percentage": (
                sum(r.completion_percentage() for r in self.reports) / len(self.reports)
            ),
        }


def execute_wave(
    wave: List[ScoredFamily],
    handler: Callable[[ScoredFamily], ExecutionResult],
    max_workers: int = 4,
) -> WaveExecutionReport:
    """Execute a single wave."""
    executor = WaveExecutor(max_workers=max_workers)
    executor.set_remediation_handler(handler)
    return executor.execute_wave(wave)
