#!/usr/bin/env python3
"""
Fetch CodeQL Code Scanning Alerts from GitHub API

This script fetches all code scanning alerts from the GitHub API, handling
pagination across all 59+ pages, and exports the data in multiple formats
(JSON, CSV, Markdown) for analysis and tracking.

Author: mbaetiong
Created: 2026-01-26
Part of: CodeQL Alert Resolution Planset
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class CodeScanningAlert:
    """Represents a code scanning alert from GitHub."""
    alert_number: int
    rule_id: str
    severity: str
    state: str
    file_path: str
    line_start: int
    line_end: int
    description: str
    created_at: str
    html_url: str
    cwe_id: Optional[str] = None
    tool_name: str = "CodeQL"
    category: str = "security"
    dismissed_reason: Optional[str] = None
    dismissed_comment: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding metadata if empty."""
        data = asdict(self)
        if not data.get("metadata"):
            del data["metadata"]
        return data


class CodeQLAlertFetcher:
    """Fetch and manage CodeQL code scanning alerts."""

    def __init__(
        self,
        owner: str,
        repo: str,
        token: Optional[str] = None,
        max_pages: Optional[int] = None,
    ):
        """
        Initialize the alert fetcher.

        Args:
            owner: Repository owner (e.g., "Aries-Serpent")
            repo: Repository name (e.g., "_codex_")
            token: GitHub API token (defaults to GITHUB_TOKEN env var)
            max_pages: Maximum number of pages to fetch (None = all pages)
        """
        if not HAS_REQUESTS:
            raise ImportError("requests library is required. Install with: pip install requests")

        self.owner = owner
        self.repo = repo
        self.token = token if token is not None else os.environ.get("GITHUB_TOKEN", "")
        self.max_pages = max_pages
        # nosemgrep: url-substring-check - GitHub API base for alert retrieval
        self.base_url = "https://api.github.com"
        self.session = requests.Session()

        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            })
        else:
            logger.warning("No GitHub token provided. Rate limits will be lower.")

    def fetch_all_alerts(
        self,
        state: str = "open",
        severity: Optional[str] = None,
        ref: Optional[str] = None,
    ) -> list[CodeScanningAlert]:
        """
        Fetch all code scanning alerts with pagination.

        Args:
            state: Alert state ("open", "closed", "dismissed", "fixed")
            severity: Filter by severity ("critical", "high", "medium", "low")
            ref: Git reference (branch/tag) to filter by

        Returns:
            List of CodeScanningAlert objects
        """
        all_alerts = []
        page = 1
        per_page = 100  # Maximum allowed by GitHub API

        logger.info(f"Fetching {state} alerts for {self.owner}/{self.repo}")

        while True:
            if self.max_pages and page > self.max_pages:
                logger.info(f"Reached max_pages limit ({self.max_pages})")
                break

            logger.info(f"Fetching page {page}...")

            # Build query parameters
            params = {
                "state": state,
                "page": page,
                "per_page": per_page,
            }
            if severity:
                params["severity"] = severity
            if ref:
                params["ref"] = ref

            # Make API request
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/code-scanning/alerts"

            try:
                response = self.session.get(url, params=params, timeout=30)

                # Check rate limits
                remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
                if remaining < 10:
                    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                    wait_seconds = max(reset_time - time.time(), 0) + 1
                    logger.warning(f"Rate limit low ({remaining}). Waiting {wait_seconds}s...")
                    time.sleep(wait_seconds)

                if response.status_code == 200:
                    alerts_data = response.json()

                    if not alerts_data:
                        logger.info(f"No more alerts found (page {page})")
                        break

                    # Parse alerts
                    for alert_data in alerts_data:
                        alert = self._parse_alert(alert_data)
                        if alert:
                            all_alerts.append(alert)

                    logger.info(f"  Found {len(alerts_data)} alerts on page {page}")
                    page += 1

                    # Rate limiting: be nice to the API
                    time.sleep(0.5)

                elif response.status_code == 403:
                    logger.error("API rate limit exceeded or insufficient permissions")
                    break
                elif response.status_code == 404:
                    logger.error("Repository not found or code scanning not enabled")
                    break
                else:
                    logger.error(f"API request failed: {response.status_code} - {response.text}")
                    break

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on page {page}: {e}")
                break

        logger.info(f"Total alerts fetched: {len(all_alerts)}")
        return all_alerts

    def _parse_alert(self, data: dict[str, Any]) -> Optional[CodeScanningAlert]:
        """Parse GitHub API alert data into CodeScanningAlert."""
        try:
            # Extract rule information
            rule = data.get("rule", {})
            rule_id = rule.get("id", "unknown")
            severity = rule.get("severity", "medium")
            description = rule.get("description") or rule.get("name", "Unknown vulnerability")

            # Extract location information
            most_recent = data.get("most_recent_instance", {})
            location = most_recent.get("location", {})
            file_path = location.get("path", "unknown")
            line_start = location.get("start_line", 0)
            line_end = location.get("end_line", 0)

            # Extract CWE ID
            cwe_id = self._extract_cwe_id(rule)

            # Extract dismissal information
            dismissed_reason = data.get("dismissed_reason")
            dismissed_comment = data.get("dismissed_comment")

            # Tool information
            tool_name = data.get("tool", {}).get("name", "CodeQL")

            return CodeScanningAlert(
                alert_number=data.get("number", 0),
                rule_id=rule_id,
                severity=severity,
                state=data.get("state", "open"),
                file_path=file_path,
                line_start=line_start,
                line_end=line_end,
                description=description,
                created_at=data.get("created_at", ""),
                html_url=data.get("html_url", ""),
                cwe_id=cwe_id,
                tool_name=tool_name,
                category=self._determine_category(rule_id),
                dismissed_reason=dismissed_reason,
                dismissed_comment=dismissed_comment,
                metadata={
                    "updated_at": data.get("updated_at"),
                    "fixed_at": data.get("fixed_at"),
                    "dismissed_at": data.get("dismissed_at"),
                    "dismissed_by": data.get("dismissed_by", {}).get("login") if data.get("dismissed_by") else None,
                }
            )

        except Exception as e:
            logger.warning(f"Error parsing alert: {e}")
            return None

    def _extract_cwe_id(self, rule: dict[str, Any]) -> Optional[str]:
        """Extract CWE ID from rule tags."""
        tags = rule.get("tags", [])
        for tag in tags:
            if tag.startswith("external/cwe/cwe-"):
                return f"CWE-{tag.split('-')[-1]}"
        return None

    def _determine_category(self, rule_id: str) -> str:
        """Determine vulnerability category from rule ID."""
        rule_lower = rule_id.lower()

        # Injection vulnerabilities
        if any(x in rule_lower for x in ["sql", "command", "injection", "xss"]):
            return "injection"

        # Path traversal
        if any(x in rule_lower for x in ["path", "traversal", "file"]):
            return "path-traversal"

        # Cryptographic issues
        if any(x in rule_lower for x in ["crypto", "hash", "secret", "password"]):
            return "cryptography"

        # Authentication/Authorization
        if any(x in rule_lower for x in ["auth", "session", "token", "jwt"]):
            return "authentication"

        # Information disclosure
        if any(x in rule_lower for x in ["leak", "exposure", "disclosure"]):
            return "information-disclosure"

        # Resource management
        if any(x in rule_lower for x in ["resource", "memory", "dos", "loop"]):
            return "resource-management"

        return "security"


