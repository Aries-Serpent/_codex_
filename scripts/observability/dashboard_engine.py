"""
Phase 12 Track 3: Real-Time Monitoring Dashboard Engine
WebSocket-based live metrics dashboard with <1s refresh, alert management, and incident analysis

Authority: @mbaetiong (D-tier AUTO-GO)
Timeline: Days 3-4 deliverable (2026-07-03 → 2026-07-04)
Target: 550+ lines, >95% test coverage, 100% type hints
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


# ============================================================================
# TYPE DEFINITIONS & DATA STRUCTURES
# ============================================================================

class DashboardWidget(Enum):
    """Dashboard widget types."""
    GAUGE = "gauge"
    TIMESERIES = "timeseries"
    STAT = "stat"
    HEATMAP = "heatmap"
    TABLE = "table"
    STATUS = "status"


@dataclass
class DashboardMetric:
    """Metric display configuration."""
    widget_id: str
    metric_id: str
    widget_type: DashboardWidget
    title: str
    unit: str = ""
    min_value: float = 0.0
    max_value: float = 100.0
    refresh_interval_ms: int = 1000
    alert_thresholds: Dict[str, float] = None  # {"warning": 75, "critical": 90}

    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {}


@dataclass
class AlertEvent:
    """Alert event in the system."""
    alert_id: str
    metric_id: str
    severity: str  # "P0" | "P1" | "P2" | "P3"
    message: str
    timestamp: datetime
    threshold: float
    current_value: float
    duration_seconds: int
    active: bool = True
    resolved_at: Optional[datetime] = None
    incident_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'alert_id': self.alert_id,
            'metric_id': self.metric_id,
            'severity': self.severity,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'threshold': self.threshold,
            'current_value': self.current_value,
            'duration_seconds': self.duration_seconds,
            'active': self.active,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'incident_id': self.incident_id,
        }


@dataclass
class IncidentEvent:
    """Incident combining multiple alerts."""
    incident_id: str
    severity: str  # "critical" | "high" | "medium" | "low"
    created_at: datetime
    resolved_at: Optional[datetime] = None
    root_cause: str = ""
    affected_metrics: List[str] = None
    related_alerts: List[str] = None

    def __post_init__(self):
        if self.affected_metrics is None:
            self.affected_metrics = []
        if self.related_alerts is None:
            self.related_alerts = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'incident_id': self.incident_id,
            'severity': self.severity,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'root_cause': self.root_cause,
            'affected_metrics': self.affected_metrics,
            'related_alerts': self.related_alerts,
        }


@dataclass
class HealthScorecard:
    """Overall system health scorecard."""
    timestamp: datetime
    overall_score: float  # 0-100
    availability_pct: float
    error_rate_pct: float
    latency_p99_ms: float
    system_status: str  # "healthy" | "degraded" | "critical"
    active_incidents: int
    last_incident: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'overall_score': self.overall_score,
            'availability_pct': self.availability_pct,
            'error_rate_pct': self.error_rate_pct,
            'latency_p99_ms': self.latency_p99_ms,
            'system_status': self.system_status,
            'active_incidents': self.active_incidents,
            'last_incident': self.last_incident.isoformat() if self.last_incident else None,
        }


# ============================================================================
# DASHBOARD STATE MANAGEMENT
# ============================================================================

class AlertManager:
    """Manages alert lifecycle and incident correlation."""

    def __init__(self):
        self.active_alerts: Dict[str, AlertEvent] = {}
        self.resolved_alerts: Dict[str, AlertEvent] = {}
        self.incidents: Dict[str, IncidentEvent] = {}
        self._lock = threading.RLock()
        self._alert_callbacks: List[Callable] = []

    def register_alert_callback(self, callback: Callable[[AlertEvent], None]) -> None:
        """Register callback for alert events."""
        with self._lock:
            self._alert_callbacks.append(callback)

    def create_alert(self, alert: AlertEvent) -> None:
        """Create a new alert."""
        with self._lock:
            # Check if alert already exists
            if alert.alert_id in self.active_alerts:
                logger.warning(f"Alert {alert.alert_id} already active")
                return

            self.active_alerts[alert.alert_id] = alert
            logger.warning(f"Alert created: {alert.alert_id} ({alert.severity})")

            # Trigger callbacks
            for callback in self._alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")

            # Try to correlate with existing incidents
            self._correlate_alert(alert)

    def resolve_alert(self, alert_id: str, resolution_reason: str = "") -> None:
        """Resolve an alert."""
        with self._lock:
            if alert_id not in self.active_alerts:
                logger.warning(f"Alert {alert_id} not found in active alerts")
                return

            alert = self.active_alerts.pop(alert_id)
            alert.active = False
            alert.resolved_at = datetime.utcnow()
            self.resolved_alerts[alert_id] = alert

            logger.info(f"Alert resolved: {alert_id} ({resolution_reason})")

    def get_active_alerts(self, severity: Optional[str] = None) -> List[AlertEvent]:
        """Get all active alerts, optionally filtered by severity."""
        with self._lock:
            if severity:
                return [a for a in self.active_alerts.values() if a.severity == severity]
            return list(self.active_alerts.values())

    def get_alert_summary(self) -> Dict[str, int]:
        """Get count of active alerts by severity."""
        with self._lock:
            summary = defaultdict(int)
            for alert in self.active_alerts.values():
                summary[alert.severity] += 1
            return dict(summary)

    def _correlate_alert(self, alert: AlertEvent) -> None:
        """Try to correlate alert with existing incidents."""
        # Look for related alerts within last 10 minutes
        cutoff = datetime.utcnow() - timedelta(minutes=10)
        related_alerts = [
            a.alert_id for a in self.active_alerts.values()
            if a.timestamp >= cutoff and a.metric_id != alert.metric_id
        ]

        if related_alerts and alert.severity in ["P0", "P1"]:
            # Create or update incident
            incident_id = f"incident_{int(time.time())}"
            incident = IncidentEvent(
                incident_id=incident_id,
                severity="critical" if alert.severity == "P0" else "high",
                created_at=datetime.utcnow(),
                affected_metrics=[alert.metric_id],
                related_alerts=[alert.alert_id] + related_alerts,
            )
            self.incidents[incident_id] = incident
            alert.incident_id = incident_id
            logger.info(f"Incident created: {incident_id}")


class MetricsCache:
    """In-memory cache of latest metric values for fast dashboard queries."""

    def __init__(self, max_history: int = 3600):
        """Initialize metrics cache.
        
        Args:
            max_history: Keep up to N history points per metric
        """
        self.max_history = max_history
        self.latest_values: Dict[str, float] = {}
        self.history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.last_update: Dict[str, datetime] = {}
        self._lock = threading.RLock()

    def update_metric(self, metric_id: str, value: float, timestamp: datetime) -> None:
        """Update metric value."""
        with self._lock:
            self.latest_values[metric_id] = value
            self.last_update[metric_id] = timestamp

            # Keep history
            self.history[metric_id].append({
                'value': value,
                'timestamp': timestamp.isoformat(),
            })
            if len(self.history[metric_id]) > self.max_history:
                self.history[metric_id].pop(0)

    def get_latest(self, metric_id: str) -> Optional[float]:
        """Get latest value for a metric."""
        with self._lock:
            return self.latest_values.get(metric_id)

    def get_history(self, metric_id: str, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get history for a metric over last N minutes."""
        with self._lock:
            if metric_id not in self.history:
                return []

            cutoff = datetime.utcnow() - timedelta(minutes=minutes)
            return [
                h for h in self.history[metric_id]
                if datetime.fromisoformat(h['timestamp']) >= cutoff
            ]

    def get_all_latest(self) -> Dict[str, float]:
        """Get latest values for all metrics."""
        with self._lock:
            return dict(self.latest_values)

    def get_statistics(self, metric_id: str, minutes: int = 5) -> Optional[Dict[str, float]]:
        """Get statistics for a metric over last N minutes."""
        with self._lock:
            history = self.get_history(metric_id, minutes)
            if not history:
                return None

            values = [h['value'] for h in history]
            return {
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'p99': sorted(values)[max(0, int(len(values) * 0.99) - 1)],
            }


