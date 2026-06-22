#!/usr/bin/env python3
"""
REQ-1: PR Eligibility Validator

Validates that a PR meets basic structural requirements:
- Branch name follows convention
- PR title is descriptive
- PR description adequate
- Reviewer assigned
"""

from __future__ import annotations

import argparse
import logging
import sys
import re
from pathlib import Path
from typing import Optional

from base import ComplianceResult, RequirementValidator

logger = logging.getLogger(__name__)

# Valid branch prefixes
VALID_BRANCH_PREFIXES = {
    "feat", "fix", "docs", "test", "chore",
    "refactor", "perf", "ci", "build", "revert",
}

# Minimum requirements
MIN_TITLE_LENGTH = 10
MIN_DESCRIPTION_LENGTH = 50
MIN_DESCRIPTION_WORDS = 5


class REQ1EligibilityValidator(RequirementValidator):
    """Validates PR eligibility (REQ-1)."""
    
    @property
    def requirement_id(self) -> str:
        return "REQ-1"
    
    def _validate_impl(self) -> ComplianceResult:
        """Check PR eligibility requirements."""
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
        
        issues: list[str] = []
        metadata: dict = {}
        
        # Check 1: Branch naming
        branch_name = pr_details.get("head", {}).get("ref", "")
        metadata["branch"] = branch_name
        branch_valid = _check_branch_name(branch_name)
        if not branch_valid:
            issues.append(f"Branch name '{branch_name}' doesn't follow convention (use feat/, fix/, docs/, etc.)")
            metadata["branch_valid"] = False
        else:
            metadata["branch_valid"] = True
        
        # Check 2: PR title
        title = pr_details.get("title", "").strip()
        metadata["title"] = title
        title_issues = _check_title_quality(title)
        if title_issues:
            issues.extend(title_issues)
            metadata["title_quality"] = "low"
        else:
            metadata["title_quality"] = "high"
        
        # Check 3: PR description
        body = pr_details.get("body", "").strip()
        metadata["description_chars"] = len(body)
        body_issues = _check_description_quality(body)
        if body_issues:
            issues.extend(body_issues)
            metadata["description_quality"] = "low"
        else:
            metadata["description_quality"] = "high"
        
        # Check 4: Reviewer assignment
        reviewers = pr_details.get("requested_reviewers", [])
        metadata["reviewers_assigned"] = len(reviewers) > 0
        metadata["reviewers_count"] = len(reviewers)
        if not reviewers:
            issues.append("No reviewers assigned")
        
        # Determine overall status
        if issues:
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="fail",
                score=0.0,
                reason=f"PR eligibility checks failed: {'; '.join(issues[:3])}",
                remediation=[
                    "Ensure branch name follows convention (feat/, fix/, docs/, etc.)",
                    "Use a descriptive PR title (minimum 10 characters)",
                    "Add detailed PR description (minimum 50 characters)",
                    "Assign at least one reviewer",
                ],
                metadata=metadata,
            )
        
        return ComplianceResult(
            requirement_id=self.requirement_id,
            status="pass",
            score=1.0,
            reason="All PR eligibility checks passed",
            remediation=[],
            metadata=metadata,
        )


def _check_branch_name(branch: str) -> bool:
    """Validate branch name follows convention."""
    if not branch:
        return False
    
    # Extract prefix (everything before first /)
    if "/" not in branch:
        return False
    
    prefix = branch.split("/")[0].lower()
    return prefix in VALID_BRANCH_PREFIXES


def _check_title_quality(title: str) -> list[str]:
    """Validate PR title quality."""
    issues: list[str] = []
    
    if not title:
        issues.append("PR title is empty")
    elif len(title) < MIN_TITLE_LENGTH:
        issues.append(f"PR title too short (got {len(title)}, min {MIN_TITLE_LENGTH})")
    
    # Check for auto-generated titles
    if title.startswith("Merge pull request") or title.startswith("Merge branch"):
        issues.append("PR title appears to be auto-generated (avoid merge commits in title)")
    
    return issues


def _check_description_quality(body: str) -> list[str]:
    """Validate PR description quality."""
    issues: list[str] = []
    
    if not body:
        issues.append("PR description is empty")
    elif len(body) < MIN_DESCRIPTION_LENGTH:
        issues.append(f"PR description too short (got {len(body)}, min {MIN_DESCRIPTION_LENGTH})")
    
    # Count words (rough estimate)
    words = len(body.split())
    if words < MIN_DESCRIPTION_WORDS:
        issues.append(f"PR description has too few words (got {words}, min {MIN_DESCRIPTION_WORDS})")
    
    return issues


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate PR eligibility (REQ-1)")
    parser.add_argument("--pr", required=True, help="PR number")
    parser.add_argument("--repo", default="Aries-Serpent/_codex_", help="Repository")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    validator = REQ1EligibilityValidator(args.pr, args.repo)
    result = validator.validate()
    
    if args.json:
        print(result.to_json())
    else:
        status_icon = "✅" if result.status == "pass" else "❌"
        print(f"{status_icon} {result.requirement_id}: {result.reason}")
        if result.remediation:
            print("\nRemediation:")
            for step in result.remediation:
                print(f"  - {step}")
    
    return 0 if result.status == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
