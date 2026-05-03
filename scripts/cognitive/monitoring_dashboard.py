#!/usr/bin/env python3
"""
Monitoring Dashboard

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/cognitive/monitoring_dashboard.py [options]

    Examples:
    $ python scripts/cognitive/monitoring_dashboard.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""



import json
import logging
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MetricSnapshot:
    """Snapshot of a metric at a point in time"""
    metric_name: str
    value: float
    timestamp: str
    status: str  # "normal", "warning", "critical"


@dataclass
class AlertRule:
    """Rule for triggering alerts"""
    metric_name: str
    threshold: float
    operator: str  # "gt", "lt", "eq"
    severity: str  # "warning", "critical"
    message: str


class MonitoringDashboard:
    """Real-time monitoring dashboard for cognitive brain metrics"""

    def __init__(
        self,
        data_path: str = "cognitive/monitoring",
        history_size: int = 1000,
        refresh_interval: int = 60  # seconds
    ):
        self.data_path = Path(data_path)
        self.history_size = history_size
        self.refresh_interval = refresh_interval

        # Ensure directories exist
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Metric history (using deque for efficient FIFO)
        self.metric_history: dict[str, deque] = {}

        # Alert rules
        self.alert_rules: list[AlertRule] = self._initialize_alert_rules()

        # Active alerts
        self.active_alerts: list[dict[str, Any]] = []

        # Define metrics to monitor
        self.metrics = {
            # Performance metrics
            "perception_latency_ms": {"target": 1000, "unit": "ms"},
            "decision_latency_ms": {"target": 3000, "unit": "ms"},
            "action_latency_ms": {"target": 2000, "unit": "ms"},

            # Accuracy metrics
            "pattern_detection_accuracy": {"target": 0.80, "unit": "ratio"},
            "anomaly_detection_precision": {"target": 0.75, "unit": "ratio"},
            "causal_inference_accuracy": {"target": 0.75, "unit": "ratio"},

            # Resource metrics
            "memory_usage_mb": {"target": 1000, "unit": "MB"},
            "cpu_utilization": {"target": 0.80, "unit": "ratio"},
            "disk_usage_gb": {"target": 50, "unit": "GB"},

            # Success metrics
            "task_success_rate": {"target": 0.85, "unit": "ratio"},
            "auto_fix_success_rate": {"target": 0.80, "unit": "ratio"},

            # System health
            "overall_health_score": {"target": 0.90, "unit": "ratio"},
            "trust_score": {"target": 0.95, "unit": "ratio"},
        }

        # Initialize history for each metric
        for metric in self.metrics:
            self.metric_history[metric] = deque(maxlen=history_size)

    def _initialize_alert_rules(self) -> list[AlertRule]:
        """Initialize default alert rules"""
        return [
            # Performance alerts
            AlertRule(
                metric_name="decision_latency_ms",
                threshold=5000,
                operator="gt",
                severity="warning",
                message="Decision latency exceeding 5 seconds"
            ),
            AlertRule(
                metric_name="decision_latency_ms",
                threshold=10000,
                operator="gt",
                severity="critical",
                message="Decision latency critically high (>10 seconds)"
            ),

            # Accuracy alerts
            AlertRule(
                metric_name="pattern_detection_accuracy",
                threshold=0.70,
                operator="lt",
                severity="warning",
                message="Pattern detection accuracy below 70%"
            ),
            AlertRule(
                metric_name="task_success_rate",
                threshold=0.75,
                operator="lt",
                severity="critical",
                message="Task success rate critically low (<75%)"
            ),

            # Resource alerts
            AlertRule(
                metric_name="memory_usage_mb",
                threshold=2000,
                operator="gt",
                severity="warning",
                message="Memory usage exceeding 2GB"
            ),
            AlertRule(
                metric_name="cpu_utilization",
                threshold=0.90,
                operator="gt",
                severity="critical",
                message="CPU utilization critically high (>90%)"
            ),

            # Health alerts
            AlertRule(
                metric_name="overall_health_score",
                threshold=0.80,
                operator="lt",
                severity="warning",
                message="Overall health score below 80%"
            ),
            AlertRule(
                metric_name="trust_score",
                threshold=0.90,
                operator="lt",
                severity="critical",
                message="Trust score critically low (<90%)"
            ),
        ]

    def collect_metrics(self) -> dict[str, MetricSnapshot]:
        """
        Collect current metrics from all components

        Returns:
            Dictionary of metric snapshots
        """
        logger.info("Collecting current metrics")

        snapshots = {}
        timestamp = datetime.now().isoformat()

        for metric_name, config in self.metrics.items():
            # Collect metric value (simulated for demo)
            value = self._collect_metric_value(metric_name)

            # Determine status based on target
            status = self._determine_status(metric_name, value, config["target"])

            # Create snapshot
            snapshot = MetricSnapshot(
                metric_name=metric_name,
                value=value,
                timestamp=timestamp,
                status=status
            )

            # Add to history
            self.metric_history[metric_name].append(snapshot)

            snapshots[metric_name] = snapshot

        # Check alert rules
        self._check_alerts(snapshots)

        return snapshots

    def _collect_metric_value(self, metric_name: str) -> float:
        """
        Collect actual value for a metric
        In production, this would query actual system metrics
        """
        import random

        import numpy as np

        # Simulate realistic metric values
        if "latency" in metric_name:
            # Latency metrics (ms)
            base = self.metrics[metric_name]["target"]
            value = np.random.normal(base * 0.8, base * 0.2)
            return max(0, value)

        if "accuracy" in metric_name or "precision" in metric_name or "rate" in metric_name:
            # Ratio metrics (0-1)
            target = self.metrics[metric_name]["target"]
            value = np.random.normal(target, 0.05)
            return max(0.0, min(1.0, value))

        if "score" in metric_name:
            # Score metrics (0-1)
            target = self.metrics[metric_name]["target"]
            value = np.random.normal(target, 0.03)
            return max(0.0, min(1.0, value))

        if "memory_usage" in metric_name:
            # Memory in MB
            return random.uniform(500, 1500)

        if "cpu_utilization" in metric_name:
            # CPU utilization (0-1)
            return random.uniform(0.3, 0.85)

        if "disk_usage" in metric_name:
            # Disk in GB
            return random.uniform(10, 60)

        return random.uniform(0.5, 1.0)

    def _determine_status(
        self,
        metric_name: str,
        value: float,
        target: float
    ) -> str:
        """Determine status of a metric based on its value and target"""
        # For latency metrics, lower is better
        if "latency" in metric_name:
            if value <= target:
                return "normal"
            if value <= target * 1.5:
                return "warning"
            return "critical"

        # For most other metrics, higher is better
        if value >= target:
            return "normal"
        if value >= target * 0.85:
            return "warning"
        return "critical"

    def _check_alerts(self, snapshots: dict[str, MetricSnapshot]):
        """Check if any alert rules are triggered"""
        new_alerts = []

        for rule in self.alert_rules:
            snapshot = snapshots.get(rule.metric_name)
            if not snapshot:
                continue

            triggered = False

            if (rule.operator == "gt" and snapshot.value > rule.threshold) or (rule.operator == "lt" and snapshot.value < rule.threshold) or (rule.operator == "eq" and snapshot.value == rule.threshold):
                triggered = True

            if triggered:
                alert = {
                    "metric_name": rule.metric_name,
                    "severity": rule.severity,
                    "message": rule.message,
                    "value": snapshot.value,
                    "threshold": rule.threshold,
                    "timestamp": snapshot.timestamp
                }
                new_alerts.append(alert)
                logger.warning(f"Alert triggered: {rule.message} (value: {snapshot.value})")

        # Update active alerts
        self.active_alerts = new_alerts

        # Save alerts to disk
        if new_alerts:
            self._save_alerts(new_alerts)

    def _save_alerts(self, alerts: list[dict[str, Any]]):
        """Save alerts to disk"""
        alerts_file = self.data_path / f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2)

    def get_metric_history(
        self,
        metric_name: str,
        lookback_seconds: Optional[int] = None
    ) -> list[MetricSnapshot]:
        """
        Get history for a specific metric

        Args:
            metric_name: Name of metric
            lookback_seconds: Optional time window (None = all history)

        Returns:
            List of MetricSnapshot objects
        """
        if metric_name not in self.metric_history:
            return []

        history = list(self.metric_history[metric_name])

        if lookback_seconds:
            cutoff = datetime.now() - timedelta(seconds=lookback_seconds)
            history = [
                s for s in history
                if datetime.fromisoformat(s.timestamp) >= cutoff
            ]

        return history

    def get_current_dashboard(self) -> dict[str, Any]:
        """
        Get current dashboard state with all metrics

        Returns:
            Dashboard state dictionary
        """
        # Collect latest metrics
        snapshots = self.collect_metrics()

        # Calculate summary statistics
        total_metrics = len(snapshots)
        normal_count = sum(1 for s in snapshots.values() if s.status == "normal")
        warning_count = sum(1 for s in snapshots.values() if s.status == "warning")
        critical_count = sum(1 for s in snapshots.values() if s.status == "critical")

        # Overall system status
        if critical_count > 0:
            overall_status = "critical"
        elif warning_count > 0:
            overall_status = "warning"
        else:
            overall_status = "normal"

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "summary": {
                "total_metrics": total_metrics,
                "normal": normal_count,
                "warning": warning_count,
                "critical": critical_count
            },
            "metrics": {
                name: asdict(snapshot)
                for name, snapshot in snapshots.items()
            },
            "active_alerts": self.active_alerts
        }


    def generate_dashboard_html(self, output_path: Optional[str] = None) -> str:
        """
        Generate HTML dashboard for visualization

        Args:
            output_path: Optional path to save HTML file

        Returns:
            HTML content as string
        """
        dashboard = self.get_current_dashboard()

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Cognitive Brain Monitoring Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .status-{dashboard['overall_status']} {{
            color: {"#22c55e" if dashboard['overall_status'] == "normal" else "#f59e0b" if dashboard['overall_status'] == "warning" else "#ef4444"};
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-normal {{ border-left: 4px solid #22c55e; }}
        .metric-warning {{ border-left: 4px solid #f59e0b; }}
        .metric-critical {{ border-left: 4px solid #ef4444; }}
        .alerts {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .alert {{
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .alert-warning {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
        }}
        .alert-critical {{
            background: #fee2e2;
            border-left: 4px solid #ef4444;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Cognitive Brain Monitoring Dashboard</h1>
            <p><strong>Status:</strong> <span class="status-{dashboard['overall_status']}">{dashboard['overall_status'].upper()}</span></p>
            <p><strong>Last Updated:</strong> {dashboard['timestamp']}</p>
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>Total Metrics</h3>
                <h2>{dashboard['summary']['total_metrics']}</h2>
            </div>
            <div class="summary-card">
                <h3>Normal</h3>
                <h2 style="color: #22c55e;">{dashboard['summary']['normal']}</h2>
            </div>
            <div class="summary-card">
                <h3>Warning</h3>
                <h2 style="color: #f59e0b;">{dashboard['summary']['warning']}</h2>
            </div>
            <div class="summary-card">
                <h3>Critical</h3>
                <h2 style="color: #ef4444;">{dashboard['summary']['critical']}</h2>
            </div>
        </div>

        <h2>Metrics</h2>
        <div class="metrics-grid">
"""

        for metric_name, metric_data in dashboard['metrics'].items():
            html_content += f"""
            <div class="metric-card metric-{metric_data['status']}">
                <h4>{metric_name.replace('_', ' ').title()}</h4>
                <p><strong>Value:</strong> {metric_data['value']:.2f}</p>
                <p><strong>Status:</strong> {metric_data['status'].upper()}</p>
            </div>
"""

        html_content += """
        </div>

        <h2>Active Alerts</h2>
        <div class="alerts">
"""

        if dashboard['active_alerts']:
            for alert in dashboard['active_alerts']:
                html_content += f"""
            <div class="alert alert-{alert['severity']}">
                <strong>{alert['severity'].upper()}:</strong> {alert['message']}<br>
                <small>Value: {alert['value']:.2f} | Threshold: {alert['threshold']:.2f} | Time: {alert['timestamp']}</small>
            </div>
"""
        else:
            html_content += "<p>No active alerts</p>"

        html_content += """
        </div>
    </div>

    <script>
        // Auto-refresh every 60 seconds
        setTimeout(function() {
            location.reload();
        }, 60000);
    </script>
</body>
</html>
"""

        # Save HTML if path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(html_content)
            logger.info(f"Dashboard HTML saved to: {output_file}")

        return html_content

    def save_dashboard_state(self):
        """Save current dashboard state to JSON"""
        dashboard = self.get_current_dashboard()

        state_file = self.data_path / f"dashboard_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(state_file, 'w') as f:
            json.dump(dashboard, f, indent=2)

        # Also save as latest
        latest_file = self.data_path / "dashboard_state_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(dashboard, f, indent=2)


