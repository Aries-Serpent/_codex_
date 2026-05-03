#!/usr/bin/env python3
"""
Close CodeQL Code Scanning Alerts via GitHub API

This script closes resolved code scanning alerts via the GitHub API,
adding appropriate comments and tracking closures.

Author: mbaetiong
Created: 2026-01-26
Part of: CodeQL Alert Resolution Planset
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

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


class AlertCloser:
    """Close CodeQL code scanning alerts via GitHub API."""

    DISMISSAL_REASONS = {
        "fixed": "A fix has been deployed to address this vulnerability",
        "false_positive": "This alert is a false positive",
        "wont_fix": "This vulnerability will not be fixed",
        "used_in_tests": "This is test code and not a real vulnerability",
    }

    def __init__(
        self,
        owner: str,
        repo: str,
        token: Optional[str] = None,
        dry_run: bool = False,
    ):
        """
        Initialize the alert closer.

        Args:
            owner: Repository owner (e.g., "Aries-Serpent")
            repo: Repository name (e.g., "_codex_")
            token: GitHub API token (defaults to GITHUB_TOKEN env var)
            dry_run: If True, don't actually close alerts (just simulate)
        """
        if not HAS_REQUESTS:
            raise ImportError("requests library is required. Install with: pip install requests")

        self.owner = owner
        self.repo = repo
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.dry_run = dry_run
        # nosemgrep: url-substring-check - GitHub API base for code scanning automation
        self.base_url = "https://api.github.com"
        self.session = requests.Session()

        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            })
        else:
            raise ValueError("GitHub token is required to close alerts")

    def close_alert(
        self,
        alert_number: int,
        reason: str,
        comment: str,
        pr_number: Optional[int] = None,
        commit_sha: Optional[str] = None,
    ) -> bool:
        """
        Close a code scanning alert.

        Args:
            alert_number: The alert number to close
            reason: Dismissal reason ("fixed", "false_positive", "wont_fix", "used_in_tests")
            comment: Detailed comment explaining the closure
            pr_number: Optional PR number that fixed the issue
            commit_sha: Optional commit SHA that fixed the issue

        Returns:
            True if successful, False otherwise
        """
        if reason not in self.DISMISSAL_REASONS:
            logger.error(f"Invalid dismissal reason: {reason}")
            logger.error(f"Valid reasons: {', '.join(self.DISMISSAL_REASONS.keys())}")
            return False

        # Build the comment with additional context
        full_comment = self._build_comment(comment, pr_number, commit_sha)

        # Prepare API request
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/code-scanning/alerts/{alert_number}"

        payload = {
            "state": "dismissed",
            "dismissed_reason": reason,
            "dismissed_comment": full_comment,
        }

        if self.dry_run:
            logger.info(f"[DRY RUN] Would close alert #{alert_number}")
            logger.info(f"  Reason: {reason}")
            logger.info(f"  Comment: {full_comment}")
            return True

        try:
            response = self.session.patch(url, json=payload, timeout=30)

            if response.status_code == 200:
                logger.info(f"✅ Successfully closed alert #{alert_number}")
                return True
            if response.status_code == 404:
                logger.error(f"❌ Alert #{alert_number} not found")
                return False
            if response.status_code == 403:
                logger.error("❌ Insufficient permissions to close alerts")
                return False
            logger.error(f"❌ Failed to close alert: {response.status_code} - {response.text}")
            return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error: {e}")
            return False

    def _build_comment(
        self,
        comment: str,
        pr_number: Optional[int] = None,
        commit_sha: Optional[str] = None,
    ) -> str:
        """Build a complete comment with links and metadata."""
        lines = [comment]

        if pr_number:
            pr_url = f"https://github.com/{self.owner}/{self.repo}/pull/{pr_number}"
            lines.append(f"\nFixed in PR: #{pr_number} ({pr_url})")

        if commit_sha:
            commit_url = f"https://github.com/{self.owner}/{self.repo}/commit/{commit_sha}"
            lines.append(f"Commit: {commit_sha[:7]} ({commit_url})")

        lines.append(f"\nClosed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

        return "\n".join(lines)

    def close_alerts_batch(
        self,
        alert_numbers: list[int],
        reason: str,
        comment_template: str,
        pr_number: Optional[int] = None,
        commit_sha: Optional[str] = None,
    ) -> dict[int, bool]:
        """
        Close multiple alerts with the same reason.

        Args:
            alert_numbers: List of alert numbers to close
            reason: Dismissal reason
            comment_template: Comment template (can include {alert_number})
            pr_number: Optional PR number
            commit_sha: Optional commit SHA

        Returns:
            Dictionary mapping alert numbers to success status
        """
        results = {}

        for alert_number in alert_numbers:
            comment = comment_template.format(alert_number=alert_number)
            success = self.close_alert(
                alert_number=alert_number,
                reason=reason,
                comment=comment,
                pr_number=pr_number,
                commit_sha=commit_sha,
            )
            results[alert_number] = success

        # Log summary
        successful = sum(1 for v in results.values() if v)
        logger.info(f"\n📊 Batch closure summary: {successful}/{len(alert_numbers)} successful")

        return results

    def log_closure(
        self,
        alert_number: int,
        reason: str,
        comment: str,
        log_file: Path,
    ) -> None:
        """Log alert closure to a tracking file."""
        log_file.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "alert_number": alert_number,
            "closed_at": datetime.utcnow().isoformat() + "Z",
            "reason": reason,
            "comment": comment,
            "repository": f"{self.owner}/{self.repo}",
        }

        # Append to JSONL file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Close CodeQL code scanning alerts via GitHub API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Close a single alert as fixed
  %(prog)s --alert 123 --reason fixed --comment "Fixed SQL injection" --pr 456

  # Close multiple alerts
  %(prog)s --alerts 123,124,125 --reason fixed --comment "Fixed in batch PR"

  # Mark as false positive
  %(prog)s --alert 789 --reason false_positive --comment "Test code only"

  # Dry run (don't actually close)
  %(prog)s --alert 123 --reason fixed --comment "Test" --dry-run

Dismissal reasons:
  - fixed: A fix has been deployed
  - false_positive: This alert is a false positive
  - wont_fix: This vulnerability will not be fixed
  - used_in_tests: This is test code
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

    # Alert specification
    alert_group = parser.add_mutually_exclusive_group(required=True)
    alert_group.add_argument(
        "--alert",
        type=int,
        help="Single alert number to close"
    )
    alert_group.add_argument(
        "--alerts",
        help="Comma-separated list of alert numbers (e.g., 123,124,125)"
    )
    alert_group.add_argument(
        "--alerts-file",
        type=Path,
        help="File containing alert numbers (one per line)"
    )

    # Closure details
    parser.add_argument(
        "--reason",
        required=True,
        choices=["fixed", "false_positive", "wont_fix", "used_in_tests"],
        help="Dismissal reason"
    )
    parser.add_argument(
        "--comment",
        required=True,
        help="Comment explaining the closure"
    )
    parser.add_argument(
        "--pr",
        type=int,
        help="PR number that fixed the issue"
    )
    parser.add_argument(
        "--commit",
        help="Commit SHA that fixed the issue"
    )

    # Options
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path(".codex/security/alert_closures.jsonl"),
        help="Log file for tracking closures (default: .codex/security/alert_closures.jsonl)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate closure without actually closing alerts"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Parse alert numbers
    alert_numbers = []
    if args.alert:
        alert_numbers = [args.alert]
    elif args.alerts:
        try:
            alert_numbers = [int(n.strip()) for n in args.alerts.split(",")]
        except ValueError:
            logger.error("Invalid alert numbers format. Use comma-separated integers.")
            return 1
    elif args.alerts_file:
        if not args.alerts_file.exists():
            logger.error(f"Alerts file not found: {args.alerts_file}")
            return 1
        with open(args.alerts_file) as f:
            alert_numbers = [int(line.strip()) for line in f if line.strip().isdigit()]

    if not alert_numbers:
        logger.error("No valid alert numbers provided")
        return 1

    logger.info(f"Processing {len(alert_numbers)} alert(s)")

    # Initialize closer
    try:
        closer = AlertCloser(
            owner=args.owner,
            repo=args.repo,
            token=args.token,
            dry_run=args.dry_run
        )
    except (ImportError, ValueError) as e:
        logger.error(str(e))
        return 1

    # Close alerts
    if len(alert_numbers) == 1:
        success = closer.close_alert(
            alert_number=alert_numbers[0],
            reason=args.reason,
            comment=args.comment,
            pr_number=args.pr,
            commit_sha=args.commit,
        )

        if success and not args.dry_run:
            closer.log_closure(
                alert_number=alert_numbers[0],
                reason=args.reason,
                comment=args.comment,
                log_file=args.log_file,
            )

        return 0 if success else 1
    results = closer.close_alerts_batch(
        alert_numbers=alert_numbers,
        reason=args.reason,
        comment_template=args.comment,
        pr_number=args.pr,
        commit_sha=args.commit,
    )

    # Log all successful closures
    if not args.dry_run:
        for alert_number, success in results.items():
            if success:
                closer.log_closure(
                    alert_number=alert_number,
                    reason=args.reason,
                    comment=args.comment,
                    log_file=args.log_file,
                )

    # Return 0 if all succeeded, 1 if any failed
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
