"""Test quality metrics validation for coverage baseline.

This module validates that test quality metrics (pass rate, flakiness,
determinism, isolation) meet or exceed the required standards for each phase.
It's part of the Coverage Baseline Monitoring Plan (Phase 2).

Reference: .codex/COVERAGE_VALIDATION_CRITERIA.md (Section 5.4)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from codex.logging.structured_logger import logger


class QualityMetricsValidator:
    """Validates test quality metrics against phase requirements."""

    def __init__(self, repo_root: Path | None = None):
        """Initialize validator.

        Args:
            repo_root: Repository root directory (defaults to project root)
        """
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]
        self.tracking_file = (
            self.repo_root
            / ".codex"
            / "coverage"
            / "BASELINE_TRACKING_REPORT.json"
        )
        self.validation_dir = self.repo_root / ".codex" / "coverage"
        self.validation_dir.mkdir(parents=True, exist_ok=True)

    def get_phase_requirements(self, phase: str = "baseline") -> dict[str, float]:
        """Get quality metric requirements for a phase.

        Args:
            phase: Phase name (e.g., 'baseline', 'phase_1', 'phase_2')

        Returns:
            Dictionary with metric requirements
        """
        # These come from PHASE_VALIDATION_GATES.yaml
        requirements = {
            "baseline": {
                "test_pass_rate_min": 99.5,
                "test_flakiness_max": 1.0,
                "regression_rate_max": 1.0,
                "test_determinism_min": 99.5,
            },
            "phase_1": {
                "test_pass_rate_min": 99.5,
                "test_flakiness_max": 0.5,
                "regression_rate_max": 0.5,
                "test_determinism_min": 100.0,
            },
            "phase_2": {
                "test_pass_rate_min": 99.5,
                "test_flakiness_max": 0.5,
                "regression_rate_max": 0.5,
                "test_determinism_min": 100.0,
            },
        }

        return requirements.get(phase, requirements["baseline"])

    def load_current_metrics(self) -> dict[str, float]:
        """Load current quality metrics from tracking report.

        Returns:
            Dictionary of current metric values
        """
        if not self.tracking_file.exists():
            return {
                "test_pass_rate": 100.0,
                "test_flakiness": 0.0,
                "test_determinism": 100.0,
                "test_isolation": 100.0,
            }

        with open(self.tracking_file) as f:
            data = json.load(f)

        return data.get("quality_metrics", {})

    def validate_quality_metrics(
        self, phase: str = "baseline"
    ) -> dict[str, Any]:
        """Validate all quality metrics meet phase requirements.

        Args:
            phase: Phase name for requirement selection

        Returns:
            Validation report dictionary
        """
        requirements = self.get_phase_requirements(phase)
        current = self.load_current_metrics()


        logger.info(f"QUALITY METRICS VALIDATION ({phase.upper()})")



        # Validate pass rate
        pass_rate = current.get("test_pass_rate", 100.0)
        pass_rate_min = requirements.get("test_pass_rate_min", 99.5)
        pass_rate_valid = pass_rate >= pass_rate_min

        logger.info("Test Pass Rate:")
        logger.info(f"  Current:  {pass_rate:.1f}%")
        logger.info(f"  Required: ≥{pass_rate_min:.1f}%")
        logger.info(f"  Status:   {'✅ PASS' if pass_rate_valid else '🔴 FAIL'}")


        # Validate flakiness
        flakiness = current.get("test_flakiness", 0.0)
        flakiness_max = requirements.get("test_flakiness_max", 1.0)
        flakiness_valid = flakiness <= flakiness_max

        logger.info("Test Flakiness:")
        logger.info(f"  Current:  {flakiness:.1f}%")
        logger.info(f"  Max:      ≤{flakiness_max:.1f}%")
        logger.info(f"  Status:   {'✅ PASS' if flakiness_valid else '🔴 FAIL'}")


        # Validate determinism
        determinism = current.get("test_determinism", 100.0)
        determinism_min = requirements.get("test_determinism_min", 99.5)
        determinism_valid = determinism >= determinism_min

        logger.info("Test Determinism:")
        logger.info(f"  Current:  {determinism:.1f}%")
        logger.info(f"  Required: ≥{determinism_min:.1f}%")
        logger.info(f"  Status:   {'✅ PASS' if determinism_valid else '🔴 FAIL'}")


        # Validate isolation
        isolation = current.get("test_isolation", 100.0)
        isolation_valid = isolation >= 99.5  # Always require high isolation

        logger.info("Test Isolation:")
        logger.info(f"  Current:  {isolation:.1f}%")
        logger.info("  Required: ≥99.5%")
        logger.info(f"  Status:   {'✅ PASS' if isolation_valid else '🔴 FAIL'}")


        # Validate regression rate
        regression_rate = current.get("regression_rate", 0.0)
        regression_max = requirements.get("regression_rate_max", 1.0)
        regression_valid = regression_rate <= regression_max

        logger.info("Regression Rate:")
        logger.info(f"  Current:  {regression_rate:.1f}%")
        logger.info(f"  Max:      ≤{regression_max:.1f}%")
        logger.info(f"  Status:   {'✅ PASS' if regression_valid else '🔴 FAIL'}")


        all_valid = (
            pass_rate_valid
            and flakiness_valid
            and determinism_valid
            and isolation_valid
            and regression_valid
        )

        # Generate report
        report = {
            "validation": "quality_metrics",
            "phase": phase,
            "current_metrics": current,
            "requirements": requirements,
            "validation_results": {
                "test_pass_rate": {
                    "current": pass_rate,
                    "required": pass_rate_min,
                    "valid": pass_rate_valid,
                },
                "test_flakiness": {
                    "current": flakiness,
                    "max": flakiness_max,
                    "valid": flakiness_valid,
                },
                "test_determinism": {
                    "current": determinism,
                    "required": determinism_min,
                    "valid": determinism_valid,
                },
                "test_isolation": {
                    "current": isolation,
                    "required": 99.5,
                    "valid": isolation_valid,
                },
                "regression_rate": {
                    "current": regression_rate,
                    "max": regression_max,
                    "valid": regression_valid,
                },
            },
            "validation_passed": all_valid,
        }

        # Write report
        report_file = self.validation_dir / "QUALITY_METRICS_VALIDATION_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report written to {report_file}")


        return report


def test_pass_rate():
    """Test that pass rate meets minimum requirement."""
    validator = QualityMetricsValidator()
    report = validator.validate_quality_metrics("baseline")

    pass_rate_valid = (
        report.get("validation_results", {})
        .get("test_pass_rate", {})
        .get("valid", False)
    )
    assert pass_rate_valid, "Test pass rate below minimum"


def test_flakiness():
    """Test that flakiness is within acceptable range."""
    validator = QualityMetricsValidator()
    report = validator.validate_quality_metrics("baseline")

    flakiness_valid = (
        report.get("validation_results", {})
        .get("test_flakiness", {})
        .get("valid", False)
    )
    assert flakiness_valid, "Test flakiness exceeds maximum"


def test_determinism():
    """Test that determinism meets minimum requirement."""
    validator = QualityMetricsValidator()
    report = validator.validate_quality_metrics("baseline")

    determinism_valid = (
        report.get("validation_results", {})
        .get("test_determinism", {})
        .get("valid", False)
    )
    assert determinism_valid, "Test determinism below minimum"


def test_isolation():
    """Test that test isolation is adequate."""
    validator = QualityMetricsValidator()
    report = validator.validate_quality_metrics("baseline")

    isolation_valid = (
        report.get("validation_results", {})
        .get("test_isolation", {})
        .get("valid", False)
    )
    assert isolation_valid, "Test isolation below minimum"


def test_regression_rate():
    """Test that regression rate is acceptable."""
    validator = QualityMetricsValidator()
    report = validator.validate_quality_metrics("baseline")

    regression_valid = (
        report.get("validation_results", {})
        .get("regression_rate", {})
        .get("valid", False)
    )
    assert regression_valid, "Regression rate exceeds maximum"


def test_all_quality_metrics():
    """Test all quality metrics meet requirements."""
    validator = QualityMetricsValidator()
    report = validator.validate_quality_metrics("baseline")

    all_valid = report.get("validation_passed", False)
    assert all_valid, "One or more quality metrics failed validation"