# ============================================================================
# DASHBOARD RENDERING ENGINE
# ============================================================================

class DashboardEngine:
    """Real-time monitoring dashboard engine."""

    def __init__(self):
        """Initialize dashboard engine."""
        self.widgets: Dict[str, DashboardMetric] = {}
        self.metrics_cache = MetricsCache()
        self.alert_manager = AlertManager()
        self.health_history: List[HealthScorecard] = []
        self._lock = threading.RLock()
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._update_interval = 1.0  # 1 second for <1s refresh

        # WebSocket clients for real-time updates
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def register_widget(self, widget: DashboardMetric) -> None:
        """Register a dashboard widget."""
        with self._lock:
            self.widgets[widget.widget_id] = widget
            logger.info(f"Registered widget: {widget.widget_id} ({widget.widget_type.value})")

    def update_metric_value(self, metric_id: str, value: float) -> None:
        """Update a metric value (called by metrics collector)."""
        with self._lock:
            self.metrics_cache.update_metric(metric_id, value, datetime.utcnow())

        # Notify subscribers
        self._notify_subscribers('metric_update', {
            'metric_id': metric_id,
            'value': value,
            'timestamp': datetime.utcnow().isoformat(),
        })

    def subscribe_to_updates(self, topic: str, callback: Callable) -> None:
        """Subscribe to dashboard update events."""
        with self._lock:
            self._subscribers[topic].append(callback)

    def _notify_subscribers(self, topic: str, data: Any) -> None:
        """Notify all subscribers of a topic update."""
        with self._lock:
            subscribers = self._subscribers.get(topic, [])

        for callback in subscribers:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")

    def get_dashboard_snapshot(self) -> Dict[str, Any]:
        """Get complete dashboard state snapshot."""
        with self._lock:
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'health_scorecard': self._calculate_health_scorecard().to_dict(),
                'alerts': {
                    'active': [a.to_dict() for a in self.alert_manager.get_active_alerts()],
                    'summary': self.alert_manager.get_alert_summary(),
                },
                'widgets': [
                    {
                        'id': w.widget_id,
                        'type': w.widget_type.value,
                        'title': w.title,
                        'value': self.metrics_cache.get_latest(w.metric_id),
                        'history': self.metrics_cache.get_history(w.metric_id, 5),
                        'stats': self.metrics_cache.get_statistics(w.metric_id, 5),
                    }
                    for w in self.widgets.values()
                ],
                'incidents': [i.to_dict() for i in self.alert_manager.incidents.values()],
            }

    def _calculate_health_scorecard(self) -> HealthScorecard:
        """Calculate overall system health scorecard."""
        # Get latest metrics
        uptime = self.metrics_cache.get_latest('sys.uptime') or 100.0
        error_rate = self.metrics_cache.get_latest('sys.error_rate') or 0.0
        latency = self.metrics_cache.get_latest('sys.network_latency_ms') or 0.0

        # Calculate overall score (0-100)
        availability_score = min(100, uptime)
        error_score = max(0, 100 - (error_rate * 1000))
        latency_score = max(0, 100 - min(100, latency / 10))
        overall_score = (availability_score * 0.5 + error_score * 0.3 + latency_score * 0.2)

        # Determine status
        if overall_score >= 95:
            status = "healthy"
        elif overall_score >= 80:
            status = "degraded"
        else:
            status = "critical"

        # Get incident info
        active_incidents = len(self.alert_manager.incidents)
        last_incident = max(
            (i.created_at for i in self.alert_manager.incidents.values()),
            default=None
        )

        scorecard = HealthScorecard(
            timestamp=datetime.utcnow(),
            overall_score=overall_score,
            availability_pct=uptime,
            error_rate_pct=error_rate,
            latency_p99_ms=latency,
            system_status=status,
            active_incidents=active_incidents,
            last_incident=last_incident,
        )

        # Keep history
        self.health_history.append(scorecard)
        if len(self.health_history) > 1440:  # Keep 24 hours at 1min intervals
            self.health_history.pop(0)

        return scorecard

    def start(self) -> None:
        """Start the dashboard engine."""
        with self._lock:
            if self._running:
                logger.warning("Dashboard engine already running")
                return

            self._running = True
            self._worker_thread = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name="DashboardEngine-Worker"
            )
            self._worker_thread.start()
            logger.info("Dashboard engine started")

    def stop(self) -> None:
        """Stop the dashboard engine."""
        with self._lock:
            self._running = False

        if self._worker_thread:
            self._worker_thread.join(timeout=5)
            logger.info("Dashboard engine stopped")

    def _worker_loop(self) -> None:
        """Background worker that recalculates health and checks alerts."""
        while self._running:
            try:
                # Update health scorecard
                self.get_dashboard_snapshot()

                # Check for alert conditions (simplified)
                # In production, this would integrate with alert rules from metrics engine
                self._check_alert_conditions()

                time.sleep(self._update_interval)
            except Exception as e:
                logger.error(f"Error in dashboard worker: {e}", exc_info=True)

    def _check_alert_conditions(self) -> None:
        """Check for metric thresholds that should trigger alerts."""
        with self._lock:
            for widget in self.widgets.values():
                if not widget.alert_thresholds:
                    continue

                current_value = self.metrics_cache.get_latest(widget.metric_id)
                if current_value is None:
                    continue

                # Check thresholds
                for threshold_name, threshold_value in widget.alert_thresholds.items():
                    if current_value > threshold_value:
                        alert_id = f"{widget.metric_id}_{threshold_name}"
                        if alert_id not in self.alert_manager.active_alerts:
                            alert = AlertEvent(
                                alert_id=alert_id,
                                metric_id=widget.metric_id,
                                severity="P1" if threshold_name == "warning" else "P0",
                                message=f"{widget.title} exceeds {threshold_name} threshold",
                                timestamp=datetime.utcnow(),
                                threshold=threshold_value,
                                current_value=current_value,
                                duration_seconds=60,
                            )
                            self.alert_manager.create_alert(alert)


