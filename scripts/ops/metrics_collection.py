"""
Metrics Collection Framework: Real-time Monitoring & Alerting

Provides:
- Real-time metrics collection from test runs
- Prometheus-compatible metrics export
- Threshold-based alerting
- Metrics aggregation and reporting
- Dashboard-compatible JSON output

Author: AI Agent Process Phase 9.3
Version: 1.0.0-baseline
"""

from __future__ import annotations

import json
import logging
import os
import psutil
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# ============================================================================
# Metrics Data Classes
# ============================================================================


@dataclass
class CPUMetrics:
    """CPU performance metrics."""

    percent: float
    count: int
    freq_current: float = 0.0
    context_switches: int = 0

    @staticmethod
    def collect() -> CPUMetrics:
        """Collect CPU metrics."""
        return CPUMetrics(
            percent=psutil.cpu_percent(interval=0.1),
            count=psutil.cpu_count(logical=True) or 1,
        )


@dataclass
class MemoryMetrics:
    """Memory metrics."""

    total_mb: float
    used_mb: float
    available_mb: float
    percent: float
    process_mb: float = 0.0

    @staticmethod
    def collect(process: Optional[psutil.Process] = None) -> MemoryMetrics:
        """Collect memory metrics."""
        vm = psutil.virtual_memory()
        process_mb = 0.0

        if process:
            try:
                process_mb = process.memory_info().rss / 1024 / 1024
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return MemoryMetrics(
            total_mb=vm.total / 1024 / 1024,
            used_mb=vm.used / 1024 / 1024,
            available_mb=vm.available / 1024 / 1024,
            percent=vm.percent,
            process_mb=process_mb,
        )


@dataclass
class NetworkMetrics:
    """Network metrics."""

    bytes_sent: int = 0
    bytes_recv: int = 0
    packets_sent: int = 0
    packets_recv: int = 0
    connections: int = 0

    @staticmethod
    def collect() -> NetworkMetrics:
        """Collect network metrics."""
        net = psutil.net_io_counters()
        connections = len(psutil.net_connections(kind="inet"))

        return NetworkMetrics(
            bytes_sent=net.bytes_sent,
            bytes_recv=net.bytes_recv,
            packets_sent=net.packets_sent,
            packets_recv=net.packets_recv,
            connections=connections,
        )


@dataclass
class LatencyMetrics:
    """Request latency metrics."""

    count: int = 0
    total_ms: float = 0.0
    min_ms: float = float("inf")
    max_ms: float = 0.0
    sum_squared: float = 0.0

    def add_sample(self, latency_ms: float) -> None:
        """Add a latency sample."""
        self.count += 1
        self.total_ms += latency_ms
        self.min_ms = min(self.min_ms, latency_ms)
        self.max_ms = max(self.max_ms, latency_ms)
        self.sum_squared += latency_ms * latency_ms

    def get_avg(self) -> float:
        """Get average latency."""
        return self.total_ms / self.count if self.count > 0 else 0.0

    def get_stddev(self) -> float:
        """Get standard deviation."""
        if self.count <= 1:
            return 0.0
        avg = self.get_avg()
        variance = (self.sum_squared / self.count) - (avg * avg)
        return variance**0.5


@dataclass
class ThroughputMetrics:
    """Throughput metrics."""

    requests: int = 0
    successes: int = 0
    failures: int = 0
    bytes_processed: int = 0

    def get_success_rate(self) -> float:
        """Get success rate (0-1)."""
        if self.requests == 0:
            return 0.0
        return self.successes / self.requests


