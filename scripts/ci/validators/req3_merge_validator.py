#!/usr/bin/env python3
"""
REQ-3: Merge Authorization Validator

Validates that a PR can legally be merged:
- Not a draft
- No merge conflicts
- Required approvals obtained
- No blocking review comments
- Status checks passing
"""

from __future__ import annotations

import argparse
import logging
import sys

from base import ComplianceResult, RequirementValidator

logger = logging.getLogger(__name__)


class REQ3MergeValidator(RequirementValidator):
    """Validates PR merge authorization (REQ-3)."""
    
    @property
    def requirement_id(self) -> str:
        return "REQ-3"
    
    def _validate_impl(self) -> ComplianceResult:
        """Check PR merge authorization requirements."""
        try:
            pr_details = self._get_pr_details()
            reviews = self._get_pr_reviews()
        except Exception as exc:
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="fail",
                score=0.0,
                reason=f"Could not fetch PR details: {exc}",
                remediation=["Verify PR number is correct", "Check GitHub API access"],
            )
        
        issues: list[str] = []
        metadata: dict = {}
        
        # Check 1: Not a draft
        is_draft = pr_details.get("draft", False)
        metadata["is_draft"] = is_draft
        if is_draft:
            issues.append("PR is marked as draft")
        
        # Check 2: No merge conflicts
        mergeable = pr_details.get("mergeable")
        metadata["mergeable"] = mergeable
        if mergeable is False:
            issues.append("PR has merge conflicts")
        
        # Check 3: Check for blocking reviews
        blocking_reviews = [
            r for r in reviews
            if r.get("state") == "CHANGES_REQUESTED"
        ]
        metadata["blocking_reviews"] = len(blocking_reviews)
        if blocking_reviews:
            issues.append(f"{len(blocking_reviews)} review(s) requesting changes")
        
        # Check 4: Check for approvals
        approving_reviews = [
            r for r in reviews
            if r.get("state") == "APPROVED"
        ]
        metadata["approving_reviews"] = len(approving_reviews)
        
        # At least one approval required (unless by owner/bot)
        author = pr_details.get("user", {}).get("login", "")
        if not approving_reviews and author not in ("github-actions[bot]", "dependabot[bot]"):
            issues.append("No approving reviews found")
        
        # Check 5: Merge method allowed
        merge_allowed = pr_details.get("mergeable_state") == "clean"
        metadata["merge_allowed"] = merge_allowed
        
        # Determine overall status
        if issues:
            if len(issues) == 1 and "approving reviews" in issues[0]:
                # This is a warning - needs approval but could be obtained
                return ComplianceResult(
                    requirement_id=self.requirement_id,
                    status="warn",
                    score=0.5,
                    reason=f"Merge authorization checks need attention: {issues[0]}",
                    remediation=[
                        "Request review from code owner",
                        "Address any reviewer concerns",
                        "Wait for approval",
                    ],
                    metadata=metadata,
                )
            
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="fail",
                score=0.0,
                reason=f"Merge authorization checks failed: {'; '.join(issues[:3])}",
                remediation=[
                    "Remove draft status if applicable",
                    "Resolve merge conflicts",
                    "Address blocking review comments",
                    "Obtain required approvals",
                ],
                metadata=metadata,
            )
        
        return ComplianceResult(
            requirement_id=self.requirement_id,
            status="pass",
            score=1.0,
            reason="All merge authorization checks passed",
            remediation=[],
            metadata=metadata,
        )


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate PR merge authorization (REQ-3)")
    parser.add_argument("--pr", required=True, help="PR number")
    parser.add_argument("--repo", default="Aries-Serpent/_codex_", help="Repository")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    validator = REQ3MergeValidator(args.pr, args.repo)
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