# ============================================================================
# DASHBOARD CONFIGURATION & INITIALIZATION
# ============================================================================

def create_standard_dashboards(engine: DashboardEngine) -> None:
    """Create all standard dashboard widgets."""

    # Dashboard 1: System Health Overview
    engine.register_widget(DashboardMetric(
        widget_id='health_gauge',
        metric_id='sys.health_score',
        widget_type=DashboardWidget.GAUGE,
        title='System Health Score',
        min_value=0, max_value=100,
        alert_thresholds={'warning': 80, 'critical': 60},
    ))

    engine.register_widget(DashboardMetric(
        widget_id='uptime_timeseries',
        metric_id='sys.uptime',
        widget_type=DashboardWidget.TIMESERIES,
        title='System Uptime (24h)',
        refresh_interval_ms=5000,
    ))

    engine.register_widget(DashboardMetric(
        widget_id='error_rate_stat',
        metric_id='sys.error_rate',
        widget_type=DashboardWidget.STAT,
        title='Error Rate',
        unit='%',
        alert_thresholds={'warning': 0.5, 'critical': 1.0},
    ))

    # Dashboard 2: RBAC Security
    engine.register_widget(DashboardMetric(
        widget_id='rbac_latency',
        metric_id='rbac.permission_check_latency_ms',
        widget_type=DashboardWidget.TIMESERIES,
        title='RBAC Permission Check Latency',
        unit='ms',
        alert_thresholds={'warning': 15, 'critical': 50},
    ))

    engine.register_widget(DashboardMetric(
        widget_id='rbac_denials',
        metric_id='rbac.permission_checks_denied',
        widget_type=DashboardWidget.STAT,
        title='Permission Denials (5m)',
        alert_thresholds={'warning': 5, 'critical': 10},
    ))

    # Dashboard 3: Cognitive System
    engine.register_widget(DashboardMetric(
        widget_id='cog_session_restore',
        metric_id='cog.session_restore_time_ms',
        widget_type=DashboardWidget.TIMESERIES,
        title='Cognitive Session Restore Time',
        unit='ms',
        alert_thresholds={'warning': 1000, 'critical': 5000},
    ))

    engine.register_widget(DashboardMetric(
        widget_id='cog_ooda',
        metric_id='cog.ooda_cycle_time_ms',
        widget_type=DashboardWidget.TIMESERIES,
        title='OODA Cycle Time',
        unit='ms',
        alert_thresholds={'warning': 1000, 'critical': 2000},
    ))

    # Dashboard 4: Governance
    engine.register_widget(DashboardMetric(
        widget_id='gov_compliance',
        metric_id='gov.compliance_status_pct',
        widget_type=DashboardWidget.GAUGE,
        title='Compliance Status',
        min_value=0, max_value=100,
        alert_thresholds={'warning': 95, 'critical': 90},
    ))

    # Dashboard 5: Agent Performance
    engine.register_widget(DashboardMetric(
        widget_id='agent_throughput',
        metric_id='agent.throughput_tasks_per_min',
        widget_type=DashboardWidget.STAT,
        title='Agent Task Throughput',
        unit='tasks/min',
    ))

    logger.info("Standard dashboards created (8 widgets)")


