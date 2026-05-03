#!/usr/bin/env python3
"""
Monitoring Sensor for Cognitive Brain Integration

Exposes artifact monitoring system state to the Cognitive Brain
for autonomous decision-making and self-healing capabilities.

Author: GitHub Copilot (AI Agent)
Created: 2026-01-22
Version: 1.0.0
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringSensor:
    """Cognitive Brain sensor for artifact monitoring system."""

    def __init__(self, state_file: Optional[Path] = None):
        self.state_file = state_file or Path(".codex/monitoring/state/monitor_state.json")

    def get_system_health(self) -> dict[str, any]:
        """Get overall monitoring system health status."""
        try:
            state = self._load_state()
            workflows = state.get("workflows", {})
            total = len(workflows)
            failing = sum(1 for w in workflows.values() if w.get("last_status") == "failure")
            health_score = (total - failing) / total * 100 if total > 0 else 100

            return {
                "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "critical",
                "health_score": health_score,
                "total_workflows": total,
                "failing_workflows": failing,
                "last_check": state.get("last_run"),
                "metrics": state.get("metrics", {})
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {"status": "unknown", "error": str(e)}

    def get_active_failures(self) -> list[dict[str, any]]:
        """Get list of currently active workflow failures."""
        try:
            state = self._load_state()
            workflows = state.get("workflows", {})
            active_failures = []

            for name, data in workflows.items():
                if data.get("last_status") == "failure" and data.get("consecutive_failures", 0) >= 2:
                    active_failures.append({
                        "workflow": name,
                        "consecutive_failures": data.get("consecutive_failures", 0),
                        "failure_rate": data.get("failure_rate", 0),
                        "last_failure": data.get("last_failure"),
                        "open_issue": data.get("open_issue_number"),
                        "severity": self._calculate_severity(data)
                    })

            active_failures.sort(key=lambda x: x["severity"], reverse=True)
            return active_failures
        except Exception as e:
            logger.error(f"Error getting active failures: {e}")
            return []

    def should_propose_action(self) -> tuple[bool, str, float]:
        """Determine if Cognitive Brain should propose an autonomous action."""
        try:
            health = self.get_system_health()
            failures = self.get_active_failures()

            health_score = health.get("health_score", 100)
            critical_failures = len([f for f in failures if f["severity"] >= 0.8])

            if health_score < 50 and critical_failures >= 3:
                return True, "Critical system health with multiple severe failures", 0.9
            if health_score < 80 and critical_failures >= 2:
                return True, "Degraded health with critical failures", 0.75
            if health_score < 80:
                return False, "System degraded but not critical", 0.5
            return False, "System healthy, no action needed", 0.3
        except Exception as e:
            logger.error(f"Error in action decision: {e}")
            return False, f"Error: {e}", 0.0

    def export_state_for_cognitive_brain(self) -> dict[str, any]:
        """Export complete monitoring state for Cognitive Brain."""
        return {
            "sensor_type": "artifact_monitoring",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system_health": self.get_system_health(),
            "active_failures": self.get_active_failures(),
            "action_recommendation": self.should_propose_action()
        }

    def _load_state(self) -> dict[str, any]:
        """Load monitoring state from JSON file."""
        try:
            if self.state_file.exists():
                with open(self.state_file) as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return {}

    def _calculate_severity(self, workflow_data: dict[str, any]) -> float:
        """Calculate failure severity (0.0-1.0)."""
        consecutive = workflow_data.get("consecutive_failures", 0)
        failure_rate = workflow_data.get("failure_rate", 0)
        return min((consecutive / 10 * 0.6) + (failure_rate * 0.4), 1.0)


def main():
    """CLI interface for monitoring sensor."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitoring Sensor for Cognitive Brain")
    parser.add_argument("--health", action="store_true", help="Get system health")
    parser.add_argument("--failures", action="store_true", help="Get active failures")
    parser.add_argument("--export", action="store_true", help="Export full state")
    args = parser.parse_args()

    sensor = MonitoringSensor()

    if args.health:
        print(json.dumps(sensor.get_system_health(), indent=2))
    elif args.failures:
        print(json.dumps(sensor.get_active_failures(), indent=2))
    elif args.export:
        print(json.dumps(sensor.export_state_for_cognitive_brain(), indent=2))
    else:
        health = sensor.get_system_health()
        should_act, reason, confidence = sensor.should_propose_action()
        print(f"System Health: {health['status']} ({health['health_score']:.1f}%)")
        print(f"Action Needed: {should_act}")
        if should_act:
            print(f"Reason: {reason} (Confidence: {confidence:.2f})")


if __name__ == "__main__":
    main()
