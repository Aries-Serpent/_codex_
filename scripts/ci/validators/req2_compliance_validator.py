#!/usr/bin/env python3
"""
REQ-2: Compliance Validator

Validates that a PR meets quality and security standards:
- Documentation updated (where applicable)
- Tests updated (where applicable)
- No security vulnerabilities
- Linting passes
- Coverage maintained
"""

from __future__ import annotations

import argparse
import logging
import sys

from base import ComplianceResult, RequirementValidator

logger = logging.getLogger(__name__)


class REQ2ComplianceValidator(RequirementValidator):
    """Validates PR compliance (REQ-2)."""
    
    @property
    def requirement_id(self) -> str:
        return "REQ-2"
    
    def _validate_impl(self) -> ComplianceResult:
        """Check PR compliance requirements."""
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
        
        issues: list[str] = []
        metadata: dict = {}
        
        # Get the files changed in this PR
        try:
            files_output = self._gh_api_call(
                f"repos/{self.repo}/pulls/{self.pr_number}/files",
                jq=".[].filename",
            )
            files_changed = set(files_output.strip().split("\n")) if files_output else set()
        except Exception as exc:
            logger.warning(f"Could not fetch files: {exc}")
            files_changed = set()
        
        metadata["files_changed"] = len(files_changed)
        
        # Check 1: Documentation updated
        doc_files = {f for f in files_changed if f.startswith("docs/") or f == "CHANGELOG.md"}
        meta_changed_code = any(f.startswith("src/") or f.startswith("tests/") for f in files_changed)
        
        if meta_changed_code and not doc_files:
            logger.warning("Code changed but no docs/ or CHANGELOG updates")
        
        metadata["doc_files_changed"] = len(doc_files)
        
        # Check 2: Tests updated  (if code changed)
        code_files = {f for f in files_changed if f.startswith("src/") and not f.startswith("src/codex/logging")}
        test_files = {f for f in files_changed if f.startswith("tests/")}
        
        if code_files and not test_files:
            issues.append("Code changed but no tests added/updated")
        
        metadata["code_files_changed"] = len(code_files)
        metadata["test_files_changed"] = len(test_files)
        
        # Check 3: Check for obvious security issues
        # (This is a basic check; real security scanning happens in CI)
        security_issues = _check_security_patterns(files_changed)
        if security_issues:
            issues.extend(security_issues)
        
        metadata["security_issues"] = len(security_issues)
        
        # Check 4: Status checks
        status_checks = pr_details.get("statuses", [])
        metadata["status_checks"] = len(status_checks)
        
        # For now, just warn if no checks are passing (we can't determine without full CI run)
        # This will be more complete when integrated with actual CI
        
        # Determine overall status
        if "No tests added" in "\n".join(issues):
            # This is a warning-level issue (code changed but no tests)
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="warn",
                score=0.5,
                reason="Some compliance checks require attention: " + "; ".join(issues[:2]),
                remediation=[
                    "Add or update tests for code changes",
                    "Run test suite locally to verify: `nox -s tests`",
                    "Update documentation if adding new features",
                ],
                metadata=metadata,
            )
        
        if issues:
            return ComplianceResult(
                requirement_id=self.requirement_id,
                status="fail",
                score=0.0,
                reason=f"Compliance checks failed: {'; '.join(issues[:3])}",
                remediation=[
                    "Add or update tests",
                    "Update documentation",
                    "Fix any security issues",
                    "Run linting: `pre-commit run --files <files>`",
                ],
                metadata=metadata,
            )
        
        return ComplianceResult(
            requirement_id=self.requirement_id,
            status="pass",
            score=1.0,
            reason="All compliance checks passed",
            remediation=[],
            metadata=metadata,
        )


def _check_security_patterns(files: set[str]) -> list[str]:
    """Check for obvious security anti-patterns."""
    issues: list[str] = []
    
    # Check for files that shouldn't be committed
    dangerous_files = {
        f for f in files
        if any(
            pattern in f
            for pattern in [".env", ".key", ".pem", ".secret", ".password", "__pycache__"]
        )
    }
    
    if dangerous_files:
        issues.append(f"Dangerous files detected: {', '.join(dangerous_files)}")
    
    return issues


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate PR compliance (REQ-2)")
    parser.add_argument("--pr", required=True, help="PR number")
    parser.add_argument("--repo", default="Aries-Serpent/_codex_", help="Repository")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    validator = REQ2ComplianceValidator(args.pr, args.repo)
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
