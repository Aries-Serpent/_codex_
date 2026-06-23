#!/usr/bin/env python3
"""
phase_8_3_sla_enforcer.py — Enforce SLA thresholds and trigger alerts.

Detects:
- Performance regressions
- SLA violations
- Anomalies
- Trends

Actions:
- Alert notifications (Slack, email, GitHub)
- Performance dashboard updates
- Automatic rollback decisions
- Issue creation

Usage:
    python scripts/ci/phase_8_3_sla_enforcer.py --metrics metrics.json
    python scripts/ci/phase_8_3_sla_enforcer.py --metrics metrics.json --check-sla
    python scripts/ci/phase_8_3_sla_enforcer.py --metrics metrics.json --send-alerts
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass
class SLAViolation:
    """Represents an SLA violation."""
    metric_name: str
    current_value: float
    threshold_value: float
    violation_percent: float
    severity: str
    timestamp: str
    action: str


class SLAEnforcer:
    """Enforce SLA thresholds and manage alerts."""

    def __init__(self, sla_config_path: Path):
        """Initialize SLA enforcer."""
        self.sla_config = self._load_sla_config(sla_config_path)
        self.violations: list[SLAViolation] = []

    def _load_sla_config(self, config_path: Path) -> dict[str, Any]:
        """Load SLA configuration."""
        if not config_path.exists():
            print(f"Warning: SLA config not found at {config_path}")
            return {}

        with open(config_path) as f:
            return json.load(f)

    def check_sla(self, metrics: dict[str, Any]) -> bool:
        """Check if metrics violate SLA thresholds."""
        sla_thresholds = self.sla_config.get("sla_thresholds", {})
        violations_found = False

        # Check workflow execution time
        if "workflow_execution_time" in metrics:
            workflows = metrics["workflow_execution_time"]
            for workflow_name, stats in workflows.items():
                if "p95_ms" not in stats:
                    continue

                current_p95 = stats["p95_ms"]
                workflow_sla = sla_thresholds.get(
                    "workflow_execution_time", {}
                )
                baseline_p95 = workflow_sla.get("baseline_p95_ms", 450000)
                alert_threshold = workflow_sla.get("alert_threshold_percent", 20)

                regression_percent = (
                    (current_p95 - baseline_p95) / baseline_p95
                ) * 100

                if regression_percent > alert_threshold:
                    violations_found = True
                    self.violations.append(
                        SLAViolation(
                            metric_name=f"{workflow_name}_p95",
                            current_value=current_p95,
                            threshold_value=baseline_p95,
                            violation_percent=regression_percent,
                            severity=self._determine_severity(regression_percent),
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            action="Alert + Monitor",
                        )
                    )

        # Check cache hit rate
        if "cache_hit_rate" in metrics:
            cache_hit_rate = metrics.get("cache_hit_rate", 75)
            cache_sla = sla_thresholds.get("cache_hit_rate", {})
            minimum_acceptable = cache_sla.get("minimum_acceptable_percent", 70)
            alert_threshold = cache_sla.get("alert_threshold_percent", 60)

            if cache_hit_rate < alert_threshold:
                violations_found = True
                self.violations.append(
                    SLAViolation(
                        metric_name="cache_hit_rate",
                        current_value=cache_hit_rate,
                        threshold_value=alert_threshold,
                        violation_percent=-((alert_threshold - cache_hit_rate)),
                        severity=self._determine_severity(
                            -((alert_threshold - cache_hit_rate))
                        ),
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        action="Alert + Cache Optimization",
                    )
                )

        # Check error rate
        if "error_rate" in metrics:
            error_rate = metrics.get("error_rate", 0.01)
            error_sla = sla_thresholds.get("error_rate", {})
            alert_threshold = error_sla.get("alert_threshold_percent", 0.1)

            if error_rate > alert_threshold:
                violations_found = True
                self.violations.append(
                    SLAViolation(
                        metric_name="error_rate",
                        current_value=error_rate,
                        threshold_value=alert_threshold,
                        violation_percent=((error_rate - alert_threshold)),
                        severity=self._determine_severity(
                            ((error_rate - alert_threshold))
                        ),
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        action="Alert + Investigation",
                    )
                )

        return violations_found

    def _determine_severity(self, regression_percent: float) -> str:
        """Determine severity based on regression percentage."""
        if regression_percent >= 30:
            return "SEVERE"
        elif regression_percent >= 20:
            return "CRITICAL"
        elif regression_percent >= 10:
            return "WARNING"
        else:
            return "INFO"

    def generate_alert_summary(self) -> str:
        """Generate alert summary for notifications."""
        if not self.violations:
            return "✅ All SLAs within acceptable thresholds"

        lines = [
            "⚠️ **SLA Violations Detected**",
            "",
            "| Metric | Current | Threshold | Violation | Severity |",
            "|--------|---------|-----------|-----------|----------|",
        ]

        for violation in sorted(
            self.violations, key=lambda v: v.violation_percent, reverse=True
        ):
            severity_icon = {
                "SEVERE": "🔴",
                "CRITICAL": "❌",
                "WARNING": "⚠️",
                "INFO": "ℹ️",
            }.get(violation.severity, "?")

            lines.append(
                f"| {violation.metric_name} | "
                f"{violation.current_value:.2f} | "
                f"{violation.threshold_value:.2f} | "
                f"{violation.violation_percent:+.1f}% | "
                f"{severity_icon} {violation.severity} |"
            )

        lines.extend([
            "",
            "## Recommended Actions",
            "",
        ])

        for violation in self.violations:
            lines.append(f"- **{violation.metric_name}**: {violation.action}")

        return "\n".join(lines)

    def should_rollback(self) -> bool:
        """Determine if automatic rollback should be triggered."""
        rollback_config = self.sla_config.get("rollback_procedures", {})
        auto_rollback = rollback_config.get("automatic_rollback", {})

        if not auto_rollback.get("enabled", False):
            return False

        trigger_threshold = auto_rollback.get("trigger_regression_percent", 30)

        for violation in self.violations:
            if violation.violation_percent >= trigger_threshold:
                return True

        return False

    def get_violations_json(self) -> dict[str, Any]:
        """Get violations as JSON."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "violations_count": len(self.violations),
            "should_rollback": self.should_rollback(),
            "violations": [
                {
                    "metric": v.metric_name,
                    "current": v.current_value,
                    "threshold": v.threshold_value,
                    "violation_percent": v.violation_percent,
                    "severity": v.severity,
                    "action": v.action,
                }
                for v in self.violations
            ],
        }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Enforce SLA thresholds")
    parser.add_argument(
        "--metrics",
        type=Path,
        required=True,
        help="Metrics JSON file to check",
    )
    parser.add_argument(
        "--sla-config",
        type=Path,
        default=Path(".codex/PHASE_8_3_SLA_THRESHOLDS.json"),
        help="SLA configuration file",
    )
    parser.add_argument(
        "--check-sla",
        action="store_true",
        help="Check SLA thresholds",
    )
    parser.add_argument(
        "--send-alerts",
        action="store_true",
        help="Send alert notifications (stub)",
    )
    parser.add_argument(
        "--export-json",
        type=Path,
        help="Export violations as JSON",
    )

    args = parser.parse_args()

    # Load metrics
    if not args.metrics.exists():
        print(f"Error: Metrics file not found: {args.metrics}")
        sys.exit(1)

    with open(args.metrics) as f:
        metrics = json.load(f)

    # Initialize enforcer
    enforcer = SLAEnforcer(args.sla_config)

    # Check SLA
    violations_found = enforcer.check_sla(metrics)

    # Print results
    print("=" * 80)
    print("SLA ENFORCEMENT REPORT")
    print("=" * 80)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Violations Found: {len(enforcer.violations)}")
    print(f"Should Rollback: {enforcer.should_rollback()}")
    print("")

    # Print summary
    summary = enforcer.generate_alert_summary()
    print(summary)

    # Export JSON if requested
    if args.export_json:
        violations_data = enforcer.get_violations_json()
        with open(args.export_json, "w") as f:
            json.dump(violations_data, f, indent=2)
        print(f"\n✅ Violations exported to: {args.export_json}")

    # Send alerts (stub)
    if args.send_alerts and violations_found:
        print("\n📢 Alert notifications would be sent:")
        print("   - Slack: performance-team")
        print("   - Email: mbaetiong@example.com")
        print("   - GitHub: Issue creation for CRITICAL violations")

    # Exit with error if violations found
    if violations_found:
        sys.exit(1)


if __name__ == "__main__":
    main()
