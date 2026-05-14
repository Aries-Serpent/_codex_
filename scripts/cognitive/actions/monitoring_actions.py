#!/usr/bin/env python3
"""
Monitoring Actions for Cognitive Brain

Proposes and executes autonomous actions based on monitoring sensor data.

Author: GitHub Copilot (AI Agent)
Created: 2026-01-22
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionProposer:
    """Proposes autonomous actions for monitoring failures."""

    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path(".codex/config/monitoring.yaml")
        self.confidence_threshold = 0.8
        self._thresholds = self._default_thresholds()
        self._workflow_overrides: dict[str, dict[str, float]] = {}
        self._config_mtime: Optional[float] = None
        self._load_threshold_config(force=True)

    def _default_thresholds(self) -> dict[str, float]:
        return {
            "severity_threshold": 0.8,
            "consecutive_threshold": 3.0,
            "confidence_threshold": 0.8,
        }

    def _safe_float(self, value: Any, fallback: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return fallback

    def _load_threshold_config(self, force: bool = False):
        defaults = self._default_thresholds()
        attempted_mtime: float | None = None

        if yaml is None:
            self._thresholds = defaults
            self.confidence_threshold = defaults["confidence_threshold"]
            self._workflow_overrides = {}
            return

        if not self.config_file.exists():
            self._thresholds = defaults
            self.confidence_threshold = defaults["confidence_threshold"]
            self._workflow_overrides = {}
            self._config_mtime = None
            return

        try:
            attempted_mtime = self.config_file.stat().st_mtime
            if (
                not force
                and self._config_mtime is not None
                and attempted_mtime == self._config_mtime
            ):
                return

            payload = yaml.safe_load(self.config_file.read_text()) or {}
            cb = payload.get("cognitive_brain", {}) if isinstance(payload, dict) else {}
            thresholds = cb.get("thresholds", {}) if isinstance(cb, dict) else {}

            loaded = {
                "severity_threshold": self._safe_float(thresholds.get("severity_threshold"), defaults["severity_threshold"]),
                "consecutive_threshold": self._safe_float(thresholds.get("consecutive_threshold"), defaults["consecutive_threshold"]),
                "confidence_threshold": self._safe_float(thresholds.get("confidence_threshold"), defaults["confidence_threshold"]),
            }

            self._thresholds = loaded
            self.confidence_threshold = loaded["confidence_threshold"]

            overrides = thresholds.get("per_workflow_overrides", {})
            self._workflow_overrides = overrides if isinstance(overrides, dict) else {}
            self._config_mtime = attempted_mtime
        except Exception as e:
            logger.warning(f"Failed loading threshold config {self.config_file}: {e}")
            self._thresholds = defaults
            self.confidence_threshold = defaults["confidence_threshold"]
            self._workflow_overrides = {}
            if attempted_mtime is not None:
                # Record the failed-attempt mtime so we do not repeatedly reload
                # and re-warn until the file changes again.
                self._config_mtime = attempted_mtime

    def _maybe_reload_config(self):
        if not self.config_file.exists():
            if self._config_mtime is not None:
                self._load_threshold_config(force=True)
            return

        try:
            current = self.config_file.stat().st_mtime
            if self._config_mtime is None or current != self._config_mtime:
                self._load_threshold_config(force=True)
        except Exception as e:
            logger.warning(f"Failed checking threshold config mtime: {e}")

    def _thresholds_for_workflow(self, workflow: str | None) -> dict[str, float]:
        thresholds = dict(self._thresholds)
        if workflow and workflow in self._workflow_overrides:
            override = self._workflow_overrides.get(workflow, {})
            if isinstance(override, dict):
                thresholds["severity_threshold"] = self._safe_float(
                    override.get("severity_threshold"), thresholds["severity_threshold"]
                )
                thresholds["consecutive_threshold"] = self._safe_float(
                    override.get("consecutive_threshold"), thresholds["consecutive_threshold"]
                )
                thresholds["confidence_threshold"] = self._safe_float(
                    override.get("confidence_threshold"), thresholds["confidence_threshold"]
                )
        return thresholds

    def propose_actions(self, failures: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Propose actions for workflow failures.

        Args:
            failures: List of failure dictionaries from sensor

        Returns:
            List of proposed actions with confidence scores
        """
        self._maybe_reload_config()
        actions = []

        for failure in failures:
            workflow = failure.get("workflow")
            severity = failure.get("severity", 0)
            consecutive = failure.get("consecutive_failures", 0)

            thresholds = self._thresholds_for_workflow(workflow)
            severity_threshold = thresholds["severity_threshold"]
            consecutive_threshold = int(thresholds["consecutive_threshold"])
            medium_severity = max(severity_threshold - 0.3, 0.0)
            medium_consecutive = max(consecutive_threshold - 1, 1)

            # High severity - immediate action
            if severity >= severity_threshold and consecutive >= consecutive_threshold:
                actions.append({
                    "action_type": "rerun_workflow",
                    "workflow": workflow,
                    "reason": f"Critical failure ({consecutive} consecutive)",
                    "confidence": 0.9,
                    "risk": "low",
                    "requires_approval": False
                })

            # Medium severity - investigate
            elif severity >= medium_severity and consecutive >= medium_consecutive:
                actions.append({
                    "action_type": "analyze_logs",
                    "workflow": workflow,
                    "reason": f"Persistent failure ({consecutive} consecutive)",
                    "confidence": 0.75,
                    "risk": "low",
                    "requires_approval": False
                })

            # Low severity - monitor
            else:
                actions.append({
                    "action_type": "monitor",
                    "workflow": workflow,
                    "reason": "Flaky test suspected",
                    "confidence": 0.6,
                    "risk": "none",
                    "requires_approval": False
                })

        return actions

    def execute_action(self, action: dict[str, Any], dry_run: bool = True) -> dict[str, Any]:
        """
        Execute proposed action (with safety checks).

        Args:
            action: Action dictionary
            dry_run: If True, simulate execution

        Returns:
            Execution result
        """
        self._maybe_reload_config()
        action_type = action.get("action_type")
        workflow = action.get("workflow")
        confidence = action.get("confidence", 0)
        thresholds = self._thresholds_for_workflow(workflow)
        confidence_threshold = thresholds["confidence_threshold"]

        if confidence < confidence_threshold:
            return {
                "status": "skipped",
                "reason": f"Confidence {confidence} below threshold {confidence_threshold}"
            }

        if action.get("requires_approval") and not dry_run:
            return {
                "status": "pending_approval",
                "reason": "Action requires human approval"
            }

        if dry_run:
            return {
                "status": "simulated",
                "action_type": action_type,
                "workflow": workflow,
                "message": f"Would execute {action_type} for {workflow}"
            }

        # Execute actual action (placeholder - would integrate with GitHub API)
        try:
            if action_type == "rerun_workflow":
                # Would call: gh workflow run {workflow}
                return {
                    "status": "executed",
                    "action_type": action_type,
                    "workflow": workflow,
                    "message": f"Workflow {workflow} rerun initiated"
                }
            if action_type == "analyze_logs":
                return {
                    "status": "executed",
                    "action_type": action_type,
                    "workflow": workflow,
                    "message": f"Log analysis initiated for {workflow}"
                }
            return {
                "status": "executed",
                "action_type": action_type,
                "workflow": workflow
            }
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }


def main():
    """CLI interface for action proposer."""
    import argparse

    from scripts.cognitive.sensors.monitoring_sensor import MonitoringSensor

    parser = argparse.ArgumentParser(description="Monitoring Actions for Cognitive Brain")
    parser.add_argument("--propose", action="store_true", help="Propose actions for failures")
    parser.add_argument("--execute", action="store_true", help="Execute proposed actions")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Simulate execution")
    args = parser.parse_args()

    sensor = MonitoringSensor()
    proposer = ActionProposer()

    failures = sensor.get_active_failures()

    if not failures:
        print("No active failures requiring action")
        return

    actions = proposer.propose_actions(failures)

    if args.propose:
        print(json.dumps(actions, indent=2))
    elif args.execute:
        for action in actions:
            result = proposer.execute_action(action, dry_run=args.dry_run)
            print(json.dumps(result, indent=2))
    else:
        print(f"Proposed {len(actions)} actions for {len(failures)} failures")
        for action in actions:
            print(f"- {action['action_type']} for {action['workflow']} (confidence: {action['confidence']})")


if __name__ == "__main__":
    main()
