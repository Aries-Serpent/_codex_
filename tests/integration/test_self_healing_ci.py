#!/usr/bin/env python3
"""
Integration Tests for Self-Healing CI Infrastructure

Tests:
- Error classification accuracy
- Exponential backoff calculation
- Recovery attempt tracking
- Telemetry collection and metrics
- Health score calculation
- AAIS reliability delta estimation
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts" / "ci"))

from automated_recovery import ExponentialBackoffRetry
from error_classifier import (
    ErrorCategory,
    ErrorClassifier,
    RecoveryMetrics,
    RecoverySeverity,
)
from telemetry_monitor import TelemetryCollector


class TestSuite:
    """Run integration tests for self-healing infrastructure."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_error_classification(self):
        """Test error classification system."""
        print("\n=== Testing Error Classification ===")
        classifier = ErrorClassifier()

        test_cases = [
            # (error_text, expected_category, description)
            (
                "Error: Connection refused - Failed to connect to api.github.com:443",
                ErrorCategory.NETWORK_TRANSIENT,
                "Network connection refused",
            ),
            (
                "SIGTERM signal: terminated",
                ErrorCategory.TIMEOUT_EXCEEDED,
                "Timeout signal",
            ),
            (
                "MemoryError: Unable to allocate 2.00 GiB for an array",
                ErrorCategory.RESOURCE_EXHAUSTION,
                "Memory exhaustion",
            ),
            (
                "ModuleNotFoundError: No module named 'pytest'",
                ErrorCategory.IMPORT_ERROR,
                "Module import error",
            ),
            (
                "invalid yaml: expected ',' but found '\n'",
                ErrorCategory.WORKFLOW_SYNTAX,
                "YAML syntax error",
            ),
            (
                "PermissionError: [Errno 13] Permission denied",
                ErrorCategory.SECURITY_POLICY,
                "Permission denied",
            ),
            (
                "AssertionError: expected 10 but got 9",
                ErrorCategory.LOGIC_ERROR,
                "Logic error",
            ),
        ]

        for error_text, expected_category, description in test_cases:
            signature = classifier.classify(error_text)
            if signature.category == expected_category:
                print(f"✓ {description}")
                self.passed += 1
            else:
                print(
                    f"✗ {description}: got {signature.category}, expected {expected_category}"
                )
                self.failed += 1
                self.errors.append(
                    f"Classification mismatch: {description}"
                )

    def test_recovery_severity(self):
        """Test recovery severity assignment."""
        print("\n=== Testing Recovery Severity ===")
        classifier = ErrorClassifier()

        test_cases = [
            # (error_text, expected_severity, description)
            ("Connection refused", RecoverySeverity.AUTO_RECOVERABLE, "Network error"),
            ("SIGTERM", RecoverySeverity.BACKOFF_RECOVERABLE, "Timeout error"),
            ("MemoryError", RecoverySeverity.BACKOFF_RECOVERABLE, "Resource error"),
            ("Invalid workflow", RecoverySeverity.ESCALATE_REQUIRED, "Syntax error"),
        ]

        for error_text, expected_severity, description in test_cases:
            signature = classifier.classify(error_text)
            if signature.severity == expected_severity:
                print(f"✓ {description}")
                self.passed += 1
            else:
                print(
                    f"✗ {description}: got {signature.severity}, expected {expected_severity}"
                )
                self.failed += 1
                self.errors.append(
                    f"Severity mismatch: {description}"
                )

    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        print("\n=== Testing Exponential Backoff ===")
        backoff = ExponentialBackoffRetry(
            base_delay_sec=1.0,
            max_delay_sec=300.0,
            multiplier=2.0,
            jitter=False,  # Disable jitter for deterministic testing
        )

        test_cases = [
            (1, 1.0),  # First attempt: base delay
            (2, 2.0),  # Second attempt: 1 * 2^(2-1) = 2
            (3, 4.0),  # Third attempt: 1 * 2^(3-1) = 4
            (4, 8.0),  # Fourth attempt: 1 * 2^(4-1) = 8
            (10, 512.0),  # Tenth attempt: 1 * 2^(10-1) = 512 (capped at 300)
        ]

        for attempt_num, expected_delay in test_cases:
            delay = backoff.calculate_delay(attempt_num)
            expected_capped = min(expected_delay, 300.0)
            if delay == expected_capped:
                print(f"✓ Attempt {attempt_num}: {delay}s")
                self.passed += 1
            else:
                print(
                    f"✗ Attempt {attempt_num}: got {delay}s, expected {expected_capped}s"
                )
                self.failed += 1
                self.errors.append(
                    f"Backoff calculation mismatch: attempt {attempt_num}"
                )

    def test_recovery_metrics(self):
        """Test recovery metrics calculation."""
        print("\n=== Testing Recovery Metrics ===")
        metrics = RecoveryMetrics()

        # Record some attempts
        metrics.record_attempt("net-conn", RecoverySeverity.AUTO_RECOVERABLE, True, 5)
        metrics.record_attempt("net-conn", RecoverySeverity.AUTO_RECOVERABLE, True, 5)
        metrics.record_attempt("timeout", RecoverySeverity.BACKOFF_RECOVERABLE, False, 10)
        metrics.record_attempt("timeout", RecoverySeverity.BACKOFF_RECOVERABLE, True, 15)

        # Test success rate
        success_rate = metrics.get_success_rate()
        expected_rate = 75.0  # 3 out of 4 successes
        if success_rate == expected_rate:
            print(f"✓ Success rate: {success_rate}%")
            self.passed += 1
        else:
            print(f"✗ Success rate: got {success_rate}%, expected {expected_rate}%")
            self.failed += 1
            self.errors.append("Success rate calculation mismatch")

        # Test MTTR
        mttr = metrics.calculate_mttr_seconds()
        expected_mttr = (5 + 5 + 10 + 15) / 4  # 8.75 seconds
        if abs(mttr - expected_mttr) < 0.01:
            print(f"✓ MTTR: {mttr:.2f}s")
            self.passed += 1
        else:
            print(f"✗ MTTR: got {mttr}s, expected {expected_mttr}s")
            self.failed += 1
            self.errors.append("MTTR calculation mismatch")

    def test_health_score(self):
        """Test CI health score calculation."""
        print("\n=== Testing Health Score ===")
        collector = TelemetryCollector()

        # Mock some recovery attempts
        attempts = [
            {
                "pattern_id": "net-conn",
                "severity": "auto_recoverable",
                "success": True,
                "delay_sec": 5,
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
            }
            for i in range(20)
        ]
        attempts.extend(
            [
                {
                    "pattern_id": "timeout",
                    "severity": "backoff_recoverable",
                    "success": False,
                    "delay_sec": 30,
                    "timestamp": (
                        datetime.utcnow() - timedelta(hours=i)
                    ).isoformat(),
                }
                for i in range(5)
            ]
        )

        # Calculate health for 85% recovery rate and 10s MTTR
        health = collector._calculate_health_score(85.0, 10.0)

        # Check score is in valid range
        if 0 <= health["score"] <= 100:
            print(f"✓ Health score: {health['score']}/100 ({health['status']})")
            self.passed += 1
        else:
            print(
                f"✗ Health score out of range: {health['score']}"
            )
            self.failed += 1
            self.errors.append("Health score out of range")

        # Check status assignment
        if health["status"] in ["excellent", "good", "fair", "poor"]:
            print(f"✓ Health status: {health['status']}")
            self.passed += 1
        else:
            print(f"✗ Invalid health status: {health['status']}")
            self.failed += 1
            self.errors.append("Invalid health status")

    def test_aais_reliability_delta(self):
        """Test AAIS Reliability score delta estimation."""
        print("\n=== Testing AAIS Reliability Delta ===")
        collector = TelemetryCollector()

        # Test case 1: High recovery rate, low MTTR
        delta1 = collector._estimate_reliability_delta(
            {
                "summary": {
                    "overall_recovery_rate_pct": 90,
                    "overall_mttr_seconds": 20,
                }
            }
        )
        if 5 <= delta1 <= 7:  # Should be close to max
            print(f"✓ High recovery + low MTTR: +{delta1:.1f} points")
            self.passed += 1
        else:
            print(f"✗ High recovery delta: got +{delta1:.1f}, expected 5-7")
            self.failed += 1
            self.errors.append("AAIS delta out of expected range")

        # Test case 2: Low recovery rate, high MTTR
        delta2 = collector._estimate_reliability_delta(
            {
                "summary": {
                    "overall_recovery_rate_pct": 50,
                    "overall_mttr_seconds": 200,
                }
            }
        )
        if 0 <= delta2 <= 2:  # Should be minimal
            print(f"✓ Low recovery + high MTTR: +{delta2:.1f} points")
            self.passed += 1
        else:
            print(f"✗ Low recovery delta: got +{delta2:.1f}, expected 0-2")
            self.failed += 1
            self.errors.append("AAIS delta calculation incorrect")

    def test_recovery_action_mapping(self):
        """Test severity to recovery action mapping."""
        print("\n=== Testing Recovery Action Mapping ===")

        actions = {
            RecoverySeverity.AUTO_RECOVERABLE: {
                "max_retries": 3,
                "base_delay_sec": 5,
                "action": "retry_immediately",
            },
            RecoverySeverity.BACKOFF_RECOVERABLE: {
                "max_retries": 3,
                "base_delay_sec": 10,
                "action": "retry_with_backoff",
            },
            RecoverySeverity.ESCALATE_REQUIRED: {
                "max_retries": 1,
                "base_delay_sec": 0,
                "action": "escalate_to_human",
            },
        }

        for severity, expected_action in actions.items():
            action = ErrorClassifier.severity_to_recovery_action(severity)
            if (
                action["max_retries"] == expected_action["max_retries"]
                and action["action"] == expected_action["action"]
            ):
                print(
                    f"✓ {severity.value}: {action['action']} (max {action['max_retries']} retries)"
                )
                self.passed += 1
            else:
                print(f"✗ Incorrect action mapping for {severity.value}")
                self.failed += 1
                self.errors.append(f"Action mapping incorrect for {severity.value}")

    def run_all_tests(self):
        """Run all test suites."""
        print("╔════════════════════════════════════════════════════════╗")
        print("║  Self-Healing CI Infrastructure - Integration Tests   ║")
        print("╚════════════════════════════════════════════════════════╝")

        self.test_error_classification()
        self.test_recovery_severity()
        self.test_exponential_backoff()
        self.test_recovery_metrics()
        self.test_health_score()
        self.test_aais_reliability_delta()
        self.test_recovery_action_mapping()

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total else 0
        print(f"Pass Rate: {pass_rate:.1f}%")

        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")

        print("=" * 60 + "\n")

        return self.failed == 0


if __name__ == "__main__":
    suite = TestSuite()
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)
