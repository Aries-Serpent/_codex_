#!/usr/bin/env python3
"""
Fetch all code scanning alerts from GitHub for systematic remediation.

This script requires a GitHub token with 'security-events:read' permission.

Usage:
    GITHUB_TOKEN=ghp_xxx python scripts/security/fetch_all_code_scanning_alerts.py \
        --repo Aries-Serpent/_codex_ \
        --output .codex/security/alerts_catalog.json
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library required. Install with: pip install requests")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


def fetch_alerts(repo: str, token: str, state: str = "open") -> list[dict[str, Any]]:
    """
    Fetch all code scanning alerts from GitHub API with pagination.

    Args:
        repo: Repository in format 'owner/repo'
        token: GitHub personal access token with security-events:read
        state: Alert state filter ('open', 'closed', or 'all')

    Returns:
        List of alert dictionaries
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    all_alerts = []
    page = 1
    per_page = 100  # Max allowed by GitHub API

    logger.info(f"Fetching {state} code scanning alerts for {repo}...")

    while True:
        url = f"{GITHUB_API_BASE}/repos/{repo}/code-scanning/alerts"
        params = {
            "state": state,
            "per_page": per_page,
            "page": page,
            "sort": "created",
            "direction": "desc",
        }

        logger.info(f"Fetching page {page}...")

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                logger.error(f"Repository not found or no access: {repo}")
            elif response.status_code == 403:
                logger.error("Access forbidden. Check token permissions (security-events:read required)")
            else:
                logger.error(f"HTTP error: {e}")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            sys.exit(1)

        alerts = response.json()

        if not alerts:
            break

        all_alerts.extend(alerts)
        logger.info(f"  Retrieved {len(alerts)} alerts (total: {len(all_alerts)})")

        # Check if there are more pages
        if len(alerts) < per_page:
            break

        page += 1

    logger.info(f"✅ Total alerts retrieved: {len(all_alerts)}")
    return all_alerts


def simplify_alert(alert: dict[str, Any]) -> dict[str, Any]:
    """Extract essential fields from alert for easier processing."""
    most_recent = alert.get("most_recent_instance", {})
    location = most_recent.get("location", {})

    return {
        "number": alert.get("number"),
        "state": alert.get("state"),
        "dismissed_reason": alert.get("dismissed_reason"),
        "dismissed_comment": alert.get("dismissed_comment"),
        "rule_id": alert["rule"]["id"],
        "rule_name": alert["rule"].get("name", ""),
        "rule_description": alert["rule"].get("description", ""),
        "rule_severity": alert["rule"].get("severity", "unknown"),
        "security_severity_level": alert["rule"].get("security_severity_level", "unknown"),
        "tool": alert["tool"]["name"],
        "created_at": alert.get("created_at"),
        "updated_at": alert.get("updated_at"),
        "url": alert.get("html_url"),
        "location_path": location.get("path"),
        "location_start_line": location.get("start_line"),
        "location_end_line": location.get("end_line"),
    }


def categorize_alerts(alerts: list[dict[str, Any]]) -> dict[str, Any]:
    """Categorize alerts by severity, rule, and state."""

    by_severity = defaultdict(list)
    by_rule = defaultdict(list)
    by_state = defaultdict(list)
    by_tool = defaultdict(list)

    for alert in alerts:
        severity = alert["security_severity_level"]
        rule = alert["rule_id"]
        state = alert["state"]
        tool = alert["tool"]

        by_severity[severity].append(alert)
        by_rule[rule].append(alert)
        by_state[state].append(alert)
        by_tool[tool].append(alert)

    return {
        "by_severity": dict(by_severity),
        "by_rule": dict(by_rule),
        "by_state": dict(by_state),
        "by_tool": dict(by_tool),
    }


