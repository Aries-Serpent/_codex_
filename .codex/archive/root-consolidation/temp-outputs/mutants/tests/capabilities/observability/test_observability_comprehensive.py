from enum import Enum

#         assert ", "Condition must be true"
#         assert "http_requests 100" in output, "Condition must be true"


# --- SLO Tests ---


class SLO:
    """Service Level Objective definition."""

    def __init__(self, name: str, target: float, window_hours: int = 720):
        self.name = name
        self.target = target  # e.g., 0.99 for 99%
        self.window_hours = window_hours
        self.measurements: list[dict[str, Any]] = []

    def record(self, success: bool, latency_ms: float | None = None) -> None:
        """Record measurement."""
        self.measurements.append(
            {
                "timestamp": time.time(),
                "success": success,
                "latency_ms": latency_ms,
            }
        )

    def current_value(self) -> float:
        """Calculate current SLO value."""
        if not self.measurements:
            return 1.0
        successes = sum(1 for m in self.measurements if m["success"])
        return successes / len(self.measurements)

    def is_meeting_target(self) -> bool:
        """Check if meeting SLO target."""
        return self.current_value() >= self.target

    def error_budget_remaining(self) -> float:
        """Calculate remaining error budget."""
        allowed_failures = 1 - self.target
        actual_failures = 1 - self.current_value()
        return max(0, allowed_failures - actual_failures)


class TestSLO:
    """Tests for SLO tracking."""

    def test_create_slo(self):
        """Create SLO."""
        slo = SLO("availability", target=0.99)
        assert slo.target == 0.99, "target is not valid"

    def test_record_measurements(self):
        """Record measurements."""
        slo = SLO("availability", target=0.99)
        slo.record(True)
        slo.record(True)
        slo.record(False)
        assert len(slo.measurements) == 3, "Collection must not be empty"

    def test_current_value(self):
        """Calculate current value."""
        slo = SLO("availability", target=0.99)
        slo.record(True)
        slo.record(True)
        slo.record(False)
        slo.record(True)
        assert slo.current_value() == 0.75, "Value must be initialized"

    def test_meeting_target(self):
        """Check if meeting target."""
        slo = SLO("availability", target=0.90)
        for _ in range(95):
            slo.record(True)
        for _ in range(5):
            slo.record(False)
        assert slo.is_meeting_target(), "Condition must be true"


# --- Alert Tests ---


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Alert:
    """Alert definition."""

    def __init__(self, name: str, severity: AlertSeverity):
        self.name = name
        self.severity = severity
        self.condition: Callable[[], bool] | None = None
        self.message: str = ""
        self.firing: bool = False
        self.last_fired: float | None = None

    def set_condition(self, condition: Callable[[], bool]) -> None:
        """Set alert condition."""
        self.condition = condition

    def evaluate(self) -> bool:
        """Evaluate alert condition."""
        if self.condition:
            self.firing = self.condition()
            if self.firing:
                self.last_fired = time.time()
            return self.firing
        return False


class AlertManager:
    """Manage alerts."""

    def __init__(self):
        self.alerts: dict[str, Alert] = {}
        self.firing_alerts: list[str] = []

    def register(self, alert: Alert) -> None:
        """Register alert."""
        self.alerts[alert.name] = alert

    def evaluate_all(self) -> list[str]:
        """Evaluate all alerts."""
        self.firing_alerts = []
        for name, alert in self.alerts.items():
            if alert.evaluate():
                self.firing_alerts.append(name)
        return self.firing_alerts

    def get_firing(self) -> list[Alert]:
        """Get firing alerts."""
        return [self.alerts[name] for name in self.firing_alerts]


class TestAlerts:
    """Tests for alerting."""

    def test_create_alert(self):
        """Create alert."""
        alert = Alert("high_latency", AlertSeverity.WARNING)
        assert alert.severity == AlertSeverity.WARNING, "severity is not valid"

    def test_evaluate_condition(self):
        """Evaluate alert condition."""
        alert = Alert("cpu_high", AlertSeverity.WARNING)
        cpu_usage = 0.95
        alert.set_condition(lambda: cpu_usage > 0.9)
        assert alert.evaluate(), "Condition must be true"

    def test_alert_manager(self):
        """Alert manager evaluates all alerts."""
        manager = AlertManager()
        alert1 = Alert("alert1", AlertSeverity.WARNING)
        alert1.set_condition(lambda: True)
        alert2 = Alert("alert2", AlertSeverity.WARNING)
        alert2.set_condition(lambda: False)
        manager.register(alert1)
        manager.register(alert2)
        firing = manager.evaluate_all()
        assert "alert1" in firing, "Condition must be true"
        assert "alert2" not in firing, "Condition must be true"


# --- Dashboard Tests ---


class DashboardPanel:
    """Dashboard panel definition."""

    def __init__(self, title: str, panel_type: str):
        self.title = title
        self.panel_type = panel_type  # graph, gauge, table, etc.
        self.queries: list[str] = []
        self.thresholds: list[dict[str, Any]] = []

    def add_query(self, query: str) -> None:
        self.queries.append(query)

    def add_threshold(self, value: float, color: str) -> None:
        self.thresholds.append({"value": value, "color": color})


