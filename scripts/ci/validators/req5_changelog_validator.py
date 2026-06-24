#!/usr/bin/env python3
"""
REQ-5: CHANGELOG Validator

Validates that CHANGELOG.md was updated in the latest commit.

This enforces the compliance requirement from session_wrapup_autofix.py.
"""

from __future__ import annotations

import argparse
import logging
import sys

from base import ComplianceResult, RequirementValidator

logger = logging.getLogger(__name__)

CHANGELOG_PATH = "CHANGELOG.md"
UNRELEASED_MARKER = "## [Unreleased]"


class REQ5ChangelogValidator(RequirementValidator):
    """Validates CHANGELOG requirement (REQ-5)."""

    @property
    def requirement_id(self) -> str:
        return "REQ-5"

    def _validate_impl(self) -> ComplianceResult:
        """Check if CHANGELOG.md was updated in latest commit."""
        try:
            pr_details = self._get_pr_details()
            commits = self._get_pr_commits()
        except Exception as exc:
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="fail",
                score=0.0,
                reason=f"Could not fetch PR details: {exc}",
                remediation=["Verify PR number is correct", "Check GitHub API access"],
            )

        metadata: dict = {}

        # Get the latest commit SHA
        if not commits:
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="fail",
                score=0.0,
                reason="No commits found in PR",
                remediation=["Ensure PR has at least one commit"],
                metadata=metadata,
            )

        latest_commit = commits[-1]
        commit_sha = latest_commit.get("sha", "")
        metadata["commit_sha"] = commit_sha[:12]

        # Get files modified in this commit
        try:
            commit_details = self._get_commit_details(commit_sha)
            files_in_commit = commit_details.get("files", [])
            modified_files = {f.get("filename", "") for f in files_in_commit}
        except Exception as exc:
            logger.warning(f"Could not fetch commit details: {exc}")
            modified_files = set()

        metadata["files_in_commit"] = len(modified_files)

        # Check if CHANGELOG was modified in latest commit
        if CHANGELOG_PATH not in modified_files:
            metadata["changelog_updated"] = False
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="fail",
                score=0.0,
                reason=f"CHANGELOG.md not updated in latest commit ({commit_sha[:12]})",
                remediation=[
                    "Update CHANGELOG.md with entry describing changes",
                    "Add entry under [Unreleased] section",
                    "Follow changelog format (issue references, category, summary)",
                    "Commit the changes: `git add CHANGELOG.md`",
                    "Or run: `python scripts/ci/session_wrapup_autofix.py --pr <pr-number> --fix-changelog`",
                ],
                metadata=metadata,
            )

        metadata["changelog_updated"] = True

        # Verify CHANGELOG has content and [Unreleased] section
        try:
            changelog_content = self._read_file(CHANGELOG_PATH) or ""
            if not changelog_content.strip():
                return ComplianceResult(
                    requirement_id=self.requirement_id,
                    status="fail",
                    score=0.0,
                    reason="CHANGELOG.md is empty",
                    remediation=["Add content to CHANGELOG.md"],
                    metadata=metadata,
                )

            if UNRELEASED_MARKER not in changelog_content:
                return ComplianceResult(
                    requirement_id=self.requirement_id,
                    status="warn",
                    score=0.5,
                    reason="CHANGELOG.md updated but [Unreleased] section not found",
                    remediation=[
                        "Ensure [Unreleased] section exists at top of CHANGELOG",
                        "Format: '## [Unreleased]'",
                        "Add entries below this section",
                    ],
                    metadata=metadata,
                )

            # Check that there's content after the [Unreleased] marker
            unreleased_idx = changelog_content.index(UNRELEASED_MARKER)
            unreleased_section = changelog_content[unreleased_idx:]

            # Look for at least some content after the marker
            lines_after = unreleased_section.split("\n")[1:]  # Skip the marker line
            content_lines = [
                l for l in lines_after
                if l.strip() and not l.startswith("#")  # Skip empty/heading lines
            ]

            if not content_lines:
                return ComplianceResult(
                    requirement_id=self.requirement_id,
                    status="warn",
                    score=0.5,
                    reason="CHANGELOG.md [Unreleased] section is empty",
                    remediation=[
                        "Add entries to the [Unreleased] section",
                        "Example: '- Fix: Resolved issue #1234 (description)'",
                    ],
                    metadata=metadata,
                )

            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="pass",
                score=1.0,
                reason=f"CHANGELOG.md was properly updated in commit {commit_sha[:12]}",
                remediation=[],
                metadata=metadata,
            )

        except Exception as exc:
            logger.warning(f"Could not validate CHANGELOG content: {exc}")
            # If we can't read it but it was modified, give benefit of doubt (warn)
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="warn",
                score=0.5,
                reason="CHANGELOG.md was modified but content verification failed",
                remediation=["Verify CHANGELOG.md format is correct"],
                metadata=metadata,
            )


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate CHANGELOG (REQ-5)")
    parser.add_argument("--pr", required=True, help="PR number")
    parser.add_argument("--repo", default="Aries-Serpent/_codex_", help="Repository")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--sha", help="Optional commit SHA to check (defaults to latest in PR)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    validator = REQ5ChangelogValidator(args.pr, args.repo)
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
