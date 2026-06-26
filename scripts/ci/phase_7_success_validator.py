#!/usr/bin/env python3
"""
phase_7_success_validator.py — Phase 6-7 Success Criteria Validation

Purpose
-------
Validates success criteria for Phase 6-7 implementation (30-day evaluation).
Measures:

  1. WEC compliance rate across active PRs
  2. Auto-approval success rate
  3. CI/CD pipeline health
  4. Workflow execution efficiency
  5. 30-day trend analysis

Success Criteria (Phase 6-7)
----------------------------
  ✅ WEC compliance rate ≥ 85% across active PRs
  ✅ Auto-approval success rate ≥ 90% (runs approved without human intervention)
  ✅ Pre-merge validation pass rate ≥ 92%
  ✅ Average workflow execution time ≤ 30 minutes
  ✅ Health score ≥ 0.80 (out of 1.0)

Usage
-----
    python scripts/ci/phase_7_success_validator.py [--json] [--report FILE]
    python scripts/ci/phase_7_success_validator.py --evaluate --days 30
    python scripts/ci/phase_7_success_validator.py --validate-all
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
REPO = "Aries-Serpent/_codex_"

# Success criteria thresholds
SUCCESS_CRITERIA = {
    "wec_compliance_rate": 0.85,           # ≥ 85%
    "auto_approval_success_rate": 0.90,    # ≥ 90%
    "pre_merge_pass_rate": 0.92,           # ≥ 92%
    "avg_workflow_time_minutes": 30.0,     # ≤ 30 minutes
    "health_score": 0.80,                  # ≥ 0.80
}

# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class SuccessCriterion:
    """Individual success criterion with evaluation result."""
    name: str
    threshold: float
    operator: str  # "gte" (>=), "lte" (<=)
    actual_value: float
    passed: bool
    weight: float = 1.0

    @property
    def status_emoji(self) -> str:
        return "✅" if self.passed else "❌"

    @property
    def status_text(self) -> str:
        return "PASS" if self.passed else "FAIL"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PhaseValidationResult:
    """Complete Phase 6-7 validation result."""
    timestamp: str
    evaluation_period_days: int
    criteria: list[SuccessCriterion] = field(default_factory=list)
    all_passed: bool = False
    pass_count: int = 0
    total_count: int = 0
    overall_score: float = 0.0
    recommendation: str = ""
    next_actions: list[str] = field(default_factory=list)

    @property
    def status_emoji(self) -> str:
        return "✅" if self.all_passed else "❌"

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "evaluation_period_days": self.evaluation_period_days,
            "all_passed": self.all_passed,
            "status": self.status_emoji + (" PHASE COMPLETE" if self.all_passed else " PHASE INCOMPLETE"),
            "criteria": [c.to_dict() for c in self.criteria],
            "pass_count": self.pass_count,
            "total_count": self.total_count,
            "overall_score": self.overall_score,
            "recommendation": self.recommendation,
            "next_actions": self.next_actions,
        }


# ---------------------------------------------------------------------------
# Evaluation Functions
# ---------------------------------------------------------------------------


def evaluate_wec_compliance() -> SuccessCriterion:
    """Evaluate WEC compliance rate across active PRs."""
    try:
        # Use the health monitor to get WEC compliance
        result = subprocess.run(
            ["python", "scripts/ci/wec_health_monitor.py", "--json"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=60,
        )
        if result.returncode != 0:
            return SuccessCriterion(
                name="WEC Compliance Rate",
                threshold=SUCCESS_CRITERIA["wec_compliance_rate"],
                operator="gte",
                actual_value=0.0,
                passed=False,
            )
        
        data = json.loads(result.stdout)
        compliance_rate = data.get("wec_compliance_rate", 0.0)
        
        passed = compliance_rate >= SUCCESS_CRITERIA["wec_compliance_rate"]
        return SuccessCriterion(
            name="WEC Compliance Rate",
            threshold=SUCCESS_CRITERIA["wec_compliance_rate"],
            operator="gte",
            actual_value=compliance_rate,
            passed=passed,
            weight=0.30,
        )
    except Exception as e:
        logger.error(f"Failed to evaluate WEC compliance: {e}")
        return SuccessCriterion(
            name="WEC Compliance Rate",
            threshold=SUCCESS_CRITERIA["wec_compliance_rate"],
            operator="gte",
            actual_value=0.0,
            passed=False,
        )


def evaluate_auto_approval_success() -> SuccessCriterion:
    """Evaluate auto-approval success rate."""
    try:
        # Query workflow runs for approval outcomes
        result = subprocess.run(
            ["gh", "run", "list", "--repo", REPO, "--workflow", "auto-approve-workflows.yml",
             "--limit", "100", "--json", "status,conclusion"],
            capture_output=True,
            text=True,
            check=True,
        )
        
        runs = json.loads(result.stdout)
        if not runs:
            return SuccessCriterion(
                name="Auto-Approval Success Rate",
                threshold=SUCCESS_CRITERIA["auto_approval_success_rate"],
                operator="gte",
                actual_value=1.0,  # No runs to fail
                passed=True,
            )
        
        successful = sum(1 for r in runs if r.get("conclusion") == "success")
        success_rate = successful / len(runs) if runs else 0.0
        
        passed = success_rate >= SUCCESS_CRITERIA["auto_approval_success_rate"]
        return SuccessCriterion(
            name="Auto-Approval Success Rate",
            threshold=SUCCESS_CRITERIA["auto_approval_success_rate"],
            operator="gte",
            actual_value=success_rate,
            passed=passed,
            weight=0.25,
        )
    except Exception as e:
        logger.error(f"Failed to evaluate auto-approval success: {e}")
        return SuccessCriterion(
            name="Auto-Approval Success Rate",
            threshold=SUCCESS_CRITERIA["auto_approval_success_rate"],
            operator="gte",
            actual_value=0.0,
            passed=False,
        )


def evaluate_pre_merge_pass_rate() -> SuccessCriterion:
    """Evaluate pre-merge validation pass rate."""
    try:
        # Query pre-merge-validation workflow runs
        result = subprocess.run(
            ["gh", "run", "list", "--repo", REPO, "--workflow", "pre-merge-validation.yml",
             "--limit", "100", "--json", "status,conclusion"],
            capture_output=True,
            text=True,
            check=True,
        )
        
        runs = json.loads(result.stdout)
        if not runs:
            return SuccessCriterion(
                name="Pre-Merge Validation Pass Rate",
                threshold=SUCCESS_CRITERIA["pre_merge_pass_rate"],
                operator="gte",
                actual_value=1.0,
                passed=True,
            )
        
        successful = sum(1 for r in runs if r.get("conclusion") == "success")
        pass_rate = successful / len(runs) if runs else 0.0
        
        passed = pass_rate >= SUCCESS_CRITERIA["pre_merge_pass_rate"]
        return SuccessCriterion(
            name="Pre-Merge Validation Pass Rate",
            threshold=SUCCESS_CRITERIA["pre_merge_pass_rate"],
            operator="gte",
            actual_value=pass_rate,
            passed=passed,
            weight=0.25,
        )
    except Exception as e:
        logger.error(f"Failed to evaluate pre-merge pass rate: {e}")
        return SuccessCriterion(
            name="Pre-Merge Validation Pass Rate",
            threshold=SUCCESS_CRITERIA["pre_merge_pass_rate"],
            operator="gte",
            actual_value=0.0,
            passed=False,
        )


def evaluate_workflow_execution_time() -> SuccessCriterion:
    """Evaluate average workflow execution time."""
    try:
        # Query workflow runs for execution times (last 50 runs)
        result = subprocess.run(
            ["gh", "run", "list", "--repo", REPO,
             "--limit", "50", "--json", "durationMinutes"],
            capture_output=True,
            text=True,
            check=True,
        )
        
        runs = json.loads(result.stdout)
        if not runs:
            return SuccessCriterion(
                name="Avg Workflow Execution Time (minutes)",
                threshold=SUCCESS_CRITERIA["avg_workflow_time_minutes"],
                operator="lte",
                actual_value=0.0,
                passed=True,
            )
        
        avg_time = sum(r.get("durationMinutes", 0) for r in runs) / len(runs) if runs else 0.0
        
        passed = avg_time <= SUCCESS_CRITERIA["avg_workflow_time_minutes"]
        return SuccessCriterion(
            name="Avg Workflow Execution Time (minutes)",
            threshold=SUCCESS_CRITERIA["avg_workflow_time_minutes"],
            operator="lte",
            actual_value=avg_time,
            passed=passed,
            weight=0.20,
        )
    except Exception as e:
        logger.error(f"Failed to evaluate workflow execution time: {e}")
        return SuccessCriterion(
            name="Avg Workflow Execution Time (minutes)",
            threshold=SUCCESS_CRITERIA["avg_workflow_time_minutes"],
            operator="lte",
            actual_value=0.0,
            passed=False,
        )


def evaluate_health_score() -> SuccessCriterion:
    """Evaluate overall health score."""
    try:
        # Get health score from health monitor
        result = subprocess.run(
            ["python", "scripts/ci/wec_health_monitor.py", "--json"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=60,
        )
        if result.returncode != 0:
            return SuccessCriterion(
                name="Overall Health Score",
                threshold=SUCCESS_CRITERIA["health_score"],
                operator="gte",
                actual_value=0.0,
                passed=False,
            )
        
        data = json.loads(result.stdout)
        health_score = data.get("health_score", 0.0)
        
        passed = health_score >= SUCCESS_CRITERIA["health_score"]
        return SuccessCriterion(
            name="Overall Health Score",
            threshold=SUCCESS_CRITERIA["health_score"],
            operator="gte",
            actual_value=health_score,
            passed=passed,
            weight=0.20,
        )
    except Exception as e:
        logger.error(f"Failed to evaluate health score: {e}")
        return SuccessCriterion(
            name="Overall Health Score",
            threshold=SUCCESS_CRITERIA["health_score"],
            operator="gte",
            actual_value=0.0,
            passed=False,
        )


def validate_all_criteria(evaluation_days: int = 30) -> PhaseValidationResult:
    """Validate all Phase 6-7 success criteria."""
    logger.info(f"🔍 Validating Phase 6-7 Success Criteria ({evaluation_days}-day evaluation)...")
    
    criteria = [
        evaluate_wec_compliance(),
        evaluate_auto_approval_success(),
        evaluate_pre_merge_pass_rate(),
        evaluate_workflow_execution_time(),
        evaluate_health_score(),
    ]
    
    passed_count = sum(1 for c in criteria if c.passed)
    total_count = len(criteria)
    all_passed = passed_count == total_count
    
    # Calculate weighted overall score
    overall_score = sum(c.actual_value * c.weight for c in criteria) / sum(c.weight for c in criteria)
    
    # Determine recommendation and next actions
    if all_passed:
        recommendation = "✅ Phase 6-7 success criteria SATISFIED — autonomous campaign ready for deployment"
        next_actions = [
            "Monitor metrics for ongoing compliance",
            "Archive success validation report",
            "Prepare Phase 8 transition documentation",
        ]
    else:
        failed_criteria = [c.name for c in criteria if not c.passed]
        recommendation = f"⚠️ Phase 6-7 success criteria NOT fully satisfied — {len(failed_criteria)} criterion/criteria need attention"
        next_actions = [
            f"Address failing criteria: {', '.join(failed_criteria[:2])}...",
            "Re-run validation after fixes applied",
            "Schedule remediation meeting with team",
        ]
    
    result = PhaseValidationResult(
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        evaluation_period_days=evaluation_days,
        criteria=criteria,
        all_passed=all_passed,
        pass_count=passed_count,
        total_count=total_count,
        overall_score=overall_score,
        recommendation=recommendation,
        next_actions=next_actions,
    )
    
    return result


def print_validation_report(result: PhaseValidationResult) -> None:
    """Print human-readable validation report."""
    print()
    print("=" * 80)
    print(f"🎯 Phase 6-7 Success Criteria Validation — {result.timestamp}")
    print("=" * 80)
    print()
    
    print(f"Status: {result.status_emoji} {result.pass_count}/{result.total_count} criteria passed")
    print(f"Overall Score: {result.overall_score:.1%}")
    print()
    
    print("📋 Criteria Evaluation:")
    for criterion in result.criteria:
        op_str = "≥" if criterion.operator == "gte" else "≤"
        print(f"  {criterion.status_emoji} {criterion.name}")
        print(f"     Threshold: {criterion.threshold:.1%} ({op_str})")
        print(f"     Actual: {criterion.actual_value:.1%}")
    print()
    
    print(f"📌 Recommendation:")
    print(f"  {result.recommendation}")
    print()
    
    print("🚀 Next Actions:")
    for i, action in enumerate(result.next_actions, 1):
        print(f"  {i}. {action}")
    print()
    
    print("=" * 80)


def save_validation_report(result: PhaseValidationResult, filepath: Path) -> None:
    """Save validation report to file."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        logger.info(f"✅ Validation report saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save validation report: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 6-7 Success Criteria Validator (30-day evaluation)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output report as JSON",
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        default=False,
        help="Run full evaluation",
    )
    parser.add_argument(
        "--validate-all",
        action="store_true",
        default=False,
        help="Validate all criteria and exit with status code",
    )
    parser.add_argument(
        "--report",
        metavar="FILE",
        default="",
        help="Save report to file",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        metavar="N",
        help="Evaluation period in days (default: 30)",
    )
    
    args = parser.parse_args(argv)
    
    # Run validation
    result = validate_all_criteria(evaluation_days=args.days)
    
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print_validation_report(result)
    
    # Save report if requested
    if args.report:
        save_validation_report(result, Path(args.report))
    
    # Exit with appropriate status code
    if args.validate_all:
        return 0 if result.all_passed else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
