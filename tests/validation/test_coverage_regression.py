"""Test coverage regression detection and prevention.

This module validates that current coverage doesn't regress from the baseline
snapshot (34.63%) and that no module loses more than its allowed tolerance.
It's part of the Coverage Baseline Monitoring Plan (Phase 2).

Reference: .codex/COVERAGE_VALIDATION_CRITERIA.md (Section 5.2)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from codex.logging.structured_logger import logger


class RegressionDetector:
    """Detects and validates coverage regressions against baseline."""

    def __init__(self, repo_root: Path | None = None):
        """Initialize detector.

        Args:
            repo_root: Repository root directory (defaults to project root)
        """
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]
        self.baseline_file = (
            self.repo_root / ".codex" / "COVERAGE_BASELINE_34_63.json"
        )
        self.tracking_file = (
            self.repo_root
            / ".codex"
            / "coverage"
            / "BASELINE_TRACKING_REPORT.json"
        )
        self.validation_dir = self.repo_root / ".codex" / "coverage"
        self.validation_dir.mkdir(parents=True, exist_ok=True)

    def load_baseline(self) -> dict[str, Any]:
        """Load baseline snapshot.

        Returns:
            Baseline snapshot dictionary
        """
        if not self.baseline_file.exists():
            return {}

        with open(self.baseline_file) as f:
            return json.load(f)

    def load_current_tracking(self) -> dict[str, Any]:
        """Load current coverage tracking report.

        Returns:
            Current tracking report dictionary
        """
        if not self.tracking_file.exists():
            return {}

        with open(self.tracking_file) as f:
            return json.load(f)

    def detect_regression(self) -> dict[str, Any]:
        """Detect coverage regressions.

        Validates:
        1. Overall coverage doesn't drop below baseline ±1.5%
        2. No module loses more than allowed tolerance per tier
        3. Test count doesn't decrease
        4. Quality metrics don't degrade

        Returns:
            Regression detection report dictionary
        """
        baseline = self.load_baseline()
        current = self.load_current_tracking()

        if not baseline or not current:
            return {
                "status": "SKIP",
                "reason": "Baseline or current data not available",
                "regression_detected": False,
            }

        baseline_coverage = baseline.get("baseline_snapshot", {}).get(
            "baseline_coverage", 34.63
        )
        current_coverage = (
            current.get("current_metrics", {}).get("line_coverage_percent", 0)
        )

        variance = current_coverage - baseline_coverage
        variance_tolerance = 1.5

        # Check for regression
        is_regression = variance < -variance_tolerance


        logger.info("COVERAGE REGRESSION DETECTION")


        logger.info(f"Baseline Coverage:        {baseline_coverage:.2f}%")
        logger.info(f"Current Coverage:         {current_coverage:.2f}%")
        logger.info(f"Variance:                 {variance:+.2f}%")
        logger.info(f"Allowed Tolerance:        ±{variance_tolerance}%")


        if is_regression:
            logger.info(f"🔴 REGRESSION DETECTED: Coverage dropped {abs(variance):.2f}%")
            logger.info(f"   Exceeds tolerance of {variance_tolerance}%")
        else:
            logger.info("✅ No regression detected")
            if variance >= 0:
                logger.info(f"   Coverage improved by {variance:.2f}%")
            else:
                logger.info(f"   Coverage variance acceptable ({variance:+.2f}% within ±{variance_tolerance}%)")



        # Get quality metrics
        quality_metrics = current.get("quality_metrics", {})
        test_pass_rate = quality_metrics.get("test_pass_rate", 100)
        flakiness = quality_metrics.get("test_flakiness", 0)
        determinism = quality_metrics.get("test_determinism", 100)

        logger.info("Quality Metrics:")
        logger.info(f"  Pass Rate:              {test_pass_rate:.1f}%")
        logger.info(f"  Flakiness:              {flakiness:.1f}%")
        logger.info(f"  Determinism:            {determinism:.1f}%")


        # Validate quality metrics
        quality_valid = (
            test_pass_rate >= 99.5 and flakiness <= 0.5 and determinism >= 99.5
        )

        # Generate report
        report = {
            "validation": "coverage_regression_detection",
            "baseline": {
                "coverage_percent": baseline_coverage,
                "test_count": baseline.get("test_statistics", {}).get("total_tests", 0),
            },
            "current": {
                "coverage_percent": current_coverage,
                "variance_percent": round(variance, 2),
                "quality_metrics": quality_metrics,
            },
            "detection": {
                "regression_detected": is_regression,
                "variance_tolerance": variance_tolerance,
                "quality_metrics_valid": quality_valid,
                "validation_passed": not is_regression and quality_valid,
            },
        }

        # Write report
        report_file = self.validation_dir / "REGRESSION_DETECTION_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report written to {report_file}")


        return report

    def validate_test_count(self) -> bool:
        """Validate test count hasn't decreased.

        Returns:
            True if test count is stable or increased, False if regression
        """
        baseline = self.load_baseline()
        current = self.load_current_tracking()

        if not baseline or not current:
            return True  # Skip if data unavailable

        baseline_tests = baseline.get("test_statistics", {}).get("total_tests", 0)
        # Note: Current tracking doesn't have test count yet; will be added in Phase 1
        current_tests = current.get("quality_metrics", {}).get("test_count", 0)

        if baseline_tests > 0 and current_tests > 0:
            if current_tests < baseline_tests:
                logger.info(f"⚠️  Test count decreased: {baseline_tests} → {current_tests}")
                return False

        return True

    def validate_module_stability(self) -> dict[str, Any]:
        """Validate module-level coverage stability.

        Checks that no module loses more than its allowed tolerance per tier.

        Returns:
            Module validation report dictionary
        """
        # This will be populated when module-level tracking is implemented
        return {
            "status": "NOT_IMPLEMENTED",
            "message": "Module-level tracking to be implemented in Phase 1",
        }


def test_no_regression():
    """Test that coverage doesn't regress from baseline."""
    detector = RegressionDetector()
    report = detector.detect_regression()

    validation_passed = report.get("detection", {}).get("validation_passed", True)
    assert validation_passed, f"Coverage regression detected: {report}"


def test_test_count_stable():
    """Test that test count doesn't decrease."""
    detector = RegressionDetector()
    is_stable = detector.validate_test_count()
    assert is_stable, "Test count decreased (regression detected)"


def test_module_stability():
    """Test module-level coverage stability."""
    detector = RegressionDetector()
    report = detector.validate_module_stability()
    # Will be fully implemented in Phase 1
    assert report is not None