class Dashboard:
    """Observability dashboard."""

    def __init__(self, name: str):
        self.name = name
        self.panels: list[DashboardPanel] = []
        self.refresh_interval: int = 30  # seconds
        self.time_range: str = "1h"

    def add_panel(self, panel: DashboardPanel) -> None:
        self.panels.append(panel)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "refresh_interval": self.refresh_interval,
            "time_range": self.time_range,
            "panels": [{"title": p.title, "type": p.panel_type} for p in self.panels],
        }


class TestDashboard:
    """Tests for dashboards."""

    def test_create_dashboard(self):
        """Create dashboard."""
        dashboard = Dashboard("API Metrics")
        assert dashboard.name == "API Metrics", "name is not valid"

    def test_add_panels(self):
        """Add panels to dashboard."""
        dashboard = Dashboard("Overview")
        dashboard.add_panel(DashboardPanel("CPU Usage", "graph"))
        dashboard.add_panel(DashboardPanel("Memory", "gauge"))
        assert len(dashboard.panels) == 2, "Collection must not be empty"


# --- Anomaly Detection Tests ---


class AnomalyDetector:
    """Detect anomalies in metrics."""

    def __init__(self, threshold_std: float = 3.0):
        self.threshold_std = threshold_std
        self.baseline: list[float] = []

    def train(self, values: list[float]) -> None:
        """Train on baseline values."""
        self.baseline = values

    def detect(self, value: float) -> dict[str, Any]:
        """Detect if value is anomalous."""
        if not self.baseline:
            return {"is_anomaly": False, "reason": "no baseline"}

        mean = sum(self.baseline) / len(self.baseline)
        variance = sum((x - mean) ** 2 for x in self.baseline) / len(self.baseline)
        std = variance**0.5

        if std == 0:
            is_anomaly = value != mean
        else:
            z_score = abs(value - mean) / std
            is_anomaly = z_score > self.threshold_std

        return {
            "is_anomaly": is_anomaly,
            "value": value,
            "mean": mean,
            "std": std,
        }


class TestAnomalyDetection:
    """Tests for anomaly detection."""

    def test_detect_normal(self):
        """Normal value is not anomaly."""
        detector = AnomalyDetector(threshold_std=3.0)
        detector.train([10, 11, 9, 10, 11, 10, 9, 10])
        result = detector.detect(10)
        assert not result["is_anomaly"], "Result must not be empty"

    def test_detect_anomaly(self):
        """Extreme value is anomaly."""
        detector = AnomalyDetector(threshold_std=3.0)
        detector.train([10, 11, 9, 10, 11, 10, 9, 10])
        result = detector.detect(100)
        assert result["is_anomaly"], "Result must not be empty"


# --- Distributed Tracing Tests ---


class Span:
    """Distributed tracing span."""

    def __init__(self, name: str, trace_id: str, span_id: str):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_id: str | None = None
        self.start_time: float = time.time()
        self.end_time: float | None = None
        self.attributes: dict[str, Any] = {}
        self.events: list[dict[str, Any]] = []

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def add_event(self, name: str) -> None:
        self.events.append({"name": name, "timestamp": time.time()})

    def end(self) -> None:
        self.end_time = time.time()

    def duration_ms(self) -> float | None:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None


class Tracer:
    """Distributed tracer."""

    def __init__(self):
        self.spans: dict[str, Span] = {}
        self._span_counter = 0

    def start_span(
        self, name: str, trace_id: str | None = None, parent_id: str | None = None
    ) -> Span:
        """Start new span."""
        self._span_counter += 1
        span_id = f"span-{self._span_counter}"
        trace_id = trace_id or f"trace-{self._span_counter}"
        span = Span(name, trace_id, span_id)
        span.parent_id = parent_id
        self.spans[span_id] = span
        return span

    def get_trace(self, trace_id: str) -> list[Span]:
        """Get all spans for a trace."""
        return [s for s in self.spans.values() if s.trace_id == trace_id]


class TestDistributedTracing:
    """Tests for distributed tracing."""

    def test_create_span(self):
        """Create tracing span."""
        tracer = Tracer()
        span = tracer.start_span("http_request")
        assert span.name == "http_request", "name is not valid"

    def test_span_attributes(self):
        """Set span attributes."""
        tracer = Tracer()
        span = tracer.start_span("db_query")
        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.statement", "SELECT * FROM users")
        assert span.attributes["db.system"] == "postgresql", "Condition must be true"

    def test_trace_hierarchy(self):
        """Create trace with parent-child spans."""
        tracer = Tracer()
        parent = tracer.start_span("request", trace_id="trace-1")
        child = tracer.start_span("db_query", trace_id="trace-1", parent_id=parent.span_id)
        assert child.parent_id == parent.span_id, "parent_id is not valid"
        trace = tracer.get_trace("trace-1")
        assert len(trace) == 2, "Trace must not be empty"
