"""Observability Plane: Real-time telemetry and anomaly detection.

Collects transfer metrics, detects anomalies, and triggers quarantine
when repeated failures occur.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TelemetryMetric:
    """Single telemetry metric."""

    metric_name: str
    value: float
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp": self.timestamp,
        }


@dataclass
class Anomaly:
    """Detected anomaly."""

    anomaly_type: str
    severity: str
    message: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp,
        }


@dataclass
class ObservabilityReport:
    """Complete observability report."""

    telemetry: Dict[str, float] = field(default_factory=dict)
    anomalies: List[Anomaly] = field(default_factory=list)
    quarantine: bool = False
    quarantine_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "telemetry": self.telemetry,
            "anomalies": [a.to_dict() for a in self.anomalies],
            "quarantine": self.quarantine,
            "quarantine_reason": self.quarantine_reason,
        }


class ObservabilityPlane:
    """Collects telemetry and detects anomalies in transfers."""

    ANOMALY_THRESHOLD = 3
    SLOW_TRANSFER_THRESHOLD_MS = 5000

    def __init__(self):
        """Initialize observability plane."""
        self.metrics: Dict[str, List[TelemetryMetric]] = {}
        self.transfer_failures: Dict[str, int] = {}
        self.transfer_latencies: Dict[str, List[float]] = {}
        self.quarantined_transfers: set = set()

    def record_metric(self, transfer_id: str, metric_name: str, value: float) -> None:
        """Record a telemetry metric."""
        if transfer_id not in self.metrics:
            self.metrics[transfer_id] = []

        metric = TelemetryMetric(metric_name=metric_name, value=value)
        self.metrics[transfer_id].append(metric)
        logger.debug(f"Metric recorded: {transfer_id}/{metric_name}={value}")

    def record_error(self, transfer_id: str) -> None:
        """Record transfer error."""
        if transfer_id not in self.transfer_failures:
            self.transfer_failures[transfer_id] = 0

        self.transfer_failures[transfer_id] += 1
        logger.warning(f"Error recorded: {transfer_id}")

    def record_latency(self, transfer_id: str, latency_ms: float) -> None:
        """Record transfer latency."""
        if transfer_id not in self.transfer_latencies:
            self.transfer_latencies[transfer_id] = []

        self.transfer_latencies[transfer_id].append(latency_ms)

    def detect_anomalies(self, transfer_id: str) -> List[Anomaly]:
        """Detect anomalies for a transfer."""
        anomalies = []

        consecutive_failures = self.transfer_failures.get(transfer_id, 0)
        if consecutive_failures > 0:
            anomaly = Anomaly(
                anomaly_type="repeated_failures",
                severity="high",
                message=f"{consecutive_failures} consecutive failures detected",
            )
            anomalies.append(anomaly)
            logger.warning(f"Anomaly detected: {transfer_id} - {anomaly.message}")

        latencies = self.transfer_latencies.get(transfer_id, [])
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            if avg_latency > self.SLOW_TRANSFER_THRESHOLD_MS:
                anomaly = Anomaly(
                    anomaly_type="slow_transfer",
                    severity="medium",
                    message=f"Average latency {avg_latency}ms exceeds threshold "
                    f"{self.SLOW_TRANSFER_THRESHOLD_MS}ms",
                )
                anomalies.append(anomaly)

        return anomalies

    def check_quarantine(self, transfer_id: str) -> bool:
        """Check if transfer should be quarantined."""
        if transfer_id in self.quarantined_transfers:
            return True

        failures = self.transfer_failures.get(transfer_id, 0)
        if failures >= self.ANOMALY_THRESHOLD:
            self.quarantined_transfers.add(transfer_id)
            logger.error(f"Transfer quarantined: {transfer_id}")
            return True

        return False

    def generate_report(self, transfer_id: str) -> ObservabilityReport:
        """Generate complete observability report."""
        report = ObservabilityReport()

        if transfer_id in self.metrics:
            for metric in self.metrics[transfer_id]:
                report.telemetry[metric.metric_name] = metric.value

        anomalies = self.detect_anomalies(transfer_id)
        report.anomalies = anomalies

        report.quarantine = self.check_quarantine(transfer_id)
        if report.quarantine:
            report.quarantine_reason = (
                f"{self.transfer_failures.get(transfer_id, 0)} failures "
                "on this transfer"
            )

        logger.info(
            f"Report generated for {transfer_id}: "
            f"{len(report.anomalies)} anomalies, quarantine={report.quarantine}"
        )
        return report

    def get_metrics(self, transfer_id: str) -> List[TelemetryMetric]:
        """Get all metrics for a transfer."""
        return self.metrics.get(transfer_id, []).copy()

    def clear_transfer_state(self, transfer_id: str) -> None:
        """Clear state for a transfer."""
        if transfer_id in self.metrics:
            del self.metrics[transfer_id]
        if transfer_id in self.transfer_failures:
            del self.transfer_failures[transfer_id]
        if transfer_id in self.transfer_latencies:
            del self.transfer_latencies[transfer_id]
        if transfer_id in self.quarantined_transfers:
            self.quarantined_transfers.remove(transfer_id)

        logger.info(f"Transfer state cleared: {transfer_id}")

    def get_transfer_error_count(self, transfer_id: str) -> int:
        """Get error count for transfer."""
        return self.transfer_failures.get(transfer_id, 0)

    def get_avg_latency(self, transfer_id: str) -> float:
        """Get average latency for transfer."""
        latencies = self.transfer_latencies.get(transfer_id, [])
        if not latencies:
            return 0.0
        return sum(latencies) / len(latencies)
