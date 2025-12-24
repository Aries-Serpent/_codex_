"""
Context Observer

Structured observability for context management including
logging, metrics, and alerts with correlation ID support.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import logging
import uuid


class MetricType(Enum):
    """Types of metrics tracked."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """A single metric measurement."""

    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
        }


@dataclass
class Alert:
    """An alert triggered by observability."""

    alert_id: str
    severity: AlertSeverity
    message: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    context: Dict = field(default_factory=dict)
    resolved: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "severity": self.severity.value,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "context": self.context,
            "resolved": self.resolved,
        }


@dataclass
class LogEntry:
    """A structured log entry."""

    level: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    x_request_id: Optional[str] = None
    gh_request_id: Optional[str] = None
    source: str = ""
    context: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "level": self.level,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "x_request_id": self.x_request_id,
            "gh_request_id": self.gh_request_id,
            "source": self.source,
            "context": self.context,
        }


class ContextObserver:
    """
    Structured observability for context management.

    Features:
    - Structured logging with correlation IDs
    - Metrics collection (counters, gauges, histograms)
    - Alert generation and management
    - Integration with external logging systems
    """

    def __init__(
        self,
        logger_name: str = "context_management",
        enable_metrics: bool = True,
        enable_alerts: bool = True,
        alert_callback: Optional[Callable[[Alert], None]] = None,
    ):
        """
        Initialize observer.

        Args:
            logger_name: Name for the logger
            enable_metrics: Whether to collect metrics
            enable_alerts: Whether to generate alerts
            alert_callback: Callback for alert handling
        """
        self.logger = logging.getLogger(logger_name)
        self.enable_metrics = enable_metrics
        self.enable_alerts = enable_alerts
        self._alert_callback = alert_callback

        # Storage
        self._metrics: List[Metric] = []
        self._alerts: List[Alert] = []
        self._logs: List[LogEntry] = []

        # Current correlation context
        self._correlation_id: Optional[str] = None
        self._x_request_id: Optional[str] = None
        self._gh_request_id: Optional[str] = None

        # Metric aggregations
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}

    def set_correlation_ids(
        self,
        correlation_id: Optional[str] = None,
        x_request_id: Optional[str] = None,
        gh_request_id: Optional[str] = None,
    ):
        """Set correlation IDs for log/metric context."""
        self._correlation_id = correlation_id
        self._x_request_id = x_request_id
        self._gh_request_id = gh_request_id

    def generate_correlation_id(self) -> str:
        """Generate a new correlation ID."""
        self._correlation_id = str(uuid.uuid4())
        return self._correlation_id

    def log(self, level: str, message: str, source: str = "", context: Optional[Dict] = None):
        """
        Log a structured message.

        Args:
            level: Log level (debug, info, warning, error)
            message: Log message
            source: Source component
            context: Additional context
        """
        entry = LogEntry(
            level=level,
            message=message,
            correlation_id=self._correlation_id,
            x_request_id=self._x_request_id,
            gh_request_id=self._gh_request_id,
            source=source,
            context=context or {},
        )

        self._logs.append(entry)

        # Also log to standard logger
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(
            f"[{source}] {message}",
            extra={
                "correlation_id": self._correlation_id,
                "x_request_id": self._x_request_id,
                "gh_request_id": self._gh_request_id,
            },
        )

    def debug(self, message: str, source: str = "", context: Optional[Dict] = None):
        """Log debug message."""
        self.log("debug", message, source, context)

    def info(self, message: str, source: str = "", context: Optional[Dict] = None):
        """Log info message."""
        self.log("info", message, source, context)

    def warning(self, message: str, source: str = "", context: Optional[Dict] = None):
        """Log warning message."""
        self.log("warning", message, source, context)

    def error(self, message: str, source: str = "", context: Optional[Dict] = None):
        """Log error message."""
        self.log("error", message, source, context)

    def increment(self, metric_name: str, value: float = 1.0, labels: Optional[Dict] = None):
        """Increment a counter metric."""
        if not self.enable_metrics:
            return

        key = f"{metric_name}:{json.dumps(labels or {}, sort_keys=True)}"
        self._counters[key] = self._counters.get(key, 0) + value

        self._metrics.append(
            Metric(
                name=metric_name,
                value=self._counters[key],
                metric_type=MetricType.COUNTER,
                labels=labels or {},
            )
        )

    def gauge(self, metric_name: str, value: float, labels: Optional[Dict] = None):
        """Set a gauge metric."""
        if not self.enable_metrics:
            return

        key = f"{metric_name}:{json.dumps(labels or {}, sort_keys=True)}"
        self._gauges[key] = value

        self._metrics.append(
            Metric(name=metric_name, value=value, metric_type=MetricType.GAUGE, labels=labels or {})
        )

    def histogram(self, metric_name: str, value: float, labels: Optional[Dict] = None):
        """Record a histogram observation."""
        if not self.enable_metrics:
            return

        self._metrics.append(
            Metric(
                name=metric_name, value=value, metric_type=MetricType.HISTOGRAM, labels=labels or {}
            )
        )

    def alert(
        self, severity: AlertSeverity, message: str, source: str, context: Optional[Dict] = None
    ) -> Alert:
        """
        Generate an alert.

        Args:
            severity: Alert severity level
            message: Alert message
            source: Source component
            context: Additional context

        Returns:
            Created Alert object
        """
        if not self.enable_alerts:
            return None

        alert = Alert(
            alert_id=str(uuid.uuid4())[:8],
            severity=severity,
            message=message,
            source=source,
            correlation_id=self._correlation_id,
            context=context or {},
        )

        self._alerts.append(alert)

        # Call callback if configured
        if self._alert_callback:
            try:
                self._alert_callback(alert)
            except Exception as e:
                logger.debug(f"Exception: {e}")
                logger.warning(f"Exception: {e}", exc_info=True)

        # Also log the alert
        self.log(
            level=(
                "error" if severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL] else "warning"
            ),
            message=f"ALERT [{severity.value}]: {message}",
            source=source,
            context=context,
        )

        return alert

    def resolve_alert(self, alert_id: str):
        """Mark an alert as resolved."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                break

    def get_active_alerts(self) -> List[Alert]:
        """Get all unresolved alerts."""
        return [a for a in self._alerts if not a.resolved]

    def get_metrics_summary(self) -> Dict:
        """Get summary of collected metrics."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "total_observations": len(self._metrics),
            "alert_count": len(self._alerts),
            "active_alerts": len(self.get_active_alerts()),
        }

    def get_recent_logs(self, count: int = 100, level: Optional[str] = None) -> List[Dict]:
        """Get recent log entries."""
        logs = self._logs[-count:] if count > 0 else self._logs

        if level:
            logs = [l for l in logs if l.level.lower() == level.lower()]

        return [l.to_dict() for l in logs]

    def export_metrics(self) -> List[Dict]:
        """Export all metrics as dictionaries."""
        return [m.to_dict() for m in self._metrics]

    def export_alerts(self) -> List[Dict]:
        """Export all alerts as dictionaries."""
        return [a.to_dict() for a in self._alerts]

    def clear(self):
        """Clear all collected data."""
        self._metrics.clear()
        self._alerts.clear()
        self._logs.clear()
        self._counters.clear()
        self._gauges.clear()

    # Context manager support for correlation tracking
    def __enter__(self):
        """Enter context with new correlation ID."""
        if not self._correlation_id:
            self.generate_correlation_id()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if exc_type:
            self.error(
                f"Exception in context: {exc_val}",
                source="context_observer",
                context={"exception_type": str(exc_type)},
            )
        return False