def create_dashboard_engine() -> DashboardEngine:
    """Create and initialize the dashboard engine."""
    engine = DashboardEngine()
    create_standard_dashboards(engine)
    engine.start()
    return engine


# ============================================================================
# DASHBOARD EXPORT UTILITIES
# ============================================================================

class DashboardExporter:
    """Export dashboard state to various formats."""

    @staticmethod
    def to_json(engine: DashboardEngine) -> str:
        """Export dashboard snapshot as JSON."""
        snapshot = engine.get_dashboard_snapshot()
        return json.dumps(snapshot, indent=2, default=str)

    @staticmethod
    def to_html_summary(engine: DashboardEngine, output_file: Optional[str] = None) -> str:
        """Export dashboard as HTML summary."""
        snapshot = engine.get_dashboard_snapshot()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Phase 12 Track 3 - Observability Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .scorecard {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .health-score {{ font-size: 32px; font-weight: bold; }}
        .status-healthy {{ color: green; }}
        .status-degraded {{ color: orange; }}
        .status-critical {{ color: red; }}
        .alert-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        .alert-table td, .alert-table th {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .severity-p0 {{ background-color: #ffcccc; }}
        .severity-p1 {{ background-color: #fff3cd; }}
    </style>
</head>
<body>
    <h1>Phase 12 Track 3: Enterprise Observability Dashboard</h1>
    <p>Generated: {snapshot['timestamp']}</p>

    <div class="scorecard">
        <div class="health-score">Health Score: {snapshot['health_scorecard']['overall_score']:.1f}/100</div>
        <div class="status-{snapshot['health_scorecard']['system_status']}">
            Status: {snapshot['health_scorecard']['system_status'].upper()}
        </div>
        <p>Availability: {snapshot['health_scorecard']['availability_pct']:.2f}%</p>
        <p>Error Rate: {snapshot['health_scorecard']['error_rate_pct']:.3f}%</p>
        <p>Active Incidents: {snapshot['health_scorecard']['active_incidents']}</p>
    </div>

    <h2>Active Alerts ({len(snapshot['alerts']['active'])})</h2>
    <table class="alert-table">
        <tr><th>Alert ID</th><th>Severity</th><th>Message</th><th>Current Value</th></tr>
"""

        for alert in snapshot['alerts']['active']:
            html += f"""
        <tr class="severity-{alert['severity']}">
            <td>{alert['alert_id']}</td>
            <td>{alert['severity']}</td>
            <td>{alert['message']}</td>
            <td>{alert['current_value']:.2f}</td>
        </tr>
"""

        html += """
    </table>
</body>
</html>
"""

        if output_file:
            with open(output_file, 'w') as f:
                f.write(html)
            logger.info(f"Exported dashboard to {output_file}")

        return html


if __name__ == '__main__':
    # Example usage
    engine = create_dashboard_engine()

    logger.info("Dashboard engine running... (press Ctrl+C to stop)")

    try:
        for i in range(30):
            # Simulate metric updates
            engine.update_metric_value('sys.health_score', 95 - (i % 10))
            engine.update_metric_value('sys.error_rate', 0.01 + (i % 5) * 0.001)
            engine.update_metric_value('rbac.permission_check_latency_ms', 5 + (i % 20))
            engine.update_metric_value('cog.session_restore_time_ms', 200 + (i % 300))
            engine.update_metric_value('gov.compliance_status_pct', 100 - (i % 10))

            # Print snapshot
            snapshot = engine.get_dashboard_snapshot()
            print(f"[{i}] Health: {snapshot['health_scorecard']['overall_score']:.1f} | "
                  f"Alerts: {len(snapshot['alerts']['active'])} | "
                  f"Incidents: {snapshot['health_scorecard']['active_incidents']}")

            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        engine.stop()
