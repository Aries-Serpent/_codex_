#!/usr/bin/env python3
"""
test_codex_master_key_scopes.py — GitHub PAT scope capability scanner.

Validates that CODEX_MASTER_KEY has the required scopes for testing
all 10 GitHub API processes.

Key design principles
---------------------
Scope Detection:
    Uses GitHub's /user endpoint to retrieve the scopes from the
    X-OAuth-Scopes header. This is the authoritative source for PAT scopes.

Graceful Degradation:
    If X-OAuth-Scopes header is missing, attempts to infer scopes by
    testing specific API endpoints and measuring response codes.

Reporting:
    Generates a detailed scope coverage report showing:
    - Scopes present in the PAT
    - Missing required scopes (if any)
    - Recommended remediation (what to request in GitHub)

Usage
-----
    python scripts/ci/test_codex_master_key_scopes.py
    
    Or in CI/CD:
        export GH_TOKEN=<CODEX_MASTER_KEY>
        python scripts/ci/test_codex_master_key_scopes.py --report-json scopes.json
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger(__name__)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# GitHub API base URL
GH_API = "https://api.github.com"
API_VERSION = "2026-03-10"


# Scopes required for each process
REQUIRED_SCOPES = {
    "Process 1: Repository Variables": ["repo"],
    "Process 2: Organization Variables": ["admin:org"],
    "Process 3: Repository Secrets (Actions)": ["repo"],
    "Process 4: Organization Secrets (Actions)": ["admin:org"],
    "Process 5: Dependabot Secrets": ["repo"],
    "Process 6: Codespaces Secrets": ["codespace"],
    "Process 7: Workflow Dispatch": ["workflow"],
    "Process 8: Repository Hooks": ["admin:repo_hook"],
    "Process 9: Organization Hooks": ["admin:org_hook"],
    "Process 10: Audit Log Access": ["audit_log"],
}

# Additional scopes that grant broader access
SUPPLEMENTARY_SCOPES = {
    "repo": ["repo:status", "repo:invite", "public_repo", "repo:deployment"],
    "admin:org": ["write:org", "read:org", "manage_runners:org"],
    "user": ["read:user", "user:email"],
}


def resolve_token() -> str | None:
    """
    Resolve GitHub token from environment.
    
    Checks in order: CODEX_MASTER_KEY, CODEX_BACKUP_KEY, GH_TOKEN, GITHUB_TOKEN
    """
    for envvar in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GH_TOKEN", "GITHUB_TOKEN"):
        token = os.environ.get(envvar, "").strip()
        if token:
            log.info("Using token from %s", envvar)
            return token
    
    return None


def get_scopes_from_header(token: str) -> set[str]:
    """
    Fetch scopes from GitHub /user endpoint.
    
    The X-OAuth-Scopes header lists all scopes granted to the PAT.
    
    Args:
        token: GitHub PAT
    
    Returns:
        Set of scope strings (e.g., {"repo", "workflow", "admin:org"})
    """
    url = f"{GH_API}/user"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"******",
        "X-GitHub-Api-Version": API_VERSION,
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            # Get scopes from response header
            scopes_header = response.headers.get("X-OAuth-Scopes", "")
            
            if scopes_header:
                # Parse comma-separated scopes
                scopes = {s.strip() for s in scopes_header.split(",") if s.strip()}
                log.info("Detected scopes from X-OAuth-Scopes: %s", scopes)
                return scopes
            
            log.warning("X-OAuth-Scopes header not found in response")
            return set()
    
    except urllib.error.HTTPError as err:
        if err.code == 401:
            log.error("Unauthorized: Invalid or expired token")
            return set()
        elif err.code == 403:
            log.error("Forbidden: Token may not have required scopes")
            return set()
        raise


def infer_scopes_from_api_tests(token: str) -> set[str]:
    """
    Infer scopes by testing specific API endpoints.
    
    This is a fallback when X-OAuth-Scopes header is not available.
    
    Args:
        token: GitHub PAT
    
    Returns:
        Set of inferred scopes
    """
    scopes = set()
    
    # Test for 'repo' scope
    try:
        url = f"{GH_API}/repos/Aries-Serpent/_codex_"
        headers = {
            "Authorization": f"******",
            "X-GitHub-Api-Version": API_VERSION,
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            scopes.add("repo")
    except:
        pass
    
    # Test for 'admin:org' scope
    try:
        url = f"{GH_API}/orgs/Aries-Serpent"
        headers = {
            "Authorization": f"******",
            "X-GitHub-Api-Version": API_VERSION,
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            scopes.add("admin:org")
    except:
        pass
    
    # Test for 'workflow' scope
    try:
        url = f"{GH_API}/repos/Aries-Serpent/_codex_/actions/workflows"
        headers = {
            "Authorization": f"******",
            "X-GitHub-Api-Version": API_VERSION,
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            scopes.add("workflow")
    except:
        pass
    
    return scopes


def check_scopes(token: str) -> dict[str, Any]:
    """
    Check token scopes and generate coverage report.
    
    Args:
        token: GitHub PAT
    
    Returns:
        Report dict with scopes, missing requirements, etc.
    """
    # Get scopes from header (primary method)
    present_scopes = get_scopes_from_header(token)
    
    # Fallback to API testing if header not available
    if not present_scopes:
        log.info("Attempting to infer scopes via API tests...")
        present_scopes = infer_scopes_from_api_tests(token)
    
    # Build coverage report
    coverage = {}
    missing_scopes = set()
    
    for process_name, required in REQUIRED_SCOPES.items():
        process_coverage = {
            "required": required,
            "present": [s for s in required if s in present_scopes],
            "missing": [s for s in required if s not in present_scopes],
            "satisfied": all(s in present_scopes for s in required),
        }
        coverage[process_name] = process_coverage
        
        if not process_coverage["satisfied"]:
            missing_scopes.update(process_coverage["missing"])
    
    return {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "present_scopes": sorted(present_scopes),
        "coverage": coverage,
        "missing_scopes": sorted(missing_scopes),
        "all_processes_covered": missing_scopes == set(),
    }


def print_report(report: dict[str, Any]) -> None:
    """Pretty-print scope coverage report."""
    print("\n" + "=" * 80)
    print("CODEX_MASTER_KEY Scope Coverage Report")
    print("=" * 80)
    
    print(f"\nTimestamp: {report['timestamp']}")
    print(f"\nPresent Scopes: {', '.join(report['present_scopes']) or '(none)'}")
    
    if report["missing_scopes"]:
        print(f"\n⚠️  Missing Scopes: {', '.join(report['missing_scopes'])}")
    else:
        print("\n✅ All required scopes present!")
    
    print("\nProcess Coverage:")
    print("-" * 80)
    
    for process_name, coverage in report["coverage"].items():
        status = "✅" if coverage["satisfied"] else "❌"
        print(f"\n{status} {process_name}")
        print(f"   Required: {', '.join(coverage['required'])}")
        
        if coverage["present"]:
            print(f"   Present:  {', '.join(coverage['present'])}")
        
        if coverage["missing"]:
            print(f"   Missing:  {', '.join(coverage['missing'])}")
    
    print("\n" + "=" * 80)
    
    if report["all_processes_covered"]:
        print("✅ All 10 processes can be tested with current token!")
    else:
        print(
            f"❌ {len([p for p in report['coverage'].values() if not p['satisfied']])} "
            "processes missing required scopes."
        )
    
    print("=" * 80 + "\n")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check CODEX_MASTER_KEY scope coverage"
    )
    parser.add_argument(
        "--report-json",
        help="Write JSON report to this file",
    )
    parser.add_argument(
        "--token",
        help="GitHub PAT (overrides environment)",
    )
    
    args = parser.parse_args()
    
    # Get token
    token = args.token or resolve_token()
    if not token:
        log.error("No GitHub token found. Set CODEX_MASTER_KEY or GH_TOKEN.")
        return 1
    
    # Check scopes
    try:
        report = check_scopes(token)
    except Exception as err:
        log.error("Failed to check scopes: %s", err)
        return 1
    
    # Print report
    print_report(report)
    
    # Write JSON report if requested
    if args.report_json:
        with open(args.report_json, "w") as f:
            json.dump(report, f, indent=2)
        print(f"✅ JSON report written to {args.report_json}")
    
    # Exit code based on coverage
    return 0 if report["all_processes_covered"] else 1


if __name__ == "__main__":
    sys.exit(main())
