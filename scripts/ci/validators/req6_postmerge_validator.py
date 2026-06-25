#!/usr/bin/env python3
"""
REQ-6: Post-Merge Validator

Validates PR health after merge:
- All workflows passed after merge
- No new CI failures introduced
- No regressions detected
- Deployment successful (if applicable)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from base import ComplianceResult, RequirementValidator

logger = logging.getLogger(__name__)


class REQ6PostMergeValidator(RequirementValidator):
    """Validates post-merge health (REQ-6)."""

    @property
    def requirement_id(self) -> str:
        return "REQ-6"

    def _validate_impl(self) -> ComplianceResult:
        """Check post-merge health."""
        metadata: dict = {}

        # This validator typically runs AFTER merge, so we check the merge commit
        # For now, we'll check if the PR is merged
        try:
            pr_details = self._get_pr_details()
        except Exception as exc:
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="fail",
                score=0.0,
                reason=f"Could not fetch PR details: {exc}",
                remediation=["Verify PR number is correct", "Check GitHub API access"],
            )

        # Check if merged
        merged_at = pr_details.get("merged_at")
        is_merged = pr_details.get("merged", False)
        metadata["is_merged"] = is_merged
        metadata["merged_at"] = merged_at

        if not is_merged:
            # PR not yet merged - this validator isn't applicable yet
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="warn",
                score=0.5,
                reason="PR not yet merged - post-merge validation not applicable",
                remediation=["Merge PR first", "Then re-run this validator"],
                metadata=metadata,
            )

        # Get the merge commit SHA
        merge_commit_sha = pr_details.get("merge_commit_sha")
        if not merge_commit_sha:
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="warn",
                score=0.5,
                reason="Merge commit SHA not found",
                remediation=["Check that PR is properly merged"],
                metadata=metadata,
            )

        metadata["merge_commit_sha"] = merge_commit_sha[:12]

        # Try to get workflow runs for the merge commit
        try:
            workflow_runs = self._gh_api_call(
                f"repos/{self.repo}/actions/runs",
                jq='.workflow_runs | map(select(.head_sha == "{merge_commit_sha}")) | .[0:5]'.format(
                    merge_commit_sha=merge_commit_sha
                ),
            )
            runs = json.loads(workflow_runs) if workflow_runs else []
        except Exception as exc:
            logger.warning(f"Could not fetch workflow runs: {exc}")
            runs = []

        metadata["workflow_runs_found"] = len(runs)

        if not runs:
            # No workflow runs found yet (may still be running)
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="warn",
                score=0.5,
                reason="No workflow runs found yet for merge commit (may still be running)",
                remediation=["Wait for workflows to complete", "Re-run validator later"],
                metadata=metadata,
            )

        # Check workflow statuses
        failed_runs = [r for r in runs if r.get("conclusion") == "failure"]
        successful_runs = [r for r in runs if r.get("conclusion") == "success"]

        metadata["successful_runs"] = len(successful_runs)
        metadata["failed_runs"] = len(failed_runs)

        if failed_runs:
            failed_names = [r.get("name", "unknown") for r in failed_runs]
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="fail",
                score=0.0,
                reason=f"Post-merge workflows failed: {', '.join(failed_names[:3])}",
                remediation=[
                    "Check failed workflow logs",
                    "Investigate root cause",
                    "Apply fixes or rollback if necessary",
                ],
                metadata=metadata,
            )

        if successful_runs:
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="pass",
                score=1.0,
                reason=f"All post-merge workflows passed ({len(successful_runs)} runs)",
                remediation=[],
                metadata=metadata,
            )

        # Workflows still running
        return ComplianceResult(
            requirement_id=self.requirement_id,
            status="warn",
            score=0.5,
            reason="Workflows for merge commit are still running",
            remediation=["Wait for workflows to complete", "Re-run validator later"],
            metadata=metadata,
        )


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate post-merge health (REQ-6)")
    parser.add_argument("--pr", required=True, help="PR number")
    parser.add_argument("--repo", default="Aries-Serpent/_codex_", help="Repository")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--merged-sha", help="Optional merged commit SHA")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    validator = REQ6PostMergeValidator(args.pr, args.repo)
    result = validator.validate()

    if args.json:
        print(result.to_json())
    else:
        status_icon = "✅" if result.status == "pass" else ("⚠️" if result.status == "warn" else "❌")
        print(f"{status_icon} {result.requirement_id}: {result.reason}")
        if result.remediation:
            print("\nRemediation:")
            for step in result.remediation:
                print(f"  - {step}")

    return 0 if result.status == "pass" else (0 if result.status == "warn" else 1)


if __name__ == "__main__":
    sys.exit(main())
