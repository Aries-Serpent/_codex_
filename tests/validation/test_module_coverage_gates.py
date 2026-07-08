"""Test module-level coverage gates and tier minimums.

This module validates that each module/tier maintains its minimum coverage
threshold and that no module regresses below its tier baseline. It's part of
the Coverage Baseline Monitoring Plan (Phase 2).

Reference: .codex/COVERAGE_VALIDATION_CRITERIA.md (Section 5.3)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from codex.logging.structured_logger import logger


class ModuleCoverageGates:
    """Validates module-level coverage against tier-specific gates."""

    def __init__(self, repo_root: Path | None = None):
        """Initialize gates validator.

        Args:
            repo_root: Repository root directory (defaults to project root)
        """
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]
        self.module_matrix_file = (
            self.repo_root / ".codex" / "coverage" / "MODULE_BASELINE_MATRIX.json"
        )
        self.validation_dir = self.repo_root / ".codex" / "coverage"
        self.validation_dir.mkdir(parents=True, exist_ok=True)

    def load_module_matrix(self) -> dict[str, Any]:
        """Load module baseline matrix.

        Returns:
            Module matrix dictionary
        """
        if not self.module_matrix_file.exists():
            return {}

        with open(self.module_matrix_file) as f:
            return json.load(f)

    def get_tier_minimums(self, phase: str = "baseline") -> dict[str, float]:
        """Get tier-level minimum coverage requirements.

        Args:
            phase: Phase name (e.g., 'baseline', 'phase_1', 'phase_2')

        Returns:
            Dictionary mapping tier names to minimum percentages
        """
        # These come from PHASE_VALIDATION_GATES.yaml
        phase_gates = {
            "baseline": {
                "tier_1": 90.0,
                "tier_2": 85.0,
                "tier_3": 77.0,
                "tier_4": 62.0,
            },
            "phase_1": {
                "tier_1": 92.0,
                "tier_2": 85.0,
                "tier_3": 77.0,
                "tier_4": 70.0,
            },
            "phase_2": {
                "tier_1": 92.0,
                "tier_2": 85.0,
                "tier_3": 80.0,
                "tier_4": 75.0,
            },
        }

        return phase_gates.get(phase, phase_gates["baseline"])

    def validate_tier_gates(
        self, phase: str = "baseline"
    ) -> dict[str, Any]:
        """Validate all modules meet their tier minimums.

        Args:
            phase: Phase name for gate selection

        Returns:
            Validation report dictionary
        """
        matrix = self.load_module_matrix()
        if not matrix:
            return {
                "status": "SKIP",
                "reason": "Module matrix not available",
                "validation_passed": True,
            }

        minimums = self.get_tier_minimums(phase)


        logger.info(f"MODULE COVERAGE GATES VALIDATION ({phase.upper()})")



        # Validate Tier 1
        logger.info("Tier 1: Security & Authentication")
        tier_1_data = matrix.get("tier_1_security_authentication", {})
        tier_1_modules = tier_1_data.get("modules", [])
        tier_1_min = minimums.get("tier_1", 90.0)
        tier_1_valid = self._validate_tier(tier_1_modules, tier_1_min)



        # Validate Tier 2
        logger.info("Tier 2: Authentication Systems")
        tier_2_data = matrix.get("tier_2_auth_systems", {})
        tier_2_modules = tier_2_data.get("modules", [])
        tier_2_min = minimums.get("tier_2", 85.0)
        tier_2_valid = self._validate_tier(tier_2_modules, tier_2_min)



        # Validate Tier 3
        logger.info("Tier 3: Infrastructure & CLI")
        tier_3_data = matrix.get("tier_3_infrastructure_cli", {})
        tier_3_modules = tier_3_data.get("modules", [])
        tier_3_min = minimums.get("tier_3", 77.0)
        tier_3_valid = self._validate_tier(tier_3_modules, tier_3_min)



        # Validate Tier 4
        logger.info("Tier 4: Extended Coverage")
        tier_4_data = matrix.get("tier_4_extended_coverage", {})
        tier_4_groups = tier_4_data.get("module_groups", [])
        tier_4_min = minimums.get("tier_4", 62.0)
        tier_4_valid = self._validate_tier(tier_4_groups, tier_4_min)



        all_valid = tier_1_valid and tier_2_valid and tier_3_valid and tier_4_valid

        # Generate report
        report = {
            "validation": "module_coverage_gates",
            "phase": phase,
            "minimums": minimums,
            "tier_results": {
                "tier_1": {"minimum": tier_1_min, "valid": tier_1_valid},
                "tier_2": {"minimum": tier_2_min, "valid": tier_2_valid},
                "tier_3": {"minimum": tier_3_min, "valid": tier_3_valid},
                "tier_4": {"minimum": tier_4_min, "valid": tier_4_valid},
            },
            "validation_passed": all_valid,
        }

        # Write report
        report_file = self.validation_dir / "MODULE_COVERAGE_VALIDATION_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report written to {report_file}")


        return report

    def _validate_tier(
        self, modules: list[dict[str, Any]], minimum: float
    ) -> bool:
        """Validate a single tier's modules against minimum.

        Args:
            modules: List of module dictionaries with 'coverage_percent' key
            minimum: Minimum required coverage percentage

        Returns:
            True if all modules meet minimum, False otherwise
        """
        violations = []
        for module in modules:
            coverage = module.get("coverage_percent", 0)
            module_name = module.get("module") or module.get("group", "unknown")

            if coverage < minimum:
                violations.append((module_name, coverage))
            else:
                logger.info(f"  ✅ {module_name}: {coverage:.1f}% >= {minimum:.1f}%")

        if violations:
            for name, coverage in violations:
                print(
                    f"  🔴 {name}: {coverage:.1f}% < {minimum:.1f}% VIOLATION"
                )
            return False

        return True


def test_tier_1_minimum():
    """Test Tier 1 (Security) meets minimum coverage."""
    gates = ModuleCoverageGates()
    report = gates.validate_tier_gates("baseline")

    tier_1_valid = report.get("tier_results", {}).get("tier_1", {}).get("valid", False)
    assert tier_1_valid, "Tier 1 coverage below minimum"


def test_tier_2_minimum():
    """Test Tier 2 (Auth) meets minimum coverage."""
    gates = ModuleCoverageGates()
    report = gates.validate_tier_gates("baseline")

    tier_2_valid = report.get("tier_results", {}).get("tier_2", {}).get("valid", False)
    assert tier_2_valid, "Tier 2 coverage below minimum"


def test_tier_3_minimum():
    """Test Tier 3 (Infrastructure) meets minimum coverage."""
    gates = ModuleCoverageGates()
    report = gates.validate_tier_gates("baseline")

    tier_3_valid = report.get("tier_results", {}).get("tier_3", {}).get("valid", False)
    assert tier_3_valid, "Tier 3 coverage below minimum"


def test_tier_4_minimum():
    """Test Tier 4 (Extended) meets minimum coverage."""
    gates = ModuleCoverageGates()
    report = gates.validate_tier_gates("baseline")

    tier_4_valid = report.get("tier_results", {}).get("tier_4", {}).get("valid", False)
    assert tier_4_valid, "Tier 4 coverage below minimum"


def test_all_gates_pass():
    """Test all tier gates pass validation."""
    gates = ModuleCoverageGates()
    report = gates.validate_tier_gates("baseline")

    all_valid = report.get("validation_passed", False)
    assert all_valid, "One or more tier gates failed validation"
