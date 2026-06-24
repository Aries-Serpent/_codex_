#!/usr/bin/env python3
"""
Unified Compliance Check Orchestrator

Runs all 6 requirement validators in parallel/sequential order and generates a unified compliance report.

Design:
- REQ-1, REQ-2, REQ-3: Run in parallel (independent checks)
- REQ-4, REQ-5: Run sequentially (both check files in commits)
- REQ-6: Run async (post-merge, may take longer)

Total time: < 60 seconds
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# Import validators
sys.path.insert(0, str(Path(__file__).parent / "validators"))
from validators.base import ComplianceResult

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class ComplianceReport:
    """Unified compliance report for a PR."""

    pr_number: str
    overall_score: float  # 0-100
    status: str  # "APPROVE", "WARN", "BLOCK"
    generated_at: str
    validators: list[dict] = field(default_factory=list)
    decision_rationale: str = ""
    next_steps: list[str] = field(default_factory=list)
    elapsed_ms: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "pr_number": self.pr_number,
            "overall_score": self.overall_score,
            "status": self.status,
            "generated_at": self.generated_at,
            "validators": self.validators,
            "decision_rationale": self.decision_rationale,
            "next_steps": self.next_steps,
            "elapsed_ms": self.elapsed_ms,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class UnifiedComplianceCheck:
    """Orchestrates all requirement validators."""

    def __init__(self, pr_number: str, repo: str = "Aries-Serpent/_codex_"):
        self.pr_number = pr_number
        self.repo = repo
        self.start_time = time.time()

    def run(self, strict: bool = False, timeout: int = 60) -> ComplianceReport:
        """Run all validators and generate compliance report."""
        logger.info(f"Starting compliance check for PR #{self.pr_number}")

        # Import validators here to avoid circular imports
        from validators.req1_eligibility_validator import REQ1EligibilityValidator
        from validators.req2_compliance_validator import REQ2ComplianceValidator
        from validators.req3_merge_validator import REQ3MergeValidator
        from validators.req4_accountability_validator import REQ4AccountabilityValidator
        from validators.req5_changelog_validator import REQ5ChangelogValidator
        from validators.req6_postmerge_validator import REQ6PostMergeValidator

        results: dict[str, ComplianceResult] = {}

        # Run REQ-1/2/3 in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                "REQ-1": executor.submit(
                    lambda: REQ1EligibilityValidator(self.pr_number, self.repo).validate()
                ),
                "REQ-2": executor.submit(
                    lambda: REQ2ComplianceValidator(self.pr_number, self.repo).validate()
                ),
                "REQ-3": executor.submit(
                    lambda: REQ3MergeValidator(self.pr_number, self.repo).validate()
                ),
            }

            for req_id, future in futures.items():
                try:
                    results[req_id] = future.result(timeout=timeout // 3)
                except concurrent.futures.TimeoutError:
                    logger.error(f"{req_id} timed out")
                    results[req_id] = ComplianceResult(
                        requirement_id=req_id,
                        status="fail",
                        score=0.0,
                        reason="Validator timed out",
                        remediation=["Try again later", "Check GitHub API status"],
                    )
                except Exception as exc:
                    logger.error(f"{req_id} failed: {exc}")
                    results[req_id] = ComplianceResult(
                        requirement_id=req_id,
                        status="fail",
                        score=0.0,
                        reason=f"Validator error: {exc}",
                        remediation=["Check logs for details"],
                    )

        # Run REQ-4/5 sequentially
        for req_id, validator_class in [
            ("REQ-4", REQ4AccountabilityValidator),
            ("REQ-5", REQ5ChangelogValidator),
        ]:
            try:
                results[req_id] = validator_class(self.pr_number, self.repo).validate()
            except Exception as exc:
                logger.error(f"{req_id} failed: {exc}")
                results[req_id] = ComplianceResult(
                    requirement_id=req_id,
                    status="fail",
                    score=0.0,
                    reason=f"Validator error: {exc}",
                    remediation=["Check logs for details"],
                )

        # Run REQ-6 (async, doesn't block)
        try:
            results["REQ-6"] = REQ6PostMergeValidator(self.pr_number, self.repo).validate()
        except Exception as exc:
            logger.warning(f"REQ-6 failed: {exc}")
            results["REQ-6"] = ComplianceResult(
                requirement_id="REQ-6",
                status="warn",
                score=0.5,
                reason="Post-merge validation unavailable",
                remediation=["Check again after merge"],
            )

        # Generate report
        report = self._generate_report(results, strict)
        elapsed = time.time() - self.start_time
        report.elapsed_ms = elapsed * 1000

        logger.info(f"Compliance check completed: {report.status} (score: {report.overall_score})")

        return report

    def _generate_report(
        self,
        results: dict[str, ComplianceResult],
        strict: bool = False,
    ) -> ComplianceReport:
        """Generate compliance report from validator results."""

        # Calculate overall score
        scores = [r.score for r in results.values()]
        overall_score = (sum(scores) / len(scores) * 100) if scores else 0.0

        # Determine status
        failures = [r for r in results.values() if r.status == "fail"]
        warnings = [r for r in results.values() if r.status == "warn"]

        if failures:
            status = "BLOCK"
            rationale = f"Compliance check failed: {len(failures)} requirement(s) not met"
        elif warnings and strict:
            status = "WARN"
            rationale = f"Compliance check has {len(warnings)} warning(s)"
        elif warnings:
            status = "APPROVE"
            rationale = f"PR approved with {len(warnings)} warning(s) to address"
        else:
            status = "APPROVE"
            rationale = "All compliance requirements met"

        # Collect next steps
        next_steps: list[str] = []
        for req_id, result in results.items():
            if result.status in ("fail", "warn") and result.remediation:
                next_steps.extend(result.remediation[:2])  # Limit to top 2 per requirement

        # Remove duplicates while preserving order
        next_steps = list(dict.fromkeys(next_steps))[:5]

        return ComplianceReport(
            pr_number=self.pr_number,
            overall_score=overall_score,
            status=status,
            generated_at=datetime.now(timezone.utc).isoformat(),
            validators=[r.to_dict() for r in results.values()],
            decision_rationale=rationale,
            next_steps=next_steps,
        )


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run unified compliance check")
    parser.add_argument("--pr", required=True, help="PR number")
    parser.add_argument("--repo", default="Aries-Serpent/_codex_", help="Repository")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--strict", action="store_true", help="Strict mode (warnings block merge)")
    parser.add_argument("--output", help="Write JSON report to file")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    checker = UnifiedComplianceCheck(args.pr, args.repo)
    report = checker.run(strict=args.strict, timeout=args.timeout)

    if args.json or args.output:
        json_output = report.to_json()
        if args.output:
            Path(args.output).write_text(json_output, encoding="utf-8")
            print(f"✅ Report written to {args.output}")
        else:
            print(json_output)
    else:
        # Pretty print
        print(f"\n{'='*60}")
        print(f"Compliance Report for PR #{args.pr}")
        print(f"{'='*60}")
        print(f"Status: {report.status} (Score: {report.overall_score:.1f}/100)")
        print(f"Generated: {report.generated_at}")
        print(f"Time: {report.elapsed_ms:.0f}ms")
        print(f"\nRationale: {report.decision_rationale}")

        print(f"\nValidators ({len(report.validators)} total):")
        for result_dict in report.validators:
            icon = "✅" if result_dict["status"] == "pass" else ("⚠️" if result_dict["status"] == "warn" else "❌")
            print(f"  {icon} {result_dict['requirement_id']}: {result_dict['reason']}")

        if report.next_steps:
            print(f"\nNext Steps:")
            for i, step in enumerate(report.next_steps, 1):
                print(f"  {i}. {step}")

        print(f"\n{'='*60}\n")

    return 0 if report.status in ("APPROVE", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
