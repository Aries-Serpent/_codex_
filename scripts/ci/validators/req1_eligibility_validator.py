#!/usr/bin/env python3
"""
REQ-1: PR Eligibility Validator

Validates that a PR meets basic structural requirements:
- Branch name follows convention
- PR title is descriptive
- PR description adequate
- Reviewer assigned

Reviewer-assignment exemption for bot/copilot PRs
--------------------------------------------------
GitHub Copilot agent PRs and other bot-authored PRs (user.type == "Bot", login
ending in "[bot]", or branch prefix "copilot/") legitimately have no human
reviewers at creation time.  For these PRs the reviewer check is downgraded from
a hard FAIL (score=0.0) to a WARN (score=0.5) so that the overall governance
score is not blocked solely by the absence of a reviewer.

The bot identity is determined primarily via the server-side ``user.type`` field
(returned as ``"Bot"`` by the GitHub API for GitHub Apps / bots), which cannot
be forged via branch naming.  The ``[bot]`` login suffix and ``copilot/`` branch
prefix are accepted as secondary signals for robustness.
"""

from __future__ import annotations

import argparse
import logging
import sys

from base import ComplianceResult, RequirementValidator

logger = logging.getLogger(__name__)

# Valid branch prefixes
VALID_BRANCH_PREFIXES = {
    "feat", "fix", "docs", "test", "chore",
    "refactor", "perf", "ci", "build", "revert", "copilot",
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
        reviewer_warning: str | None = None
        if not reviewers:
            # Exempt bot/copilot-authored PRs from the hard reviewer requirement.
            # Use user.type == "Bot" as the primary (server-side, unforgeable) signal.
            # Fall back to login suffix and branch prefix as secondary signals.
            pr_author = pr_details.get("user", {}).get("login", "")
            pr_author_type = pr_details.get("user", {}).get("type", "")
            is_bot_pr = (
                pr_author_type == "Bot"
                or pr_author.endswith("[bot]")
                or branch_name.startswith("copilot/")
            )
            if is_bot_pr:
                reviewer_warning = "No reviewers assigned (bot/copilot PR — warning only)"
                metadata["reviewer_exemption"] = "bot_or_copilot_branch"
            else:
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

        if reviewer_warning:
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="warn",
                score=0.5,
                reason=reviewer_warning,
                remediation=["Consider assigning a human reviewer for visibility"],
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
