"""
Phase 5: Promotion Gates

KPI-based gates for promotion from shadow mode to Phase 6 canary deployment.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class GateStatus(Enum):
    """Gate evaluation status"""

    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass
class GateResult:
    """Result of a gate evaluation"""

    gate_name: str
    gate_number: int  # 1, 2, 3 for Phase 5 shadow gates
    status: GateStatus
    threshold: float
    actual_value: float
    passed: bool
    evidence: dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass
class PromotionGateReport:
    """Report of promotion gate evaluation"""

    evaluation_id: str
    gates: list[GateResult]
    all_passed: bool
    ready_for_promotion: bool
    recommendation: str
    details: dict[str, Any] = field(default_factory=dict)


class PromotionGates:
    """Evaluates KPI gates for shadow → canary promotion"""

    def __init__(self):
        self._gate_history: list[PromotionGateReport] = []

        # Phase 5 Shadow Mode Gates
        self.GATE_1_IMPROVEMENT = {
            "name": "Shadow Improvement Threshold",
            "number": 1,
            "threshold": 0.05,  # >5% improvement
            "description": "Hybrid solver shows >5% improvement over classical",
        }
        self.GATE_2_DETERMINISM = {
            "name": "Determinism Drift",
            "number": 2,
            "threshold": 0.001,  # <0.1% variance
            "description": "Identical seeds produce consistent results (<0.1% drift)",
        }
        self.GATE_3_LATENCY = {
            "name": "Latency Acceptable",
            "number": 3,
            "threshold": 2.0,  # <2x classical latency
            "description": "Hybrid execution latency <2x classical",
        }

    def evaluate_shadow_gates(
        self,
        avg_improvement_pct: float,
        determinism_drift_pct: float,
        latency_ratio: float,
        num_samples: int,
        metadata: dict[str, Any] | None = None,
    ) -> PromotionGateReport:
        """Evaluate all Phase 5 promotion gates"""

        evaluation_id = f"eval_{int(1e9)}"  # Simplified ID
        gates = []

        # Gate 1: Improvement Threshold
        gate_1_pass = avg_improvement_pct > self.GATE_1_IMPROVEMENT["threshold"] * 100
        gate_1_status = GateStatus.PASS if gate_1_pass else GateStatus.FAIL
        gates.append(
            GateResult(
                gate_name=self.GATE_1_IMPROVEMENT["name"],
                gate_number=1,
                status=gate_1_status,
                threshold=self.GATE_1_IMPROVEMENT["threshold"] * 100,
                actual_value=avg_improvement_pct,
                passed=gate_1_pass,
                evidence={
                    "avg_improvement_pct": avg_improvement_pct,
                    "num_samples": num_samples,
                    "description": self.GATE_1_IMPROVEMENT["description"],
                },
                notes=(
                    f"Hybrid shows {avg_improvement_pct:+.2f}% improvement "
                    f"(threshold: >{self.GATE_1_IMPROVEMENT['threshold']*100:.1f}%)"
                ),
            )
        )

        # Gate 2: Determinism Drift
        gate_2_pass = determinism_drift_pct < self.GATE_2_DETERMINISM["threshold"] * 100
        gate_2_status = GateStatus.PASS if gate_2_pass else GateStatus.FAIL
        gates.append(
            GateResult(
                gate_name=self.GATE_2_DETERMINISM["name"],
                gate_number=2,
                status=gate_2_status,
                threshold=self.GATE_2_DETERMINISM["threshold"] * 100,
                actual_value=determinism_drift_pct,
                passed=gate_2_pass,
                evidence={
                    "determinism_drift_pct": determinism_drift_pct,
                    "num_seeds_tested": num_samples,
                    "description": self.GATE_2_DETERMINISM["description"],
                },
                notes=(
                    f"Determinism drift {determinism_drift_pct:.3f}% "
                    f"(threshold: <{self.GATE_2_DETERMINISM['threshold']*100:.2f}%)"
                ),
            )
        )

        # Gate 3: Latency Acceptable
        gate_3_pass = latency_ratio < self.GATE_3_LATENCY["threshold"]
        gate_3_status = GateStatus.PASS if gate_3_pass else GateStatus.FAIL
        gates.append(
            GateResult(
                gate_name=self.GATE_3_LATENCY["name"],
                gate_number=3,
                status=gate_3_status,
                threshold=self.GATE_3_LATENCY["threshold"],
                actual_value=latency_ratio,
                passed=gate_3_pass,
                evidence={
                    "latency_ratio": latency_ratio,
                    "num_samples": num_samples,
                    "description": self.GATE_3_LATENCY["description"],
                },
                notes=(
                    f"Latency ratio {latency_ratio:.2f}x "
                    f"(threshold: <{self.GATE_3_LATENCY['threshold']:.1f}x)"
                ),
            )
        )

        # Determine readiness
        all_passed = all(g.passed for g in gates)
        ready_for_promotion = all_passed and num_samples >= 50

        if ready_for_promotion:
            recommendation = (
                "✅ READY FOR PHASE 6 PROMOTION: All gates passed, "
                "sufficient samples collected"
            )
        elif all_passed:
            recommendation = (
                f"⚠️  GATES PASSED but insufficient samples ({num_samples}/50). "
                "Collect more data before promotion."
            )
        else:
            failed_gates = [g.gate_number for g in gates if not g.passed]
            recommendation = (
                f"❌ GATES FAILED: Gates {failed_gates} did not meet thresholds. "
                "Investigate and retry after tuning."
            )

        report = PromotionGateReport(
            evaluation_id=evaluation_id,
            gates=gates,
            all_passed=all_passed,
            ready_for_promotion=ready_for_promotion,
            recommendation=recommendation,
            details=metadata or {},
        )

        self._gate_history.append(report)
        logger.info(
            f"Gate evaluation {evaluation_id}: "
            f"{'✅ PASS' if all_passed else '❌ FAIL'} | "
            f"Gate 1: {gate_1_status.value}, "
            f"Gate 2: {gate_2_status.value}, "
            f"Gate 3: {gate_3_status.value}"
        )

        return report

    def get_gate_history(self) -> list[PromotionGateReport]:
        """Get history of gate evaluations"""
        return self._gate_history.copy()

    def get_latest_evaluation(self) -> PromotionGateReport | None:
        """Get most recent gate evaluation"""
        return self._gate_history[-1] if self._gate_history else None
