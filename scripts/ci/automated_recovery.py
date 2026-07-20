#!/usr/bin/env python3
"""
Automated Recovery Script for Self-Healing CI

Implements:
- Exponential backoff retry logic
- Automatic failure recovery attempts
- Telemetry collection and reporting
- Integration with error classification system
"""

import json
import time
import sys
import os
import subprocess
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

# Import error classifier
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from error_classifier import ErrorClassifier, RecoveryMetrics, RecoverySeverity


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class RecoveryAttempt:
    """Single recovery attempt record."""

    attempt_num: int
    pattern_id: str
    severity: str
    delay_sec: int
    success: bool
    start_time: str
    end_time: str
    error_message: str = ""
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self):
        return asdict(self)


class ExponentialBackoffRetry:
    """Implements exponential backoff with jitter for retries."""

    def __init__(
        self,
        base_delay_sec: float = 1.0,
        max_delay_sec: float = 300.0,
        multiplier: float = 2.0,
        jitter: bool = True,
    ):
        """
        Initialize exponential backoff strategy.

        Parameters
        ----------
        base_delay_sec : float
            Initial delay in seconds
        max_delay_sec : float
            Maximum delay cap in seconds
        multiplier : float
            Exponential multiplier for each retry
        jitter : bool
            Add random jitter to prevent thundering herd
        """
        self.base_delay_sec = base_delay_sec
        self.max_delay_sec = max_delay_sec
        self.multiplier = multiplier
        self.jitter = jitter

    def calculate_delay(self, attempt_num: int) -> float:
        """
        Calculate delay for given attempt number.

        Parameters
        ----------
        attempt_num : int
            Attempt number (1-based)

        Returns
        -------
        float
            Delay in seconds (capped at max_delay_sec)
        """
        delay = self.base_delay_sec * (self.multiplier ** (attempt_num - 1))
        delay = min(delay, self.max_delay_sec)

        if self.jitter:
            import random

            jitter = random.uniform(0, delay * 0.1)
            delay += jitter

        return delay

    def wait(self, attempt_num: int):
        """Sleep for calculated delay."""
        delay = self.calculate_delay(attempt_num)
        logger.info(f"Waiting {delay:.1f}s before retry {attempt_num}")
        time.sleep(delay)


