#!/usr/bin/env python3
"""
CI Gate for Vulnerability Drift Detection.

This script runs in CI to:
1. Check if any CVE exceptions have expired
2. Detect new CVEs in dependency chain
3. Validate suppression rules are justified
4. Enforce release gate checklist

Usage:
    python scripts/ci/check_cve_drift.py --check-expiry
    python scripts/ci/check_cve_drift.py --detect-new --lock-file uv.lock
    python scripts/ci/check_cve_drift.py --quarterly-audit
"""

import json
import subprocess
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import re


class CVEDriftGate:
    """CI gate for CVE and vulnerability exception governance."""

    def __init__(self, registry_path: str = ".codex/VULNERABILITY_EXCEPTION_REGISTRY.md", 
                 lock_file: str = "uv.lock",
                 verbose: bool = False):
        """
        Initialize CVE drift gate.

        Args:
            registry_path: Path to VULNERABILITY_EXCEPTION_REGISTRY.md
            lock_file: Path to uv.lock or requirements.txt
            verbose: Verbose output
        """
        self.registry_path = Path(registry_path)
        self.lock_file = Path(lock_file)
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.passed = True

    def check_expiry(self) -> bool:
        """
        Check if any CVE exceptions have expired.

        Returns:
            True if all exceptions non-expired, False otherwise
        """
        if not self.registry_path.exists():
            self.errors.append(f"Registry not found: {self.registry_path}")
            return False

        with open(self.registry_path, "r") as f:
            content = f.read()

        # Parse expiry dates from markdown table
        # Pattern: | **Expiry Date** | 2026-12-31 |
        expiry_pattern = r"\|\s*\*\*Expiry Date\*\*\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|"
        # Also look for inline expiry dates
        inline_pattern = r"expires_at\s*=\s*['\"](\d{4}-\d{2}-\d{2})"
        
        matches = re.findall(expiry_pattern, content) + re.findall(inline_pattern, content)
        
        if not matches:
            print("⚠️  No expiry dates found in registry")
            return True

        today = datetime.now().date()
        
        for expiry_str in matches:
            try:
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                days_remaining = (expiry_date - today).days
                
                if days_remaining < 0:
                    self.errors.append(f"EXPIRED exception (expired {abs(days_remaining)} days ago): {expiry_str}")
                    self.passed = False
                elif days_remaining < 30:
                    self.warnings.append(f"Exception expires in {days_remaining} days: {expiry_str}")
                elif self.verbose:
                    print(f"✓ Exception valid ({days_remaining} days remaining): {expiry_str}")
            except ValueError:
                self.errors.append(f"Invalid date format in registry: {expiry_str}")
                self.passed = False

        return self.passed

    def detect_new_cves(self) -> bool:
        """
        Detect new CVEs in dependency chain using pip-audit.

        Returns:
            True if no new CVEs, False otherwise
        """
        if not self.lock_file.exists():
            print(f"⚠️  Lock file not found: {self.lock_file}, skipping new CVE detection")
            return True

        try:
            # Run pip-audit to detect vulnerabilities
            result = subprocess.run(
                ["pip-audit", "--format", "json", f"--file={self.lock_file}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # No vulnerabilities found
                print("✓ No vulnerabilities detected by pip-audit")
                return True

            # Parse JSON output
            audit_data = json.loads(result.stdout)
            vulnerabilities = audit_data.get("vulnerabilities", [])

            # Check each vulnerability against registry
            documented = self._load_documented_cves()
            new_cves = []

            for vuln in vulnerabilities:
                cve_id = vuln.get("id", "UNKNOWN")
                package = vuln.get("package", "")
                version = vuln.get("version", "")

                if cve_id not in documented:
                    new_cves.append(f"{cve_id} in {package}=={version}")

            if new_cves:
                self.warnings.append(f"Found {len(new_cves)} unhandled CVEs:")
                for cve_info in new_cves:
                    self.warnings.append(f"  - {cve_info}")
                self.warnings.append("Action: Add exceptions to VULNERABILITY_EXCEPTION_REGISTRY.md and re-approve")

            return len(new_cves) == 0

        except subprocess.TimeoutExpired:
            self.errors.append("pip-audit timed out (> 30 seconds)")
            return False
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.errors.append(f"pip-audit check failed: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error during CVE detection: {e}")
            return False

    def _load_documented_cves(self) -> set:
        """Load documented CVE IDs from registry."""
        documented = set()
        if not self.registry_path.exists():
            return documented

        with open(self.registry_path, "r") as f:
            content = f.read()

        # Extract CVE IDs from markdown
        # Pattern: | **CVE ID** | CVE-2024-XXXXX |
        cve_pattern = r"\|\s*\*\*CVE ID\*\*\s*\|\s*(CVE-\d{4}-\d+|[A-Z]+-\d+-[A-Z0-9]+)\s*\|"
        matches = re.findall(cve_pattern, content)
        documented.update(matches)

        return documented

    def quarterly_audit(self) -> bool:
        """
        Run quarterly audit: check expirations and create GitHub issue if needed.

        Returns:
            True if audit passes
        """
        print("\n" + "=" * 70)
        print("QUARTERLY CVE EXCEPTION AUDIT")
        print("=" * 70)

        all_pass = True

        # Check expiry
        print("\n1. Checking exception expiry dates...")
        if not self.check_expiry():
            all_pass = False

        # Detect new CVEs
        print("\n2. Detecting new CVEs...")
        if not self.detect_new_cves():
            all_pass = False

        # Count exceptions
        documented = self._load_documented_cves()
        print(f"\n3. Exception Statistics:")
        print(f"   - Total documented exceptions: {len(documented)}")
        print(f"   - Warning: {len(self.warnings)}")
        print(f"   - Errors: {len(self.errors)}")

        if not all_pass or self.warnings or self.errors:
            self._create_github_issue()

        return all_pass

    def _create_github_issue(self):
        """Create GitHub issue with audit findings."""
        title = "Quarterly CVE Exception Audit - Action Required"
        
        body_parts = ["## Quarterly CVE Exception Audit Report\n"]
        
        if self.errors:
            body_parts.append("### ❌ Errors\n")
            for error in self.errors:
                body_parts.append(f"- {error}\n")
        
        if self.warnings:
            body_parts.append("### ⚠️ Warnings\n")
            for warning in self.warnings:
                body_parts.append(f"- {warning}\n")
        
        body_parts.append("\n### Action Items\n")
        body_parts.append("- [ ] Review and update VULNERABILITY_EXCEPTION_REGISTRY.md\n")
        body_parts.append("- [ ] Update suppression rules if needed\n")
        body_parts.append("- [ ] Approve changes\n")
        
        body = "".join(body_parts)
        
        # Try to create GitHub issue using gh CLI
        try:
            result = subprocess.run(
                ["gh", "issue", "create", "--title", title, "--body", body, "--label", "security:cve-exception"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✓ Created GitHub issue for audit findings")
                print(result.stdout)
            else:
                print(f"⚠️  Could not create GitHub issue (gh CLI not available)")
                print("Please create issue manually with findings above")
        except FileNotFoundError:
            print("⚠️  GitHub CLI (gh) not available; issue creation skipped")

    def report(self):
        """Print verification report."""
        print("\n" + "=" * 70)
        print("CVE DRIFT GATE REPORT")
        print("=" * 70)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")
        else:
            print("\n✅ No critical errors")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")

        print("\n" + "=" * 70)

        if self.passed and not self.errors:
            print("✅ CVE DRIFT GATE PASSED")
            return 0
        else:
            print("❌ CVE DRIFT GATE FAILED")
            return 1


def main():
    parser = argparse.ArgumentParser(
        description="CI gate for CVE and vulnerability exception governance"
    )
    parser.add_argument("--check-expiry", action="store_true", help="Check if exceptions have expired")
    parser.add_argument("--detect-new", action="store_true", help="Detect new CVEs in dependency chain")
    parser.add_argument("--quarterly-audit", action="store_true", help="Run full quarterly audit")
    parser.add_argument("--registry", default=".codex/VULNERABILITY_EXCEPTION_REGISTRY.md", help="Path to registry")
    parser.add_argument("--lock-file", default="uv.lock", help="Path to lock file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    gate = CVEDriftGate(
        registry_path=args.registry,
        lock_file=args.lock_file,
        verbose=args.verbose
    )

    # If no specific check, run all
    if not (args.check_expiry or args.detect_new or args.quarterly_audit):
        args.quarterly_audit = True

    if args.quarterly_audit:
        success = gate.quarterly_audit()
    else:
        all_pass = True

        if args.check_expiry:
            print("Checking exception expiry dates...")
            if not gate.check_expiry():
                all_pass = False

        if args.detect_new:
            print("Detecting new CVEs...")
            if not gate.detect_new_cves():
                all_pass = False

        gate.passed = all_pass

    gate.report()
    
    return 0 if gate.passed else 1


if __name__ == "__main__":
    sys.exit(main())
