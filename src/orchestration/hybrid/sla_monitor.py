"""
Phase 6: SLA Monitoring

Tracks SLA compliance for quantum-hybrid operations with instant rollback.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class SLAMetric(Enum):
    """SLA metric types"""

    SUCCESS_RATE = "success_rate"
    LATENCY = "latency"
    CORRECTNESS = "correctness"
    FALLBACK_SUCCESS = "fallback_success"


class ComplianceStatus(Enum):
    """SLA compliance status"""

    COMPLIANT = "compliant"
    APPROACHING_BREACH = "approaching_breach"
    BREACHED = "breached"
    CRITICAL = "critical"


@dataclass
class SLAThreshold:
    """SLA threshold definition"""

    metric: SLAMetric
    min_value: float  # Minimum acceptable value
    warning_threshold: float  # Warning when below this
    breach_threshold: float  # Breach when below this
    description: str = ""


@dataclass
class SLAMeasurement:
    """Single SLA measurement"""

    metric: SLAMetric
    value: float
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SLAReport:
    """SLA compliance report"""

    report_id: str
    canary_percentage: float  # Current canary percentage (1, 5, 25, 100)
    measurements: list[SLAMeasurement]
    compliance_status: ComplianceStatus
    metrics_summary: dict[str, float]
    breaches_detected: list[str]
    fallback_triggered: bool
    recommendation: str
    timestamp: float = field(default_factory=time.time)


class SLAMonitor:
    """Monitors SLA compliance for quantum-hybrid cohorts"""

    def __init__(self, fallback_fn: Optional[Callable[[], bool]] = None):
        self.fallback_fn = fallback_fn or self._default_fallback
        self._measurements: list[SLAMeasurement] = []
        self._reports: list[SLAReport] = []
        self._thresholds = {
            SLAMetric.SUCCESS_RATE: SLAThreshold(
                metric=SLAMetric.SUCCESS_RATE,
                min_value=0.99,  # 99% minimum
                warning_threshold=0.995,  # Warn at <99.5%
                breach_threshold=0.990,  # Breach at <99%
                description="Success rate must remain above 99%",
            ),
            SLAMetric.LATENCY: SLAThreshold(
                metric=SLAMetric.LATENCY,
                min_value=2000.0,  # Max 2 seconds in ms
                warning_threshold=1500.0,  # Warn when >1.5s
                breach_threshold=2000.0,  # Breach when >2s
                description="Latency must stay under 2 seconds",
            ),
            SLAMetric.CORRECTNESS: SLAThreshold(
                metric=SLAMetric.CORRECTNESS,
                min_value=0.999,  # 99.9% correctness
                warning_threshold=0.9995,  # Warn at <99.95%
                breach_threshold=0.999,  # Breach at <99.9%
                description="Correctness must exceed 99.9%",
            ),
            SLAMetric.FALLBACK_SUCCESS: SLAThreshold(
                metric=SLAMetric.FALLBACK_SUCCESS,
                min_value=1.0,  # 100% fallback success
                warning_threshold=0.99,  # Warn at <99%
                breach_threshold=0.99,  # Breach at <99%
                description="Fallback must succeed 99%+ of time",
            ),
        }

    def record_measurement(
        self,
        metric: SLAMetric,
        value: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record an SLA measurement"""
        
        measurement = SLAMeasurement(
            metric=metric,
            value=value,
            metadata=metadata or {},
        )
        self._measurements.append(measurement)

    def evaluate_compliance(
        self,
        canary_percentage: float,
        window_seconds: int = 300,
    ) -> SLAReport:
        """Evaluate current SLA compliance"""

        report_id = f"sla_report_{len(self._reports)}"
        now = time.time()
        window_start = now - window_seconds

        # Filter measurements in window
        recent = [
            m for m in self._measurements
            if m.timestamp >= window_start
        ]

        metrics_summary = {}
        breaches = []

        # Evaluate each metric
        for metric_type, threshold in self._thresholds.items():
            metric_measurements = [m for m in recent if m.metric == metric_type]

            if not metric_measurements:
                # No data - assume OK but warn
                metrics_summary[metric_type.value] = 1.0
                continue

            # Calculate average for this metric
            avg_value = sum(m.value for m in metric_measurements) / len(
                metric_measurements
            )
            metrics_summary[metric_type.value] = avg_value

            # Check thresholds
            if avg_value < threshold.breach_threshold:
                breaches.append(
                    f"{metric_type.value}: {avg_value:.3f} "
                    f"(threshold: {threshold.breach_threshold:.3f})"
                )
            elif avg_value < threshold.warning_threshold:
                logger.warning(
                    f"{metric_type.value} approaching breach: {avg_value:.3f}"
                )

        # Determine compliance status
        if not recent:
            compliance_status = ComplianceStatus.APPROACHING_BREACH
            recommendation = "Insufficient data for compliance evaluation"
            fallback_triggered = False
        elif breaches:
            compliance_status = ComplianceStatus.BREACHED
            recommendation = (
                f"SLA BREACH DETECTED: {len(breaches)} metric(s) violated. "
                "Triggering fallback to classical solver."
            )
            fallback_triggered = self.fallback_fn()
        elif any(
            metrics_summary.get(m.metric.value, 1.0) < m.warning_threshold
            for m in self._thresholds.values()
        ):
            compliance_status = ComplianceStatus.APPROACHING_BREACH
            recommendation = "Approaching SLA threshold - monitor closely"
            fallback_triggered = False
        else:
            compliance_status = ComplianceStatus.COMPLIANT
            recommendation = f"SLA COMPLIANT at {canary_percentage*100:.0f}% canary"
            fallback_triggered = False

        report = SLAReport(
            report_id=report_id,
            canary_percentage=canary_percentage,
            measurements=recent,
            compliance_status=compliance_status,
            metrics_summary=metrics_summary,
            breaches_detected=breaches,
            fallback_triggered=fallback_triggered,
            recommendation=recommendation,
        )

        self._reports.append(report)
        logger.info(
            f"SLA evaluation: {compliance_status.value} | "
            f"Fallback: {'triggered' if fallback_triggered else 'not triggered'}"
        )

        return report

    def _default_fallback(self) -> bool:
        """Default fallback implementation"""
        logger.error("SLA fallback triggered - returning to classical solver")
        return True

    def get_latest_report(self) -> SLAReport | None:
        """Get most recent SLA report"""
        return self._reports[-1] if self._reports else None

    def get_compliance_history(self) -> list[SLAReport]:
        """Get history of SLA reports"""
        return self._reports.copy()