@dataclass
class SystemMetrics:
    """Complete system metrics snapshot."""

    timestamp: float
    timestamp_iso: str
    cpu: CPUMetrics
    memory: MemoryMetrics
    network: NetworkMetrics
    latency: LatencyMetrics
    throughput: ThroughputMetrics

    @staticmethod
    def collect(
        process: Optional[psutil.Process] = None,
    ) -> SystemMetrics:
        """Collect all system metrics."""
        now = time.time()
        return SystemMetrics(
            timestamp=now,
            timestamp_iso=datetime.fromtimestamp(now).isoformat(),
            cpu=CPUMetrics.collect(),
            memory=MemoryMetrics.collect(process),
            network=NetworkMetrics.collect(),
            latency=LatencyMetrics(),
            throughput=ThroughputMetrics(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "timestamp_iso": self.timestamp_iso,
            "cpu": asdict(self.cpu),
            "memory": asdict(self.memory),
            "network": asdict(self.network),
            "latency": {
                "count": self.latency.count,
                "avg_ms": self.latency.get_avg(),
                "stddev_ms": self.latency.get_stddev(),
                "min_ms": self.latency.min_ms if self.latency.count > 0 else 0,
                "max_ms": self.latency.max_ms,
            },
            "throughput": asdict(self.throughput),
        }


# ============================================================================
# Metrics Thresholds & Alerting
# ============================================================================


@dataclass
class AlertThresholds:
    """Alert thresholds for metrics."""

    cpu_percent_warn: float = 75.0
    cpu_percent_crit: float = 90.0
    memory_percent_warn: float = 75.0
    memory_percent_crit: float = 90.0
    error_rate_warn: float = 0.05  # 5%
    error_rate_crit: float = 0.10  # 10%
    latency_p99_warn_ms: float = 1000.0
    latency_p99_crit_ms: float = 5000.0


@dataclass
class Alert:
    """Alert event."""

    timestamp: float
    level: str  # warning, critical
    metric: str
    value: float
    threshold: float
    message: str


class AlertManager:
    """Manages alert generation and tracking."""

    def __init__(self, thresholds: AlertThresholds) -> None:
        """Initialize alert manager."""
        self.thresholds = thresholds
        self.alerts: list[Alert] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def check_metrics(self, metrics: SystemMetrics) -> list[Alert]:
        """Check metrics against thresholds and generate alerts."""
        new_alerts = []

        # CPU checks
        if metrics.cpu.percent >= self.thresholds.cpu_percent_crit:
            new_alerts.append(
                Alert(
                    timestamp=metrics.timestamp,
                    level="critical",
                    metric="cpu_percent",
                    value=metrics.cpu.percent,
                    threshold=self.thresholds.cpu_percent_crit,
                    message=f"CPU usage critical: {metrics.cpu.percent}%",
                )
            )
        elif metrics.cpu.percent >= self.thresholds.cpu_percent_warn:
            new_alerts.append(
                Alert(
                    timestamp=metrics.timestamp,
                    level="warning",
                    metric="cpu_percent",
                    value=metrics.cpu.percent,
                    threshold=self.thresholds.cpu_percent_warn,
                    message=f"CPU usage warning: {metrics.cpu.percent}%",
                )
            )

        # Memory checks
        if metrics.memory.percent >= self.thresholds.memory_percent_crit:
            new_alerts.append(
                Alert(
                    timestamp=metrics.timestamp,
                    level="critical",
                    metric="memory_percent",
                    value=metrics.memory.percent,
                    threshold=self.thresholds.memory_percent_crit,
                    message=f"Memory usage critical: {metrics.memory.percent}%",
                )
            )
        elif metrics.memory.percent >= self.thresholds.memory_percent_warn:
            new_alerts.append(
                Alert(
                    timestamp=metrics.timestamp,
                    level="warning",
                    metric="memory_percent",
                    value=metrics.memory.percent,
                    threshold=self.thresholds.memory_percent_warn,
                    message=f"Memory usage warning: {metrics.memory.percent}%",
                )
            )

        # Error rate checks
        error_rate = 1.0 - metrics.throughput.get_success_rate()
        if error_rate >= self.thresholds.error_rate_crit:
            new_alerts.append(
                Alert(
                    timestamp=metrics.timestamp,
                    level="critical",
                    metric="error_rate",
                    value=error_rate,
                    threshold=self.thresholds.error_rate_crit,
                    message=f"Error rate critical: {error_rate*100:.1f}%",
                )
            )
        elif error_rate >= self.thresholds.error_rate_warn:
            new_alerts.append(
                Alert(
                    timestamp=metrics.timestamp,
                    level="warning",
                    metric="error_rate",
                    value=error_rate,
                    threshold=self.thresholds.error_rate_warn,
                    message=f"Error rate warning: {error_rate*100:.1f}%",
                )
            )

        # Log and store alerts
        for alert in new_alerts:
            self.logger.log(
                logging.CRITICAL if alert.level == "critical" else logging.WARNING,
                alert.message,
            )
            self.alerts.append(alert)

        return new_alerts


# ============================================================================
# Metrics Collector
# ============================================================================


class MetricsCollector:
    """Collects and aggregates metrics from test runs."""

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        collection_interval_sec: float = 5.0,
    ) -> None:
        """Initialize metrics collector."""
        self.output_dir = output_dir or Path(".codex/metrics")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.collection_interval_sec = collection_interval_sec
        self.logger = logging.getLogger(self.__class__.__name__)

        self.metrics_history: list[SystemMetrics] = []
        self.alert_manager = AlertManager(AlertThresholds())
        self.process = psutil.Process(os.getpid())
        self.running = False

    def collect_snapshot(self) -> SystemMetrics:
        """Collect a single metrics snapshot."""
        return SystemMetrics.collect(process=self.process)

    def add_request_latency(self, latency_ms: float) -> None:
        """Add request latency to latest metrics."""
        if self.metrics_history:
            self.metrics_history[-1].latency.add_sample(latency_ms)

    def record_request(self, success: bool = True, bytes_count: int = 0) -> None:
        """Record a request completion."""
        if self.metrics_history:
            tp = self.metrics_history[-1].throughput
            tp.requests += 1
            if success:
                tp.successes += 1
            else:
                tp.failures += 1
            tp.bytes_processed += bytes_count

    def get_latest(self) -> Optional[SystemMetrics]:
        """Get latest metrics snapshot."""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_summary(self) -> dict[str, Any]:
        """Get summary of collected metrics."""
        if not self.metrics_history:
            return {"message": "No metrics collected"}

        latest = self.metrics_history[-1]
        first = self.metrics_history[0]
        duration = latest.timestamp - first.timestamp

        # Aggregate latency metrics
        all_latencies = []
        for m in self.metrics_history:
            for _ in range(m.latency.count):
                all_latencies.append(m.latency.get_avg())

        return {
            "collection_start": first.timestamp_iso,
            "collection_end": latest.timestamp_iso,
            "duration_sec": duration,
            "snapshots": len(self.metrics_history),
            "cpu": {
                "current_percent": latest.cpu.percent,
                "avg_percent": (
                    sum(m.cpu.percent for m in self.metrics_history)
                    / len(self.metrics_history)
                ),
                "max_percent": max(m.cpu.percent for m in self.metrics_history),
            },
            "memory": {
                "current_mb": latest.memory.used_mb,
                "peak_mb": max(m.memory.used_mb for m in self.metrics_history),
                "current_percent": latest.memory.percent,
            },
            "network": {
                "total_bytes_sent": latest.network.bytes_sent,
                "total_bytes_recv": latest.network.bytes_recv,
                "connections": latest.network.connections,
            },
            "throughput": {
                "total_requests": latest.throughput.requests,
                "success_rate": latest.throughput.get_success_rate(),
                "failures": latest.throughput.failures,
            },
            "alerts": len(self.alert_manager.alerts),
        }

    def to_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        # Type definitions
        lines.append("# HELP system_cpu_percent CPU usage percentage")
        lines.append("# TYPE system_cpu_percent gauge")

        # Metrics
        for i, m in enumerate(self.metrics_history):
            timestamp_ms = int(m.timestamp * 1000)
            lines.append(
                f'system_cpu_percent{{instance="test"}} {m.cpu.percent} {timestamp_ms}'
            )
            lines.append(
                f'system_memory_mb{{instance="test"}} {m.memory.used_mb} {timestamp_ms}'
            )
            lines.append(
                f'request_latency_p99_ms{{instance="test"}} '
                f'{m.latency.get_avg()} {timestamp_ms}'
            )
            lines.append(
                f'request_success_rate{{instance="test"}} '
                f'{m.throughput.get_success_rate()} {timestamp_ms}'
            )

        return "\n".join(lines)

    def export_json(self, filename: Optional[str] = None) -> str:
        """Export metrics to JSON file."""
        if filename is None:
            filename = f"metrics_{int(time.time())}.json"

        filepath = self.output_dir / filename
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "snapshots": [m.to_dict() for m in self.metrics_history],
            "alerts": [
                {
                    "timestamp": a.timestamp,
                    "level": a.level,
                    "metric": a.metric,
                    "value": a.value,
                    "threshold": a.threshold,
                    "message": a.message,
                }
                for a in self.alert_manager.alerts
            ],
        }

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Metrics exported to {filepath}")
        return str(filepath)

    def export_prometheus(self, filename: Optional[str] = None) -> str:
        """Export metrics in Prometheus format."""
        if filename is None:
            filename = f"metrics_{int(time.time())}.prom"

        filepath = self.output_dir / filename
        with open(filepath, "w") as f:
            f.write(self.to_prometheus_format())

        self.logger.info(f"Prometheus metrics exported to {filepath}")
        return str(filepath)


