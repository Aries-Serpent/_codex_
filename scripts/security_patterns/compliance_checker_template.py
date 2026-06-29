"""Template: Compliance Checker Pattern

This template shows the pattern for creating compliance verification scripts
that can be stored as hidden scripts (Level 3 - MEDIUM).

Usage:
    1. Copy this template
    2. Implement compliance checks specific to your organization
    3. Store using HiddenScriptsManager
    4. Execute from compliance monitoring workflows

Example:
    from scripts.ci._hidden_scripts_manager import HiddenScriptsManager
    manager = HiddenScriptsManager()
    
    with open("policy_compliance_checker.py") as f:
        code = f.read()
    
    manager.store_hidden_script(
        name="policy_compliance_checker",
        script_content=code,
        security_level=3,  # MEDIUM
        dependencies=["pyyaml"]
    )
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple


class ComplianceChecker:
    """Template for compliance verification scripts (MEDIUM - Level 3)."""

    def __init__(self):
        """Initialize compliance checker."""
        self.policies = self._load_policies()
        self.violations = []

    def _load_policies(self) -> Dict[str, Any]:
        """Load compliance policies.
        
        Returns:
            Dictionary of policies
        """
        return {
            "code_review_required": {
                "description": "All code changes require review",
                "enabled": True,
                "threshold": 1  # At least 1 reviewer required
            },
            "tests_required": {
                "description": "All commits must include tests",
                "enabled": True,
                "threshold": 0.8  # At least 80% test coverage
            },
            "documentation_updated": {
                "description": "Documentation must be updated with code changes",
                "enabled": True
            },
            "security_scan_passed": {
                "description": "Security scanning must pass before merge",
                "enabled": True
            },
            "no_unresolved_vulnerabilities": {
                "description": "No HIGH/CRITICAL vulnerabilities can be unresolved",
                "enabled": True
            },
        }

    def check_code_review(self, pull_request: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if code review requirement is met.
        
        Args:
            pull_request: PR metadata
            
        Returns:
            Tuple of (compliant, message)
        """
        reviews = pull_request.get("reviews", [])
        approved_reviews = [r for r in reviews if r.get("state") == "APPROVED"]

        policy = self.policies["code_review_required"]
        threshold = policy["threshold"]

        if len(approved_reviews) >= threshold:
            return True, f"Code review policy met ({len(approved_reviews)} approvals)"
        else:
            return False, f"Code review policy NOT met ({len(approved_reviews)}/{threshold} approvals)"

    def check_test_coverage(self, coverage: float) -> Tuple[bool, str]:
        """Check if test coverage meets policy.
        
        Args:
            coverage: Test coverage percentage (0-100)
            
        Returns:
            Tuple of (compliant, message)
        """
        policy = self.policies["tests_required"]
        threshold = policy["threshold"]

        if coverage >= threshold * 100:
            return True, f"Test coverage meets policy ({coverage:.1f}%)"
        else:
            return False, f"Test coverage below policy ({coverage:.1f}% < {threshold*100:.0f}%)"

    def check_documentation(self, changes: List[Dict[str, str]]) -> Tuple[bool, str]:
        """Check if documentation was updated.
        
        Args:
            changes: List of changed files
            
        Returns:
            Tuple of (compliant, message)
        """
        doc_extensions = {'.md', '.rst', '.txt'}
        code_extensions = {'.py', '.js', '.go', '.java', '.c', '.cpp'}

        has_code_changes = any(
            Path(f.get("filename", "")).suffix in code_extensions
            for f in changes
        )

        has_doc_changes = any(
            Path(f.get("filename", "")).suffix in doc_extensions
            for f in changes
        )

        if not has_code_changes:
            return True, "No code changes, documentation not required"

        if has_doc_changes:
            return True, "Documentation updated with code changes"
        else:
            return False, "Code changed but documentation not updated"

    def check_security_scan(self, scan_results: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if security scan passed.
        
        Args:
            scan_results: Security scan results
            
        Returns:
            Tuple of (compliant, message)
        """
        status = scan_results.get("status")

        if status == "passed":
            return True, "Security scan passed"
        elif status == "warnings":
            return False, "Security scan has warnings"
        elif status == "failed":
            return False, "Security scan FAILED"
        else:
            return False, f"Unknown scan status: {status}"

    def check_no_high_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Check for HIGH/CRITICAL vulnerabilities.
        
        Args:
            vulnerabilities: List of vulnerabilities
            
        Returns:
            Tuple of (compliant, message)
        """
        high_critical = [
            v for v in vulnerabilities
            if v.get("severity") in ("HIGH", "CRITICAL") and v.get("resolved") is False
        ]

        if not high_critical:
            return True, "No unresolved HIGH/CRITICAL vulnerabilities"
        else:
            return False, f"Found {len(high_critical)} unresolved HIGH/CRITICAL vulnerabilities"

    def perform_compliance_check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform full compliance check.
        
        Args:
            context: Compliance context (PR, coverage, scan results, etc.)
            
        Returns:
            Compliance report
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "violations": [],
            "compliant": True
        }

        # Check 1: Code Review
        if "pull_request" in context:
            is_compliant, msg = self.check_code_review(context["pull_request"])
            report["checks"]["code_review"] = {"compliant": is_compliant, "message": msg}
            if not is_compliant:
                report["violations"].append("code_review")
                report["compliant"] = False

        # Check 2: Test Coverage
        if "coverage" in context:
            is_compliant, msg = self.check_test_coverage(context["coverage"])
            report["checks"]["test_coverage"] = {"compliant": is_compliant, "message": msg}
            if not is_compliant:
                report["violations"].append("test_coverage")
                report["compliant"] = False

        # Check 3: Documentation
        if "changes" in context:
            is_compliant, msg = self.check_documentation(context["changes"])
            report["checks"]["documentation"] = {"compliant": is_compliant, "message": msg}
            if not is_compliant:
                report["violations"].append("documentation")
                report["compliant"] = False

        # Check 4: Security Scan
        if "security_scan" in context:
            is_compliant, msg = self.check_security_scan(context["security_scan"])
            report["checks"]["security_scan"] = {"compliant": is_compliant, "message": msg}
            if not is_compliant:
                report["violations"].append("security_scan")
                report["compliant"] = False

        # Check 5: Vulnerabilities
        if "vulnerabilities" in context:
            is_compliant, msg = self.check_no_high_vulnerabilities(context["vulnerabilities"])
            report["checks"]["vulnerabilities"] = {"compliant": is_compliant, "message": msg}
            if not is_compliant:
                report["violations"].append("vulnerabilities")
                report["compliant"] = False

        # Final recommendation
        report["recommendation"] = "ALLOW_MERGE" if report["compliant"] else "BLOCK_MERGE"

        return report


def main():
    """Main entry point - called when script is executed."""
    # Simulate compliance check context
    context = {
        "pull_request": {
            "number": 123,
            "reviews": [
                {"state": "APPROVED", "author": "reviewer1"},
                {"state": "APPROVED", "author": "reviewer2"}
            ]
        },
        "coverage": 85.5,  # 85.5%
        "changes": [
            {"filename": "src/main.py"},
            {"filename": "docs/README.md"}
        ],
        "security_scan": {"status": "passed"},
        "vulnerabilities": []
    }

    checker = ComplianceChecker()
    report = checker.perform_compliance_check(context)

    print(json.dumps(report, indent=2))

    # Exit with appropriate code
    sys.exit(0 if report["compliant"] else 1)


if __name__ == "__main__":
    main()
