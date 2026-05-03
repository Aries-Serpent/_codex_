#!/usr/bin/env python3
"""
Self-Healing Validation Loop for Monitoring System

Validates autonomous actions and adjusts confidence thresholds based on outcomes.

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


class SelfHealingValidator:
    """Validates autonomous actions and learns from outcomes."""

    def __init__(self, history_file: Optional[Path] = None):
        self.history_file = history_file or Path(".codex/monitoring/state/self_healing_history.json")
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def validate_action_outcome(self, action: dict[str, any], outcome: dict[str, any]) -> dict[str, any]:
        """
        Validate outcome of an autonomous action.

        Args:
            action: The action that was executed
            outcome: The result of the action

        Returns:
            Validation result with confidence adjustment
        """
        workflow = action.get("workflow")
        action_type = action.get("action_type")
        initial_confidence = action.get("confidence", 0)

        # Check if action was successful
        success = outcome.get("status") == "success"

        # Calculate confidence adjustment
        if success:
            confidence_delta = +0.05  # Increase confidence
            validation_status = "validated"
        else:
            confidence_delta = -0.1  # Decrease confidence
            validation_status = "failed"

        new_confidence = max(0.0, min(1.0, initial_confidence + confidence_delta))

        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workflow": workflow,
            "action_type": action_type,
            "validation_status": validation_status,
            "initial_confidence": initial_confidence,
            "confidence_adjustment": confidence_delta,
            "new_confidence": new_confidence,
            "success": success
        }

        # Save to history
        self._save_to_history(result)

        return result

    def get_confidence_for_action(self, action_type: str, workflow: str) -> float:
        """Get adjusted confidence for action type based on history."""
        history = self._load_history()

        # Filter relevant actions
        relevant = [h for h in history
                   if h.get("action_type") == action_type
                   and h.get("workflow") == workflow]

        if not relevant:
            return 0.7  # Default confidence

        # Calculate average confidence from recent outcomes
        recent = relevant[-10:]  # Last 10 actions
        return sum(h.get("new_confidence", 0.7) for h in recent) / len(recent)


    def _load_history(self) -> list[dict[str, any]]:
        """Load self-healing history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file) as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return []

    def _save_to_history(self, result: dict[str, any]):
        """Save validation result to history."""
        try:
            history = self._load_history()
            history.append(result)

            # Keep last 1000 entries
            if len(history) > 1000:
                history = history[-1000:]

            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving history: {e}")


def main():
    """CLI interface for self-healing validator."""
    import argparse

    parser = argparse.ArgumentParser(description="Self-Healing Validation Loop")
    parser.add_argument("--history", action="store_true", help="Show validation history")
    parser.add_argument("--stats", action="store_true", help="Show validation statistics")
    args = parser.parse_args()

    validator = SelfHealingValidator()

    if args.history:
        history = validator._load_history()
        print(json.dumps(history[-20:], indent=2))  # Last 20 entries
    elif args.stats:
        history = validator._load_history()
        total = len(history)
        successful = len([h for h in history if h.get("success")])
        print(f"Total Validations: {total}")
        print(f"Successful: {successful} ({successful/total*100:.1f}%)")
        print(f"Failed: {total-successful} ({(total-successful)/total*100:.1f}%)")
    else:
        print("Self-Healing Validator ready")
        print("Use --history to view history or --stats for statistics")


if __name__ == "__main__":
    main()