# ============================================================================
# Real-time Dashboard Data
# ============================================================================


class DashboardDataProvider:
    """Provides real-time data for monitoring dashboards."""

    def __init__(self, collector: MetricsCollector) -> None:
        """Initialize dashboard data provider."""
        self.collector = collector

    def get_dashboard_state(self) -> dict[str, Any]:
        """Get current dashboard state."""
        latest = self.collector.get_latest()
        if not latest:
            return {"status": "no_data"}

        return {
            "status": "running",
            "timestamp": latest.timestamp_iso,
            "system": {
                "cpu_percent": latest.cpu.percent,
                "memory_mb": latest.memory.used_mb,
                "memory_percent": latest.memory.percent,
                "active_connections": latest.network.connections,
            },
            "performance": {
                "request_latency_p99_ms": latest.latency.get_avg(),
                "request_success_rate": latest.throughput.get_success_rate(),
                "throughput_requests": latest.throughput.requests,
            },
            "alerts": {
                "critical": sum(
                    1 for a in self.collector.alert_manager.alerts
                    if a.level == "critical"
                ),
                "warning": sum(
                    1 for a in self.collector.alert_manager.alerts
                    if a.level == "warning"
                ),
            },
        }


# ============================================================================
# CLI Interface
# ============================================================================


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("main")

    # Create collector and collect some sample metrics
    collector = MetricsCollector()

    logger.info("Collecting metrics for 30 seconds...")
    for i in range(6):
        snapshot = collector.collect_snapshot()
        collector.metrics_history.append(snapshot)

        # Simulate some requests
        for _ in range(10):
            collector.add_request_latency(50.0 + (i * 10.0))
            collector.record_request(success=(i < 5), bytes_count=1024)

        time.sleep(5.0)
        logger.info(f"Collected snapshot {i + 1}")

    # Export results
    json_file = collector.export_json()
    prom_file = collector.export_prometheus()

    logger.info("Summary:")
    logger.info(json.dumps(collector.get_summary(), indent=2))

    sys.exit(0)
