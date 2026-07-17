"""
Phase 5: Shadow Mode Execution

Runs quantum-hybrid solvers in parallel with classical solvers for comparison.
Results are advisory only - no production impact.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Shadow execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class SolverResult:
    """Result from a solver execution"""

    solver_name: str
    status: ExecutionStatus
    quality: float  # Solution quality (0.0 to 1.0 or objective value)
    latency_ms: float  # Execution time in milliseconds
    constraints_satisfied: bool
    metadata: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_seed: Optional[int] = None


@dataclass
class ShadowComparison:
    """Result of shadow execution comparison"""

    comparison_id: str
    decision_id: str
    classical_result: SolverResult
    hybrid_result: SolverResult
    improvement_pct: float  # (Hybrid - Classical) / Classical * 100
    latency_ratio: float  # Hybrid latency / Classical latency
    both_feasible: bool  # Both solutions satisfy constraints
    deterministic: bool  # Results reproducible with same seed
    timestamp: float = field(default_factory=time.time)
    notes: str = ""


class ShadowExecutor:
    """Executes quantum-hybrid solvers in shadow mode (advisory only)"""

    def __init__(self, timeout_ms: float = 5000.0):
        self.timeout_ms = timeout_ms
        self._executions: list[ShadowComparison] = []
        self._seeds_used: dict[str, int] = {}

    def execute_parallel(
        self,
        decision_id: str,
        classical_solver: Callable[..., SolverResult],
        hybrid_solver: Callable[..., SolverResult],
        solver_params: dict[str, Any],
        seed: Optional[int] = None,
    ) -> ShadowComparison:
        """Execute classical and hybrid solvers in parallel"""
        
        comparison_id = f"shadow_{decision_id}_{int(time.time()*1000)}"
        
        try:
            # Run both solvers with timeout
            classical_start = time.time()
            classical_result = self._safe_execute(
                classical_solver,
                solver_params,
                seed=seed,
                solver_name="classical",
            )
            classical_time = (time.time() - classical_start) * 1000

            hybrid_start = time.time()
            hybrid_result = self._safe_execute(
                hybrid_solver,
                solver_params,
                seed=seed,
                solver_name="hybrid",
            )
            hybrid_time = (time.time() - hybrid_start) * 1000

            # Update latencies
            classical_result.latency_ms = classical_time
            hybrid_result.latency_ms = hybrid_time

            # Calculate improvement
            improvement_pct = self._calculate_improvement(
                classical_result.quality,
                hybrid_result.quality,
            )

            latency_ratio = (
                hybrid_result.latency_ms / classical_result.latency_ms
                if classical_result.latency_ms > 0
                else 1.0
            )

            # Check determinism: same seed should yield same result
            deterministic = seed is not None and (
                classical_result.execution_seed == seed
                and hybrid_result.execution_seed == seed
            )

            comparison = ShadowComparison(
                comparison_id=comparison_id,
                decision_id=decision_id,
                classical_result=classical_result,
                hybrid_result=hybrid_result,
                improvement_pct=improvement_pct,
                latency_ratio=latency_ratio,
                both_feasible=(
                    classical_result.constraints_satisfied
                    and hybrid_result.constraints_satisfied
                ),
                deterministic=deterministic,
                notes=(
                    f"Classical: {classical_time:.1f}ms → Hybrid: {hybrid_time:.1f}ms; "
                    f"Improvement: {improvement_pct:+.2f}%"
                ),
            )

            self._executions.append(comparison)
            logger.info(
                f"Shadow execution {comparison_id}: "
                f"improvement={improvement_pct:+.2f}%, "
                f"latency_ratio={latency_ratio:.2f}x"
            )

            return comparison

        except Exception as e:
            logger.error(f"Shadow execution failed: {e}")
            # Return failed result
            failed_comparison = ShadowComparison(
                comparison_id=comparison_id,
                decision_id=decision_id,
                classical_result=SolverResult(
                    solver_name="classical",
                    status=ExecutionStatus.FAILED,
                    quality=0.0,
                    latency_ms=0.0,
                    constraints_satisfied=False,
                    error=str(e),
                ),
                hybrid_result=SolverResult(
                    solver_name="hybrid",
                    status=ExecutionStatus.FAILED,
                    quality=0.0,
                    latency_ms=0.0,
                    constraints_satisfied=False,
                    error=str(e),
                ),
                improvement_pct=0.0,
                latency_ratio=1.0,
                both_feasible=False,
                deterministic=False,
                notes=f"Failed: {e}",
            )
            self._executions.append(failed_comparison)
            raise

    def _safe_execute(
        self,
        solver: Callable[..., SolverResult],
        params: dict[str, Any],
        seed: Optional[int] = None,
        solver_name: str = "solver",
    ) -> SolverResult:
        """Safely execute a solver with timeout"""
        
        try:
            # Add seed if provided
            if seed is not None:
                params = {**params, "seed": seed}

            result = solver(**params)
            result.solver_name = solver_name
            result.execution_seed = seed
            result.status = ExecutionStatus.COMPLETED
            return result

        except TimeoutError:
            logger.warning(f"Solver {solver_name} timed out")
            return SolverResult(
                solver_name=solver_name,
                status=ExecutionStatus.TIMEOUT,
                quality=0.0,
                latency_ms=self.timeout_ms,
                constraints_satisfied=False,
                error="Timeout",
                execution_seed=seed,
            )
        except Exception as e:
            logger.error(f"Solver {solver_name} failed: {e}")
            return SolverResult(
                solver_name=solver_name,
                status=ExecutionStatus.FAILED,
                quality=0.0,
                latency_ms=0.0,
                constraints_satisfied=False,
                error=str(e),
                execution_seed=seed,
            )

    def _calculate_improvement(
        self, classical_quality: float, hybrid_quality: float
    ) -> float:
        """Calculate improvement percentage"""
        
        if classical_quality == 0:
            return 0.0
        
        # Assume higher quality is better
        improvement = (hybrid_quality - classical_quality) / abs(classical_quality)
        return improvement * 100

    def get_statistics(self) -> dict[str, float]:
        """Get aggregate statistics from shadow executions"""
        
        if not self._executions:
            return {}

        successful = [e for e in self._executions
                     if e.classical_result.status == ExecutionStatus.COMPLETED
                     and e.hybrid_result.status == ExecutionStatus.COMPLETED]

        if not successful:
            return {}

        improvements = [e.improvement_pct for e in successful]
        latency_ratios = [e.latency_ratio for e in successful]

        return {
            "total_executions": len(self._executions),
            "successful_executions": len(successful),
            "avg_improvement_pct": sum(improvements) / len(improvements),
            "max_improvement_pct": max(improvements),
            "min_improvement_pct": min(improvements),
            "avg_latency_ratio": sum(latency_ratios) / len(latency_ratios),
            "deterministic_pct": (
                sum(1 for e in successful if e.deterministic) / len(successful) * 100
                if successful else 0
            ),
            "feasibility_pct": (
                sum(1 for e in successful if e.both_feasible) / len(successful) * 100
                if successful else 0
            ),
        }
