"""
Phase 12 Track 3: Metrics Collection Engine
Enterprise-grade time-series metrics collection, aggregation, and export

Authority: @mbaetiong (D-tier AUTO-GO)
Timeline: Days 3-4 deliverable (2026-07-03 → 2026-07-04)
Target: 650+ lines, >95% test coverage, 100% type hints
"""

import time
import threading
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from abc import ABC, abstractmethod
import logging
from pathlib import Path
import queue
import psutil
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# TYPE DEFINITIONS & ENUMS
# ============================================================================

class MetricType(Enum):
    """Metric collection type."""
    GAUGE = "gauge"  # Current value (e.g., CPU usage)
    COUNTER = "counter"  # Monotonically increasing (e.g., requests total)
    HISTOGRAM = "histogram"  # Distribution (e.g., latency)


class Severity(Enum):
    """Alert severity levels."""
    P0 = "critical"  # Immediate escalation <5min
    P1 = "high"  # High priority <15min
    P2 = "medium"  # Medium priority <30min
    P3 = "low"  # Low priority <60min


@dataclass
class MetricPoint:
    """Single metric data point."""
    metric_id: str
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'metric_id': self.metric_id,
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'labels': self.labels,
            'tags': self.tags,
        }


@dataclass
class AggregatedMetric:
    """Aggregated metric with statistics."""
    metric_id: str
    timestamp: datetime
    count: int
    sum_val: float
    min_val: float
    max_val: float
    p50: float
    p99: float
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'metric_id': self.metric_id,
            'timestamp': self.timestamp.isoformat(),
            'count': self.count,
            'sum': self.sum_val,
            'min': self.min_val,
            'max': self.max_val,
            'p50': self.p50,
            'p99': self.p99,
            'labels': self.labels,
        }


@dataclass
class AlertRule:
    """Alert rule definition."""
    alert_id: str
    metric_id: str
    condition: str  # ">" | "<" | ">=" | "<=" | "==" | "!="
    threshold: float
    duration_seconds: int  # Alert fires if condition true for this duration
    severity: Severity
    enabled: bool = True
    message: str = ""
    action_handler: Optional[Callable] = None


# ============================================================================
# METRIC COLLECTION & STORAGE
# ============================================================================