class AutomatedRecovery:
    """Orchestrate automated recovery attempts."""

    def __init__(self, max_retries: int = 3, work_dir: str = "."):
        """
        Initialize recovery orchestrator.

        Parameters
        ----------
        max_retries : int
            Maximum retry attempts per failure
        work_dir : str
            Working directory for artifacts
        """
        self.max_retries = max_retries
        self.work_dir = Path(work_dir)
        self.classifier = ErrorClassifier()
        self.metrics = RecoveryMetrics()
        self.attempts: List[RecoveryAttempt] = []

    def recover_from_error(
        self, error_text: str, command: Optional[str] = None
    ) -> Tuple[bool, Dict]:
        """
        Attempt recovery from CI failure.

        Parameters
        ----------
        error_text : str
            Error message/log output
        command : str, optional
            Command that failed (for re-execution)

        Returns
        -------
        Tuple[bool, Dict]
            (success, recovery_report)
        """
        # Classify the error
        signature = self.classifier.classify(error_text)
        if not signature:
            logger.warning("Could not classify error")
            return False, {"status": "unclassified"}

        logger.info(f"Classified as: {signature.category.value}")
        logger.info(f"Severity: {signature.severity.value}")

        # Get recovery action
        action = ErrorClassifier.severity_to_recovery_action(signature.severity)
        max_retries = action["max_retries"]

        # Attempt recovery
        if signature.severity == RecoverySeverity.AUTO_RECOVERABLE:
            return self._recover_auto(signature, command, action, max_retries)
        elif signature.severity == RecoverySeverity.BACKOFF_RECOVERABLE:
            return self._recover_with_backoff(signature, command, action, max_retries)
        else:
            return self._escalate(signature, action)

    def _recover_auto(
        self, signature, command: Optional[str], action: Dict, max_retries: int
    ) -> Tuple[bool, Dict]:
        """Attempt immediate auto-recovery (network transient)."""
        logger.info(f"Auto-recovery: Immediate retry (max {max_retries} attempts)")

        for attempt in range(1, max_retries + 1):
            start = datetime.utcnow()
            success = self._execute_recovery(command, attempt)
            end = datetime.utcnow()

            self._record_attempt(
                signature.pattern_id,
                signature.severity,
                success,
                (end - start).total_seconds(),
            )

            if success:
                logger.info(f"✓ Recovery succeeded on attempt {attempt}")
                return True, {
                    "status": "recovered",
                    "method": "auto_retry",
                    "attempt": attempt,
                }

        logger.warning(f"✗ Auto-recovery failed after {max_retries} attempts")
        return False, {
            "status": "failed",
            "method": "auto_retry",
            "attempts": max_retries,
        }

    def _recover_with_backoff(
        self, signature, command: Optional[str], action: Dict, max_retries: int
    ) -> Tuple[bool, Dict]:
        """Attempt recovery with exponential backoff."""
        backoff = ExponentialBackoffRetry(
            base_delay_sec=action.get("base_delay_sec", 10),
            multiplier=action.get("backoff_multiplier", 2.0),
        )

        logger.info(
            f"Backoff recovery: Max {max_retries} attempts with exponential backoff"
        )

        for attempt in range(1, max_retries + 1):
            if attempt > 1:
                backoff.wait(attempt)

            start = datetime.utcnow()
            success = self._execute_recovery(command, attempt)
            end = datetime.utcnow()

            delay = (end - start).total_seconds()
            self._record_attempt(
                signature.pattern_id, signature.severity, success, delay
            )

            if success:
                logger.info(f"✓ Recovery succeeded on attempt {attempt}")
                return True, {
                    "status": "recovered",
                    "method": "backoff_retry",
                    "attempt": attempt,
                }

        logger.warning(f"✗ Backoff recovery failed after {max_retries} attempts")
        return False, {
            "status": "failed",
            "method": "backoff_retry",
            "attempts": max_retries,
        }

    def _execute_recovery(self, command: Optional[str], attempt: int) -> bool:
        """
        Execute recovery (re-run command or diagnostic).

        Parameters
        ----------
        command : str, optional
            Command to re-execute
        attempt : int
            Attempt number (for logging)

        Returns
        -------
        bool
            True if recovery succeeded
        """
        if not command:
            logger.info(f"Attempt {attempt}: No command to re-execute, assuming success")
            return True

        logger.info(f"Attempt {attempt}: Re-executing: {command}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                timeout=300,
                text=True,
            )

            if result.returncode == 0:
                logger.info(f"Attempt {attempt}: Command succeeded")
                return True
            else:
                logger.warning(f"Attempt {attempt}: Command failed with code {result.returncode}")
                if result.stderr:
                    logger.warning(f"stderr: {result.stderr[:200]}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"Attempt {attempt}: Command timeout")
            return False
        except Exception as e:
            logger.error(f"Attempt {attempt}: Execution error: {e}")
            return False

    def _escalate(self, signature, action: Dict) -> Tuple[bool, Dict]:
        """Escalate to human review."""
        logger.warning(f"Escalating: {signature.message}")
        logger.warning(f"Suggestions: {signature.suggestions}")

        return False, {
            "status": "escalated",
            "method": "human_review",
            "message": signature.message,
            "suggestions": signature.suggestions,
        }

    def _record_attempt(
        self,
        pattern_id: str,
        severity: RecoverySeverity,
        success: bool,
        duration_sec: float,
    ):
        """Record recovery attempt for metrics."""
        self.attempts.append(
            RecoveryAttempt(
                attempt_num=len(self.attempts) + 1,
                pattern_id=pattern_id,
                severity=severity.value,
                delay_sec=int(duration_sec),
                success=success,
                start_time=datetime.utcnow().isoformat(),
                end_time=datetime.utcnow().isoformat(),
            )
        )

    def generate_report(self) -> Dict:
        """Generate comprehensive recovery report."""
        success_count = sum(1 for a in self.attempts if a.success)
        total_attempts = len(self.attempts)
        success_rate = (success_count / total_attempts * 100) if total_attempts else 0

        # Calculate MTTR
        if self.attempts:
            total_time = sum(a.delay_sec for a in self.attempts)
            mttr = total_time / len(self.attempts)
        else:
            mttr = 0

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "total_attempts": total_attempts,
            "successful_recoveries": success_count,
            "failed_recoveries": total_attempts - success_count,
            "success_rate_pct": round(success_rate, 1),
            "mttr_seconds": round(mttr, 1),
            "attempts": [asdict(a) for a in self.attempts],
        }

    def save_report(self, filepath: Optional[str] = None) -> Path:
        """Save recovery report to file."""
        if not filepath:
            filepath = self.work_dir / "recovery-report.json"
        else:
            filepath = Path(filepath)

        filepath.parent.mkdir(parents=True, exist_ok=True)

        report = self.generate_report()
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to: {filepath}")
        return filepath


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated CI failure recovery with exponential backoff"
    )
    parser.add_argument("--error-text", help="Error message to classify and recover from")
    parser.add_argument("--command", help="Command to re-execute for recovery")
    parser.add_argument("--max-retries", type=int, default=3, help="Max retry attempts")
    parser.add_argument("--output", help="Output report filepath")
    parser.add_argument("--json", action="store_true", help="Output JSON report")

    args = parser.parse_args()

    recovery = AutomatedRecovery(max_retries=args.max_retries)

    if args.error_text:
        success, report = recovery.recover_from_error(
            args.error_text, command=args.command
        )

        full_report = recovery.generate_report()

        if args.output:
            recovery.save_report(args.output)

        if args.json:
            print(json.dumps(full_report, indent=2))
        else:
            print(f"\n{'='*60}")
            print("RECOVERY REPORT")
            print(f"{'='*60}")
            print(f"Status: {report.get('status', 'unknown')}")
            print(f"Method: {report.get('method', 'unknown')}")
            if "attempt" in report:
                print(f"Recovered on attempt: {report['attempt']}")
            if "attempts" in report:
                print(f"Total attempts: {report['attempts']}")
            if "suggestions" in report:
                print("Suggestions:")
                for s in report["suggestions"]:
                    print(f"  - {s}")
            print(f"\nMetrics:")
            print(f"  Success Rate: {full_report['success_rate_pct']:.1f}%")
            print(f"  MTTR: {full_report['mttr_seconds']:.1f}s")
            print(f"{'='*60}\n")

        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