class AlertExporter:
    """Export alerts to various formats."""

    @staticmethod
    def export_json(alerts: list[CodeScanningAlert], output_path: Path) -> None:
        """Export alerts to JSON format."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_alerts": len(alerts),
            "alerts": [alert.to_dict() for alert in alerts]
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported {len(alerts)} alerts to JSON: {output_path}")

    @staticmethod
    def export_csv(alerts: list[CodeScanningAlert], output_path: Path) -> None:
        """Export alerts to CSV format."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not alerts:
            logger.warning("No alerts to export to CSV")
            return

        # Get all field names (excluding metadata for simplicity)
        fieldnames = [
            "alert_number", "rule_id", "severity", "state", "file_path",
            "line_start", "line_end", "description", "created_at",
            "html_url", "cwe_id", "tool_name", "category",
            "dismissed_reason", "dismissed_comment"
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for alert in alerts:
                row = {k: v for k, v in alert.to_dict().items() if k in fieldnames}
                writer.writerow(row)

        logger.info(f"Exported {len(alerts)} alerts to CSV: {output_path}")

    @staticmethod
    def export_markdown(alerts: list[CodeScanningAlert], output_path: Path) -> None:
        """Export alerts to Markdown format with summary statistics."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Calculate statistics
        total = len(alerts)
        by_severity = {}
        by_category = {}
        by_state = {}

        for alert in alerts:
            by_severity[alert.severity] = by_severity.get(alert.severity, 0) + 1
            by_category[alert.category] = by_category.get(alert.category, 0) + 1
            by_state[alert.state] = by_state.get(alert.state, 0) + 1

        # Generate markdown
        lines = [
            "# CodeQL Code Scanning Alerts",
            "",
            f"> **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"> **Total Alerts:** {total}",
            "",
            "## 📊 Summary Statistics",
            "",
            "### By Severity",
            "",
            "| Severity | Count | Percentage |",
            "|----------|-------|------------|",
        ]

        for severity in ["critical", "high", "medium", "low", "warning", "note"]:
            count = by_severity.get(severity, 0)
            pct = (count / total * 100) if total > 0 else 0
            lines.append(f"| {severity.title()} | {count} | {pct:.1f}% |")

        lines.extend([
            "",
            "### By Category",
            "",
            "| Category | Count | Percentage |",
            "|----------|-------|------------|",
        ])

        for category, count in sorted(by_category.items(), key=lambda x: -x[1]):
            pct = (count / total * 100) if total > 0 else 0
            lines.append(f"| {category} | {count} | {pct:.1f}% |")

        lines.extend([
            "",
            "### By State",
            "",
            "| State | Count | Percentage |",
            "|-------|-------|------------|",
        ])

        for state, count in sorted(by_state.items(), key=lambda x: -x[1]):
            pct = (count / total * 100) if total > 0 else 0
            lines.append(f"| {state.title()} | {count} | {pct:.1f}% |")

        lines.extend([
            "",
            "## 🔍 Alert Details",
            "",
            "| # | Severity | Rule | File | Line | State |",
            "|---|----------|------|------|------|-------|",
        ])

        # Sort by severity then alert number
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "warning": 4, "note": 5}
        sorted_alerts = sorted(
            alerts,
            key=lambda a: (severity_order.get(a.severity, 99), -a.alert_number)
        )

        for alert in sorted_alerts[:100]:  # Limit to first 100 for readability
            lines.append(
                f"| [{alert.alert_number}]({alert.html_url}) | "
                f"{alert.severity} | {alert.rule_id} | "
                f"`{alert.file_path}` | {alert.line_start} | "
                f"{alert.state} |"
            )

        if total > 100:
            lines.append(f"\n*Showing first 100 of {total} alerts. See JSON/CSV for complete data.*")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"Exported alert summary to Markdown: {output_path}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch CodeQL code scanning alerts from GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch all open alerts
  %(prog)s --owner Aries-Serpent --repo _codex_

  # Fetch only critical/high severity alerts
  %(prog)s --owner Aries-Serpent --repo _codex_ --severity high

  # Fetch first 10 pages only (for testing)
  %(prog)s --owner Aries-Serpent --repo _codex_ --max-pages 10

  # Export to specific directory
  %(prog)s --owner Aries-Serpent --repo _codex_ --output-dir /tmp/alerts
        """
    )

    parser.add_argument(
        "--owner",
        default="Aries-Serpent",
        help="Repository owner (default: Aries-Serpent)"
    )
    parser.add_argument(
        "--repo",
        default="_codex_",
        help="Repository name (default: _codex_)"
    )
    parser.add_argument(
        "--token",
        help="GitHub API token (default: GITHUB_TOKEN env var)"
    )
    parser.add_argument(
        "--state",
        default="open",
        choices=["open", "closed", "dismissed", "fixed"],
        help="Alert state to fetch (default: open)"
    )
    parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low"],
        help="Filter by severity level"
    )
    parser.add_argument(
        "--ref",
        help="Git reference (branch/tag) to filter by"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        help="Maximum number of pages to fetch (default: all)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".codex/security"),
        help="Output directory (default: .codex/security)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize fetcher
    try:
        fetcher = CodeQLAlertFetcher(
            owner=args.owner,
            repo=args.repo,
            token=args.token,
            max_pages=args.max_pages
        )
    except ImportError as e:
        logger.error(str(e))
        return 1

    # Fetch alerts
    logger.info("Starting alert fetch...")
    alerts = fetcher.fetch_all_alerts(
        state=args.state,
        severity=args.severity,
        ref=args.ref
    )

    if not alerts:
        logger.warning("No alerts found")
        return 0

    # Export to multiple formats
    exporter = AlertExporter()

    json_path = args.output_dir / "alert_inventory.json"
    exporter.export_json(alerts, json_path)

    csv_path = args.output_dir / "alert_inventory.csv"
    exporter.export_csv(alerts, csv_path)

    md_path = args.output_dir / "alert_summary.md"
    exporter.export_markdown(alerts, md_path)

    logger.info("✅ Alert fetch complete!")
    logger.info(f"📁 Output directory: {args.output_dir}")
    logger.info(f"📊 Total alerts: {len(alerts)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