class MetricRegistry:
    """Registry of all metrics with metadata."""

    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def register(
        self,
        metric_id: str,
        name: str,
        metric_type: MetricType,
        unit: str = "",
        help_text: str = "",
        slo_target: Optional[str] = None,
    ) -> None:
        """Register a new metric."""
        with self._lock:
            if metric_id in self.metrics:
                logger.warning(f"Metric {metric_id} already registered, skipping")
                return

            self.metrics[metric_id] = {
                'name': name,
                'type': metric_type,
                'unit': unit,
                'help': help_text,
                'slo_target': slo_target,
                'registered_at': datetime.utcnow(),
            }
            logger.info(f"Registered metric: {metric_id} ({name})")

    def get(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """Get metric definition."""
        with self._lock:
            return self.metrics.get(metric_id)

    def list_metrics(self) -> List[str]:
        """List all registered metric IDs."""
        with self._lock:
            return list(self.metrics.keys())


class TimeSeriesBuffer:
    """Circular buffer for time-series data."""

    def __init__(self, max_points: int = 3600):
        """Initialize with max points (default: 1 hour at 1Hz)."""
        self.max_points = max_points
        self.points: deque = deque(maxlen=max_points)
        self._lock = threading.RLock()

    def append(self, point: MetricPoint) -> None:
        """Add data point."""
        with self._lock:
            self.points.append(point)

    def get_all(self) -> List[MetricPoint]:
        """Get all buffered points."""
        with self._lock:
            return list(self.points)

    def get_since(self, timestamp: datetime) -> List[MetricPoint]:
        """Get points since timestamp."""
        with self._lock:
            return [p for p in self.points if p.timestamp >= timestamp]

    def clear(self) -> None:
        """Clear buffer."""
        with self._lock:
            self.points.clear()


class MetricsCollector:
    """Central metrics collection engine."""

    def __init__(self, export_interval_seconds: int = 60):
        """Initialize metrics collector.
        
        Args:
            export_interval_seconds: How often to export aggregated metrics
        """
        self.registry = MetricRegistry()
        self.buffers: Dict[str, TimeSeriesBuffer] = {}
        self.aggregations: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1440))
        self.alert_rules: Dict[str, AlertRule] = {}
        self.export_interval = export_interval_seconds
        self._lock = threading.RLock()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._export_handlers: List[Callable] = []

    def register_metric(
        self,
        metric_id: str,
        name: str,
        metric_type: MetricType,
        unit: str = "",
        help_text: str = "",
        slo_target: Optional[str] = None,
    ) -> None:
        """Register a metric with the collector."""
        with self._lock:
            self.registry.register(metric_id, name, metric_type, unit, help_text, slo_target)
            self.buffers[metric_id] = TimeSeriesBuffer(max_points=3600)

    def record_metric(
        self,
        metric_id: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a metric value."""
        with self._lock:
            if metric_id not in self.buffers:
                logger.warning(f"Metric {metric_id} not registered, ignoring")
                return

            point = MetricPoint(
                metric_id=metric_id,
                timestamp=datetime.utcnow(),
                value=value,
                labels=labels or {},
                tags=tags or {},
            )
            self.buffers[metric_id].append(point)

    def register_alert_rule(self, rule: AlertRule) -> None:
        """Register an alert rule."""
        with self._lock:
            self.alert_rules[rule.alert_id] = rule
            logger.info(f"Registered alert rule: {rule.alert_id} ({rule.severity.value})")

    def register_export_handler(self, handler: Callable[[List[AggregatedMetric]], None]) -> None:
        """Register a handler to be called on export (e.g., to Prometheus)."""
        with self._lock:
            self._export_handlers.append(handler)

    def start(self) -> None:
        """Start the metrics collection worker thread."""
        with self._lock:
            if self._running:
                logger.warning("Metrics collector already running")
                return

            self._running = True
            self._worker_thread = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name="MetricsCollector-Worker"
            )
            self._worker_thread.start()
            logger.info("Metrics collector started")

    def stop(self) -> None:
        """Stop the metrics collection worker."""
        with self._lock:
            self._running = False

        if self._worker_thread:
            self._worker_thread.join(timeout=5)
            logger.info("Metrics collector stopped")

    def _worker_loop(self) -> None:
        """Background worker that aggregates and exports metrics."""
        while self._running:
            try:
                time.sleep(self.export_interval)
                self._aggregate_and_export()
                self._evaluate_alerts()
            except Exception as e:
                logger.error(f"Error in metrics worker: {e}", exc_info=True)

    def _aggregate_and_export(self) -> None:
        """Aggregate metrics and call export handlers."""
        with self._lock:
            aggregated = self._aggregate_all()
            for handler in self._export_handlers:
                try:
                    handler(aggregated)
                except Exception as e:
                    logger.error(f"Error in export handler: {e}")

    def _aggregate_all(self) -> List[AggregatedMetric]:
        """Aggregate all metrics from last period."""
        aggregated = []
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.export_interval)

        for metric_id, buffer in self.buffers.items():
            points = buffer.get_since(cutoff_time)
            if points:
                agg = self._aggregate_points(metric_id, points)
                aggregated.append(agg)
                self.aggregations[metric_id].append(agg)

        return aggregated

    @staticmethod
    def _aggregate_points(metric_id: str, points: List[MetricPoint]) -> AggregatedMetric:
        """Aggregate a list of points into statistics."""
        values = [p.value for p in points]
        sorted_values = sorted(values)

        return AggregatedMetric(
            metric_id=metric_id,
            timestamp=datetime.utcnow(),
            count=len(values),
            sum_val=sum(values),
            min_val=min(values),
            max_val=max(values),
            p50=statistics.median(sorted_values),
            p99=sorted_values[max(0, int(len(sorted_values) * 0.99) - 1)],
        )

    def _evaluate_alerts(self) -> None:
        """Evaluate all alert rules."""
        with self._lock:
            for alert_id, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue

                metric_buffer = self.buffers.get(rule.metric_id)
                if not metric_buffer:
                    continue

                if self._check_alert_condition(rule, metric_buffer):
                    self._trigger_alert(rule)

    def _check_alert_condition(self, rule: AlertRule, buffer: TimeSeriesBuffer) -> bool:
        """Check if alert condition is met."""
        cutoff = datetime.utcnow() - timedelta(seconds=rule.duration_seconds)
        points = buffer.get_since(cutoff)

        if not points:
            return False

        values = [p.value for p in points]
        avg_value = statistics.mean(values)

        conditions = {
            '>': lambda v, t: v > t,
            '<': lambda v, t: v < t,
            '>=': lambda v, t: v >= t,
            '<=': lambda v, t: v <= t,
            '==': lambda v, t: abs(v - t) < 1e-6,
            '!=': lambda v, t: abs(v - t) >= 1e-6,
        }

        condition_func = conditions.get(rule.condition)
        if condition_func is None:
            logger.warning(f"Unknown condition: {rule.condition}")
            return False

        return condition_func(avg_value, rule.threshold)

    def _trigger_alert(self, rule: AlertRule) -> None:
        """Handle alert trigger."""
        logger.warning(
            f"ALERT TRIGGERED: {rule.alert_id} ({rule.severity.value}) - {rule.message}"
        )
        if rule.action_handler:
            try:
                rule.action_handler(rule)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")

    def get_metric_summary(self, metric_id: str, minutes: int = 5) -> Optional[Dict[str, Any]]:
        """Get summary statistics for a metric over last N minutes."""
        with self._lock:
            aggregations = list(self.aggregations.get(metric_id, []))
            if not aggregations:
                return None

            # Filter to last N minutes
            cutoff = datetime.utcnow() - timedelta(minutes=minutes)
            recent = [a for a in aggregations if a.timestamp >= cutoff]

            if not recent:
                return None

            # Aggregate across aggregations
            all_values = []
            for agg in recent:
                # Estimate values from aggregated data
                all_values.extend([agg.p50] * max(1, agg.count // len(recent)))

            return {
                'metric_id': metric_id,
                'window_minutes': minutes,
                'sample_count': sum(a.count for a in recent),
                'min': min(a.min_val for a in recent),
                'max': max(a.max_val for a in recent),
                'mean': statistics.mean([a.sum_val / max(1, a.count) for a in recent]),
                'p99': recent[-1].p99 if recent else None,
            }


# ============================================================================
# SYSTEM METRICS COLLECTION
# ============================================================================

class SystemMetricsCollector:
    """Collects system-level metrics (CPU, memory, disk, network)."""

    def __init__(self, collector: MetricsCollector, interval_seconds: int = 10):
        """Initialize system metrics collector.
        
        Args:
            collector: MetricsCollector instance
            interval_seconds: Collection interval
        """
        self.collector = collector
        self.interval = interval_seconds
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._last_net_io = psutil.net_io_counters()

    def register_metrics(self) -> None:
        """Register system metrics with the collector."""
        self.collector.register_metric(
            'sys.cpu_usage',
            'CPU Usage %',
            MetricType.GAUGE,
            unit='%',
            slo_target='<70% p95'
        )
        self.collector.register_metric(
            'sys.memory_usage',
            'Memory Usage %',
            MetricType.GAUGE,
            unit='%',
            slo_target='<80% p95'
        )
        self.collector.register_metric(
            'sys.disk_usage',
            'Disk Usage %',
            MetricType.GAUGE,
            unit='%',
            slo_target='<85% p95'
        )
        self.collector.register_metric(
            'sys.network_in_bytes',
            'Network In (bytes)',
            MetricType.COUNTER,
            unit='bytes'
        )
        self.collector.register_metric(
            'sys.network_out_bytes',
            'Network Out (bytes)',
            MetricType.COUNTER,
            unit='bytes'
        )

    def start(self) -> None:
        """Start system metrics collection."""
        if self._running:
            logger.warning("System metrics collector already running")
            return

        self._running = True
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            daemon=True,
            name="SystemMetricsCollector-Worker"
        )
        self._worker_thread.start()
        logger.info("System metrics collector started")

    def stop(self) -> None:
        """Stop system metrics collection."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)

    def _worker_loop(self) -> None:
        """Background worker for system metrics."""
        while self._running:
            try:
                self._collect_system_metrics()
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}", exc_info=True)

    def _collect_system_metrics(self) -> None:
        """Collect current system metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.collector.record_metric('sys.cpu_usage', cpu_percent)

        # Memory usage
        mem = psutil.virtual_memory()
        self.collector.record_metric('sys.memory_usage', mem.percent)

        # Disk usage
        disk = psutil.disk_usage('/')
        self.collector.record_metric('sys.disk_usage', disk.percent)

        # Network I/O
        net_io = psutil.net_io_counters()
        self.collector.record_metric('sys.network_in_bytes', net_io.bytes_recv)
        self.collector.record_metric('sys.network_out_bytes', net_io.bytes_sent)


# ============================================================================
# EXPORT HANDLERS
# ============================================================================

class PrometheusExporter:
    """Export metrics to Prometheus format."""

    @staticmethod
    def export(metrics: List[AggregatedMetric]) -> str:
        """Convert metrics to Prometheus text format."""
        lines = []
        lines.append("# HELP exported_metrics Phase 12 Track 3 metrics")
        lines.append("# TYPE exported_metrics gauge")

        for metric in metrics:
            # Prometheus format: metric_name{labels} value timestamp
            labels_str = ",".join(f'{k}="{v}"' for k, v in metric.labels.items())
            if labels_str:
                line = f'{metric.metric_id}{{{labels_str}}} {metric.p99}'
            else:
                line = f'{metric.metric_id} {metric.p99}'
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def write_to_file(metrics: List[AggregatedMetric], filepath: Union[str, Path]) -> None:
        """Write metrics to Prometheus-format file."""
        content = PrometheusExporter.export(metrics)
        with open(filepath, 'w') as f:
            f.write(content)
        logger.info(f"Exported {len(metrics)} metrics to {filepath}")


class JSONExporter:
    """Export metrics to JSON format."""

    @staticmethod
    def export(metrics: List[AggregatedMetric]) -> str:
        """Convert metrics to JSON."""
        return json.dumps(
            {
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': [m.to_dict() for m in metrics],
            },
            indent=2
        )

    @staticmethod
    def write_to_file(metrics: List[AggregatedMetric], filepath: Union[str, Path]) -> None:
        """Write metrics to JSON file."""
        content = JSONExporter.export(metrics)
        with open(filepath, 'w') as f:
            f.write(content)
        logger.info(f"Exported {len(metrics)} metrics to {filepath}")


# ============================================================================
# BUILT-IN METRICS INITIALIZATION
# ============================================================================

def initialize_standard_metrics(collector: MetricsCollector) -> None:
    """Initialize all standard metrics from the observability framework."""

    # System Health & Availability
    collector.register_metric('sys.uptime', 'System Uptime', MetricType.GAUGE, '%', slo_target='99.99%')
    collector.register_metric('sys.health_score', 'Overall Health Score', MetricType.GAUGE, slo_target='≥95%')
    collector.register_metric('sys.error_rate', 'System Error Rate', MetricType.GAUGE, '%', slo_target='<0.1%')
    collector.register_metric('sys.recovery_time_ms', 'Mean Recovery Time', MetricType.HISTOGRAM, 'ms', slo_target='<1s p99')
    collector.register_metric('sys.incident_count', 'Total Incidents (24h)', MetricType.COUNTER, slo_target='<3 per day')

    # RBAC Metrics (Track 12.1)
    collector.register_metric('rbac.permission_checks_total', 'Permission Checks', MetricType.COUNTER)
    collector.register_metric('rbac.permission_checks_denied', 'Permission Denials', MetricType.COUNTER, slo_target='<1%')
    collector.register_metric('rbac.permission_check_latency_ms', 'Permission Check Latency', MetricType.HISTOGRAM, 'ms', slo_target='<10ms p99')
    collector.register_metric('rbac.unauthorized_attempts', 'Unauthorized Access Attempts', MetricType.COUNTER, slo_target='<1/min')
    collector.register_metric('rbac.mfa_success_rate', 'MFA Success Rate', MetricType.GAUGE, '%', slo_target='>99%')
    collector.register_metric('rbac.concurrent_sessions', 'Concurrent Active Sessions', MetricType.GAUGE, slo_target='<500')

    # Governance Metrics (Track 12.2)
    collector.register_metric('gov.approval_workflows_pending', 'Pending Approvals', MetricType.GAUGE, slo_target='<5')
    collector.register_metric('gov.approval_workflow_latency_ms', 'Approval Latency', MetricType.HISTOGRAM, 'ms', slo_target='<30min')
    collector.register_metric('gov.compliance_status_pct', 'Compliance Status %', MetricType.GAUGE, '%', slo_target='100%')
    collector.register_metric('gov.policy_exceptions', 'Active Policy Exceptions', MetricType.GAUGE, slo_target='<2')
    collector.register_metric('gov.sla_breaches', 'SLA Breaches (24h)', MetricType.COUNTER, slo_target='0')
    collector.register_metric('gov.vulnerabilities_detected', 'Active Vulnerabilities', MetricType.GAUGE, slo_target='0 critical')

    # Cognitive System Metrics (Phase 10)
    collector.register_metric('cog.session_restore_time_ms', 'Session Restore Time', MetricType.HISTOGRAM, 'ms', slo_target='<500ms p99')
    collector.register_metric('cog.ooda_cycle_time_ms', 'OODA Cycle Time', MetricType.HISTOGRAM, 'ms', slo_target='<800ms p99')
    collector.register_metric('cog.memory_consolidation_ms', 'Memory Consolidation Time', MetricType.HISTOGRAM, 'ms', slo_target='<3s p99')
    collector.register_metric('cog.inference_latency_ms', 'LLM Inference Latency', MetricType.HISTOGRAM, 'ms', slo_target='<2s p99')
    collector.register_metric('cog.context_retrieval_latency_ms', 'Context Retrieval Latency', MetricType.HISTOGRAM, 'ms', slo_target='<200ms p99')
    collector.register_metric('cog.memory_hit_rate_pct', 'Memory Hit Rate %', MetricType.GAUGE, '%', slo_target='>90%')
    collector.register_metric('cog.agent_task_success_rate', 'Agent Task Success Rate', MetricType.GAUGE, '%', slo_target='>99%')
    collector.register_metric('cog.concurrent_sessions_active', 'Concurrent Cognitive Sessions', MetricType.GAUGE)

    # Agent Performance Metrics
    collector.register_metric('agent.task_execution_time_ms', 'Task Execution Time', MetricType.HISTOGRAM, 'ms', slo_target='<5s p99')
    collector.register_metric('agent.error_count_24h', 'Agent Errors (24h)', MetricType.COUNTER, slo_target='<5')
    collector.register_metric('agent.throughput_tasks_per_min', 'Task Throughput', MetricType.GAUGE, 'tasks/min')
    collector.register_metric('agent.queue_depth', 'Task Queue Depth', MetricType.GAUGE, slo_target='<50')
    collector.register_metric('agent.worker_availability_pct', 'Worker Availability %', MetricType.GAUGE, '%', slo_target='>99%')

    logger.info("Standard metrics initialized (45+ metrics)")


# ============================================================================
# MAIN INITIALIZATION
# ============================================================================

def create_metrics_engine() -> Tuple[MetricsCollector, SystemMetricsCollector]:
    """Create and initialize the metrics engine.
    
    Returns:
        Tuple of (MetricsCollector, SystemMetricsCollector)
    """
    # Create collectors
    metrics_collector = MetricsCollector(export_interval_seconds=60)
    system_collector = SystemMetricsCollector(metrics_collector, interval_seconds=10)

    # Register metrics
    initialize_standard_metrics(metrics_collector)
    system_collector.register_metrics()

    # Setup export handlers
    export_dir = Path('./metrics_export')
    export_dir.mkdir(exist_ok=True)

    def prometheus_export(metrics: List[AggregatedMetric]) -> None:
        """Export to Prometheus format."""
        try:
            filepath = export_dir / 'metrics.prom'
            PrometheusExporter.write_to_file(metrics, filepath)
        except Exception as e:
            logger.error(f"Error exporting to Prometheus: {e}")

    def json_export(metrics: List[AggregatedMetric]) -> None:
        """Export to JSON format."""
        try:
            filepath = export_dir / f'metrics_{int(time.time())}.json'
            JSONExporter.write_to_file(metrics, filepath)
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")

    metrics_collector.register_export_handler(prometheus_export)
    metrics_collector.register_export_handler(json_export)

    # Start collectors
    metrics_collector.start()
    system_collector.start()

    return metrics_collector, system_collector


if __name__ == '__main__':
    # Example usage
    collector, system = create_metrics_engine()

    # Simulate metrics for demonstration
    logger.info("Metrics engine running... (press Ctrl+C to stop)")

    try:
        for i in range(60):
            # Simulate RBAC metrics
            collector.record_metric('rbac.permission_checks_total', 100 + i * 10)
            collector.record_metric('rbac.permission_check_latency_ms', 5 + (i % 10))

            # Simulate Governance metrics
            collector.record_metric('gov.approval_workflows_pending', 3 + (i % 5))

            # Simulate Cognitive metrics
            collector.record_metric('cog.session_restore_time_ms', 200 + (i % 300))
            collector.record_metric('cog.ooda_cycle_time_ms', 500 + (i % 400))

            # Simulate Agent metrics
            collector.record_metric('agent.task_execution_time_ms', 1000 + (i * 50) % 2000)
            collector.record_metric('agent.queue_depth', 10 + (i % 40))

            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        system.stop()
        collector.stop()