def generate_remediation_plan(
    alerts: list[dict[str, Any]],
    categories: dict[str, Any],
    output_dir: Path
) -> None:
    """Generate a markdown remediation plan."""

    plan_path = output_dir / "ALERT_REMEDIATION_PLAN.md"

    # Count by severity
    severity_counts = {
        sev: len(alerts_list)
        for sev, alerts_list in categories["by_severity"].items()
    }

    # Sort severities
    severity_order = ["critical", "high", "medium", "low", "warning", "note", "error"]
    sorted_severities = [s for s in severity_order if s in severity_counts]

    with open(plan_path, "w", encoding="utf-8") as f:
        f.write("# 🔐 Code Scanning Alert Remediation Plan\n\n")
        f.write(f"> **Generated**: {datetime.now(timezone.utc).isoformat()}Z\n")
        f.write("> **Repository**: Aries-Serpent/_codex_\n")
        f.write(f"> **Total Alerts**: {len(alerts)}\n\n")

        f.write("---\n\n")
        f.write("## 📊 Alert Summary\n\n")
        f.write("| Severity | Count | Priority |\n")
        f.write("|----------|-------|----------|\n")

        priority_map = {
            "critical": "🔴 P0 - Immediate",
            "high": "🟠 P1 - Urgent",
            "medium": "🟡 P2 - Important",
            "low": "🟢 P3 - Normal",
        }

        for sev in sorted_severities:
            count = severity_counts[sev]
            priority = priority_map.get(sev, "⚪ P4 - Info")
            f.write(f"| **{sev.upper()}** | {count} | {priority} |\n")

        f.write("\n---\n\n")
        f.write("## 🎯 Remediation Strategy\n\n")

        for sev in sorted_severities:
            if sev not in categories["by_severity"]:
                continue

            alerts_for_severity = categories["by_severity"][sev]
            f.write(f"### {priority_map.get(sev, sev.upper())} - {sev.upper()} Severity ({len(alerts_for_severity)} alerts)\n\n")

            # Group by rule
            rules_in_severity = defaultdict(list)
            for alert in alerts_for_severity:
                rules_in_severity[alert["rule_id"]].append(alert)

            for rule_id, rule_alerts in sorted(rules_in_severity.items(), key=lambda x: -len(x[1])):
                f.write(f"#### Rule: `{rule_id}` ({len(rule_alerts)} occurrences)\n\n")
                f.write(f"**Description**: {rule_alerts[0]['rule_description']}\n\n")

                # Show first 5 locations
                f.write("**Sample Locations**:\n")
                for alert in rule_alerts[:5]:
                    path = alert.get("location_path", "unknown")
                    line = alert.get("location_start_line", "?")
                    num = alert["number"]
                    url = alert["url"]
                    f.write(f"- Alert #{num}: `{path}:{line}` ([view]({url}))\n")

                if len(rule_alerts) > 5:
                    f.write(f"- ... and {len(rule_alerts) - 5} more\n")

                f.write("\n")

        f.write("---\n\n")
        f.write("## 📋 Top 10 Rules by Frequency\n\n")
        f.write("| Rule ID | Count | Severity | Description |\n")
        f.write("|---------|-------|----------|-------------|\n")

        rule_counts = [(rule, len(alerts)) for rule, alerts in categories["by_rule"].items()]
        rule_counts.sort(key=lambda x: -x[1])

        for rule_id, count in rule_counts[:10]:
            sample = categories["by_rule"][rule_id][0]
            sev = sample["security_severity_level"]
            desc = sample["rule_description"][:60] + "..." if len(sample["rule_description"]) > 60 else sample["rule_description"]
            f.write(f"| `{rule_id}` | {count} | {sev} | {desc} |\n")

        f.write("\n---\n\n")
        f.write("## ✅ Next Steps for Copilot Agent\n\n")
        f.write("1. **CRITICAL Priority** (P0): Fix all critical alerts immediately\n")
        f.write("2. **HIGH Priority** (P1): Fix all high severity alerts\n")
        f.write("3. **MEDIUM Priority** (P2): Fix medium severity alerts or document suppressions\n")
        f.write("4. **LOW Priority** (P3): Batch fix or suppress with justification\n")
        f.write("5. **Verification**: After each batch, verify alerts are marked as 'Fixed' in Security tab\n")
        f.write("6. **Final Report**: Generate resolution report with before/after metrics\n\n")
        f.write("---\n\n")
        f.write("## 🔗 Resources\n\n")
        f.write("- [Security Tab](https://github.com/Aries-Serpent/_codex_/security/code-scanning)\n")
        f.write("- [Alert Catalog JSON](.codex/security/alerts_catalog.json)\n")
        f.write("- [Fix Templates](../../docs/security/FIX_TEMPLATES.md)\n")

    logger.info(f"✅ Remediation plan saved to: {plan_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch all code scanning alerts from GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch open alerts
  GITHUB_TOKEN=ghp_xxx python %(prog)s --repo owner/repo --output alerts.json

  # Fetch all alerts (open and closed)
  GITHUB_TOKEN=ghp_xxx python %(prog)s --repo owner/repo --state all --output alerts.json
        """,
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Repository in format 'owner/repo'",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output JSON file path",
    )
    parser.add_argument(
        "--state",
        choices=["open", "closed", "all"],
        default="open",
        help="Alert state filter (default: open)",
    )
    parser.add_argument(
        "--generate-plan",
        action="store_true",
        default=True,
        help="Generate remediation plan markdown (default: True)",
    )
    args = parser.parse_args()

    # Get token from environment
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("ERROR: GITHUB_TOKEN environment variable required")
        logger.error("Usage: GITHUB_TOKEN=ghp_xxx python %(prog)s ...")
        return 1

    # Fetch alerts
    alerts = fetch_alerts(args.repo, token, args.state)

    if not alerts:
        logger.warning("No alerts found!")
        return 0

    # Simplify alerts
    simplified = [simplify_alert(a) for a in alerts]

    # Categorize
    categories = categorize_alerts(simplified)

    # Save catalog
    args.output.parent.mkdir(parents=True, exist_ok=True)

    catalog = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repository": args.repo,
        "state_filter": args.state,
        "total_alerts": len(simplified),
        "summary": {
            "by_severity": {k: len(v) for k, v in categories["by_severity"].items()},
            "by_state": {k: len(v) for k, v in categories["by_state"].items()},
            "by_tool": {k: len(v) for k, v in categories["by_tool"].items()},
        },
        "categories": categories,
        "alerts": simplified,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    logger.info(f"✅ Alert catalog saved to: {args.output}")

    # Generate remediation plan
    if args.generate_plan:
        generate_remediation_plan(simplified, categories, args.output.parent)

    # Print summary
    print(f"\n{'='*70}")
    print("📊 ALERT FETCH SUMMARY")
    print(f"{'='*70}")
    print(f"Repository:    {args.repo}")
    print(f"Total Alerts:  {len(simplified)}")
    print(f"State Filter:  {args.state}")
    print("\nBy Severity:")
    for sev, count in sorted(catalog["summary"]["by_severity"].items(), key=lambda x: -x[1]):
        print(f"  {sev.upper():12} {count:5} alerts")
    print("\nBy Tool:")
    for tool, count in catalog["summary"]["by_tool"].items():
        print(f"  {tool:12} {count:5} alerts")
    print("\nOutputs:")
    print(f"  Catalog:  {args.output}")
    if args.generate_plan:
        print(f"  Plan:     {args.output.parent / 'ALERT_REMEDIATION_PLAN.md'}")
    print(f"{'='*70}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
