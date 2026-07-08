"""Test coverage determinism and stability.

This module verifies that test suite behavior is deterministic and that
coverage measurements are stable across repeated test runs. It's part of the
Coverage Baseline Monitoring Plan (Phase 2).

Reference: .codex/COVERAGE_VALIDATION_CRITERIA.md (Section 5.1)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from codex.logging.structured_logger import logger


class DeterminismValidator:
    """Validates test suite determinism across multiple runs."""

    def __init__(self, repo_root: Path | None = None):
        """Initialize validator.

        Args:
            repo_root: Repository root directory (defaults to project root)
        """
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]
        self.validation_dir = self.repo_root / ".codex" / "coverage"
        self.validation_dir.mkdir(parents=True, exist_ok=True)

    def run_test_suite(self, run_number: int) -> dict[str, Any]:
        """Run full test suite and capture metrics.

        Args:
            run_number: Run sequence number (1, 2, 3)

        Returns:
            Dictionary with test metrics for this run
        """
        try:
            # Run pytest with coverage
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "--cov=src",
                "--cov-report=json",
                "--cov-report=term-missing",
                "-v",
                "--tb=short",
                "-x",
            ]

            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=3600,
            )

            # Parse coverage report
            coverage_file = self.repo_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    total_coverage = coverage_data.get("totals", {}).get(
                        "percent_covered", 0
                    )
            else:
                total_coverage = 0

            return {
                "run_number": run_number,
                "exit_code": result.returncode,
                "total_coverage": total_coverage,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "test_count": self._count_tests(result.stdout),
            }

        except subprocess.TimeoutExpired:
            return {
                "run_number": run_number,
                "exit_code": -1,
                "error": "Test suite timeout (>3600s)",
                "total_coverage": 0,
                "test_count": 0,
            }

    def _count_tests(self, output: str) -> int:
        """Extract test count from pytest output.

        Args:
            output: Pytest output string

        Returns:
            Number of tests passed
        """
        # Look for "N passed" pattern
        import re

        match = re.search(r"(\d+) passed", output)
        return int(match.group(1)) if match else 0

    def validate_determinism(self) -> bool:
        """Run test suite 3 times and validate determinism.

        Success criteria:
        - All 3 runs pass (exit_code == 0)
        - Coverage variance < 0.1%
        - Test count identical across runs
        - No new failures in any run

        Returns:
            True if determinism validated, False otherwise
        """

        logger.info("COVERAGE DETERMINISM VALIDATION")



        runs = []
        for run_num in range(1, 4):
            logger.info(f"Run {run_num}/3: Executing test suite...")
            result = self.run_test_suite(run_num)
            runs.append(result)

            exit_code = result.get("exit_code", -1)
            coverage = result.get("total_coverage", 0)
            test_count = result.get("test_count", 0)

            logger.info(f"  Exit Code: {exit_code}")
            logger.info(f"  Coverage: {coverage:.2f}%")
            logger.info(f"  Tests: {test_count}")


        # Validate consistency
        logger.info("Validating determinism across runs...")


        all_passed = all(r.get("exit_code") == 0 for r in runs)
        coverages = [r.get("total_coverage", 0) for r in runs]
        test_counts = [r.get("test_count", 0) for r in runs]

        coverage_variance = max(coverages) - min(coverages)
        all_coverage_match = coverage_variance < 0.1
        all_tests_match = all(tc == test_counts[0] for tc in test_counts)

        logger.info(f"✓ All runs passed: {all_passed}")
        logger.info(f"✓ Coverage variance < 0.1%: {all_coverage_match} (variance: {coverage_variance:.3f}%)")
        logger.info(f"✓ Test count consistent: {all_tests_match} (counts: {test_counts})")


        # Generate report
        report = {
            "validation": "test_coverage_determinism",
            "runs": runs,
            "summary": {
                "all_passed": all_passed,
                "coverage_variance": round(coverage_variance, 3),
                "coverage_variance_acceptable": all_coverage_match,
                "test_count_consistent": all_tests_match,
                "determinism_validated": all_passed
                and all_coverage_match
                and all_tests_match,
            },
        }

        # Write report
        report_file = self.validation_dir / "DETERMINISM_VALIDATION_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report written to {report_file}")


        return report["summary"]["determinism_validated"]


def test_determinism_validation():
    """Test coverage determinism (main validation function)."""
    validator = DeterminismValidator()
    is_valid = validator.validate_determinism()

    assert is_valid, "Coverage determinism validation failed"


if __name__ == "__main__":
    validator = DeterminismValidator()
    success = validator.validate_determinism()
    sys.exit(0 if success else 1)
