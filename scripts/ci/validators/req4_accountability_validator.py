#!/usr/bin/env python3
"""
REQ-4: Accountability Validator

Validates that the AGENT_ACCOUNTABILITY_REPORT.md was updated in the latest commit.

This enforces the compliance requirement from session_wrapup_autofix.py.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from base import ComplianceResult, RequirementValidator

logger = logging.getLogger(__name__)

ACCOUNTABILITY_REPORT_PATH = "docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md"


class REQ4AccountabilityValidator(RequirementValidator):
    """Validates accountability report requirement (REQ-4)."""
    
    @property
    def requirement_id(self) -> str:
        return "REQ-4"
    
    def _validate_impl(self) -> ComplianceResult:
        """Check if accountability report was updated in latest commit."""
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
        
        latest_commit = commits[-1]  # Last commit in the PR
        commit_sha = latest_commit.get("sha", "")
        metadata["commit_sha"] = commit_sha[:12]  # Short SHA
        
        # Get files modified in this commit
        try:
            commit_details = self._get_commit_details(commit_sha)
            files_in_commit = commit_details.get("files", [])
            modified_files = {f.get("filename", "") for f in files_in_commit}
        except Exception as exc:
            logger.warning(f"Could not fetch commit details: {exc}")
            modified_files = set()
        
        metadata["files_in_commit"] = len(modified_files)
        
        # Check if accountability report was modified in latest commit
        if ACCOUNTABILITY_REPORT_PATH in modified_files:
            metadata["accountability_report_updated"] = True
            
            # Check that it has content (not just whitespace)
            try:
                report_content = self._read_file(ACCOUNTABILITY_REPORT_PATH) or ""
                if report_content.strip():
                    return ComplianceResult(
                        requirement_id=self.requirement_id,
                        status="pass",
                        score=1.0,
                        reason=f"Accountability report was updated in commit {commit_sha[:12]}",
                        remediation=[],
                        metadata=metadata,
                    )
            except Exception as exc:
                logger.warning(f"Could not read accountability report: {exc}")
        
        metadata["accountability_report_updated"] = False
        
        # Report was not updated
        return ComplianceResult(
            requirement_id=self.requirement_id,
            status="fail",
            score=0.0,
            reason=f"Accountability report not updated in latest commit ({commit_sha[:12]})",
            remediation=[
                "Update docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md",
                "Add entry describing session summary, results, and governance notes",
                "Commit the changes: `git add docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`",
                "Or run: `python scripts/ci/session_wrapup_autofix.py --pr <pr-number> --fix-accountability`",
            ],
            metadata=metadata,
        )


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate accountability report (REQ-4)")
    parser.add_argument("--pr", required=True, help="PR number")
    parser.add_argument("--repo", default="Aries-Serpent/_codex_", help="Repository")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--sha", help="Optional commit SHA to check (defaults to latest in PR)")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    validator = REQ4AccountabilityValidator(args.pr, args.repo)
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