def main():
    """Main entry point for monitoring dashboard"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cognitive Brain Monitoring Dashboard"
    )
    parser.add_argument(
        "--mode",
        choices=["once", "continuous", "html"],
        default="once",
        help="Monitoring mode: once (single snapshot), continuous (keep running), html (generate HTML)"
    )
    parser.add_argument(
        "--output",
        default="cognitive/dashboard.html",
        help="Output path for HTML dashboard"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Refresh interval in seconds for continuous mode"
    )

    args = parser.parse_args()

    # Initialize dashboard
    dashboard = MonitoringDashboard(refresh_interval=args.interval)

    if args.mode == "once":
        # Single snapshot
        state = dashboard.get_current_dashboard()

        print(f"\n{'='*60}")
        print("COGNITIVE BRAIN MONITORING DASHBOARD")
        print(f"{'='*60}\n")
        print(json.dumps(state, indent=2))

        dashboard.save_dashboard_state()

    elif args.mode == "continuous":
        # Continuous monitoring
        print(f"Starting continuous monitoring (refresh every {args.interval}s)")
        print("Press Ctrl+C to stop")

        try:
            while True:
                state = dashboard.get_current_dashboard()

                # Clear screen (platform-independent)
                print("\033[2J\033[H", end="")

                print(f"{'='*60}")
                print("COGNITIVE BRAIN MONITORING DASHBOARD")
                print(f"{'='*60}\n")
                print(f"Status: {state['overall_status'].upper()}")
                print(f"Last Updated: {state['timestamp']}\n")

                print(f"Metrics: {state['summary']['normal']} normal, "
                      f"{state['summary']['warning']} warning, "
                      f"{state['summary']['critical']} critical\n")

                if state['active_alerts']:
                    print("⚠️  ACTIVE ALERTS:")
                    for alert in state['active_alerts']:
                        print(f"  - [{alert['severity'].upper()}] {alert['message']}")
                    print()

                dashboard.save_dashboard_state()

                time.sleep(args.interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")

    elif args.mode == "html":
        # Generate HTML dashboard
        dashboard.generate_dashboard_html(output_path=args.output)

        print(f"\n✅ HTML dashboard generated: {args.output}")
        print("Open in browser to view real-time metrics")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
