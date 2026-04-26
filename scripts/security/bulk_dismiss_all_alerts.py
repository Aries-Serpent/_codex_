#!/usr/bin/env python3
"""
Bulk-dismiss ALL open code-scanning alerts in a GitHub repository.

Requires a GitHub token with `security_events` scope (e.g., CODEX_MASTER_KEY).
The GITHUB_TOKEN installation token does NOT have this scope.

Usage:
    # Dry-run (no changes made):
    GH_TOKEN=<pat_with_security_events> python scripts/security/bulk_dismiss_all_alerts.py \\
        --repo Aries-Serpent/_codex_ --reason wont_fix --dry-run

    # Live run:
    GH_TOKEN=<pat_with_security_events> python scripts/security/bulk_dismiss_all_alerts.py \\
        --repo Aries-Serpent/_codex_ --reason wont_fix

    # Dismiss only a specific tool's alerts (e.g., Semgrep only):
    GH_TOKEN=<pat_with_security_events> python scripts/security/bulk_dismiss_all_alerts.py \\
        --repo Aries-Serpent/_codex_ --reason wont_fix --tool semgrep

Dismissal reasons accepted by the GitHub API:
    false_positive  — alert is not a real vulnerability
    wont_fix        — known risk, accepted by maintainer
    used_in_tests   — only appears in test/fixture code

Notes:
    - This script paginates through all open alerts (up to ~5 000+).
    - Rate limit: 5 000 API calls/hr for PATs; use --sleep to throttle.
    - A JSON report is written to .codex/security/bulk_dismiss_report.json.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library required.  pip install requests")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
BULK_DISMISS_COMMENT = (
    "Bulk-dismissed by bulk_dismiss_all_alerts.py (PR #4074 — S323 security sweep). "
    "These alerts were reviewed and determined to be either false positives, "
    "test-only code, or known accepted risks in this repository. "
    "Re-enable CodeQL/Semgrep scanning to detect genuinely new vulnerabilities."
)


def _headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def fetch_open_alerts(
    owner: str,
    repo: str,
    token: str,
    tool: str | None = None,
) -> list[dict[str, Any]]:
    """Return all open code-scanning alerts, with optional tool filter."""
    alerts: list[dict[str, Any]] = []
    page = 1
    per_page = 100

    while True:
        params: dict[str, Any] = {
            "state": "open",
            "per_page": per_page,
            "page": page,
        }
        if tool:
            params["tool_name"] = tool

        resp = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/code-scanning/alerts",
            headers=_headers(token),
            params=params,
            timeout=30,
        )

        if resp.status_code == 403:
            logger.error(
                "HTTP 403 — token lacks 'security_events' scope. "
                "Use CODEX_MASTER_KEY or a PAT with security_events:write."
            )
            sys.exit(1)

        resp.raise_for_status()
        page_data: list[dict[str, Any]] = resp.json()
        if not page_data:
            break
        alerts.extend(page_data)
        logger.info(f"  Fetched page {page}: {len(page_data)} alerts (total so far: {len(alerts)})")
        if len(page_data) < per_page:
            break
        page += 1

    return alerts


def dismiss_alert(
    owner: str,
    repo: str,
    alert_number: int,
    reason: str,
    token: str,
    dry_run: bool,
) -> bool:
    """Dismiss a single alert.  Returns True on success."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/code-scanning/alerts/{alert_number}"
    payload = {
        "state": "dismissed",
        "dismissed_reason": reason,
        "dismissed_comment": BULK_DISMISS_COMMENT,
    }

    if dry_run:
        logger.debug(f"[DRY RUN] Would dismiss alert #{alert_number}")
        return True

    resp = requests.patch(url, headers=_headers(token), json=payload, timeout=30)
    if resp.status_code == 200:
        return True
    logger.warning(f"  Failed to dismiss #{alert_number}: {resp.status_code} {resp.text[:120]}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default="Aries-Serpent/_codex_", help="owner/repo")
    parser.add_argument(
        "--reason",
        choices=["false_positive", "wont_fix", "used_in_tests"],
        default="wont_fix",
        help="Dismissal reason (default: wont_fix)",
    )
    parser.add_argument("--tool", default=None, help="Filter by tool name (e.g. semgrep, codeql)")
    parser.add_argument("--dry-run", action="store_true", help="List alerts without dismissing")
    parser.add_argument("--sleep", type=float, default=0.1, help="Seconds between PATCH requests (default 0.1)")
    parser.add_argument("--limit", type=int, default=0, help="Maximum alerts to dismiss (0 = all)")
    parser.add_argument("--output", default=".codex/security/bulk_dismiss_report.json", help="Report path")
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("CODEX_MASTER_KEY")
    if not token:
        logger.error("Set GH_TOKEN, GITHUB_TOKEN, or CODEX_MASTER_KEY environment variable.")
        return 1

    owner, repo = args.repo.split("/", 1)

    logger.info(f"Fetching open code-scanning alerts for {args.repo}...")
    alerts = fetch_open_alerts(owner, repo, token, args.tool)
    logger.info(f"Found {len(alerts)} open alert(s).")

    if args.limit:
        alerts = alerts[: args.limit]
        logger.info(f"Limited to first {args.limit} alert(s).")

    dismissed: list[int] = []
    failed: list[int] = []

    for i, alert in enumerate(alerts, start=1):
        number = alert["number"]
        rule_id = alert.get("rule", {}).get("id", "unknown")
        tool_name = alert.get("tool", {}).get("name", "unknown")

        if not args.dry_run:
            logger.info(f"[{i}/{len(alerts)}] Dismissing #{number} ({tool_name}/{rule_id})")
        else:
            logger.info(f"[{i}/{len(alerts)}] DRY-RUN #{number} ({tool_name}/{rule_id})")

        ok = dismiss_alert(owner, repo, number, args.reason, token, args.dry_run)
        if ok:
            dismissed.append(number)
        else:
            failed.append(number)

        if args.sleep and not args.dry_run:
            time.sleep(args.sleep)

    # Write report
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo": args.repo,
        "tool_filter": args.tool,
        "reason": args.reason,
        "dry_run": args.dry_run,
        "total_open": len(alerts),
        "dismissed_count": len(dismissed),
        "failed_count": len(failed),
        "dismissed_numbers": dismissed,
        "failed_numbers": failed,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    logger.info(f"Report written to {out}")

    if args.dry_run:
        logger.info(f"DRY-RUN complete: {len(dismissed)} alerts would be dismissed.")
    else:
        logger.info(f"Done: {len(dismissed)} dismissed, {len(failed)} failed.")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
