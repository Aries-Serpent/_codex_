#!/usr/bin/env python3
"""
fetch_codeql_alerts.py — Rate-limit-aware CodeQL alert fetcher.

Fetches all open CodeQL alerts via the GitHub code-scanning REST API using
CODEX_MASTER_KEY (which has security_events scope).  Produces four output
files consumed by the WEC codeql-alert-fetcher.yml workflow:

  .codex/artifacts/codeql_alerts/alerts_raw.json     — full API response
  .codex/artifacts/codeql_alerts/alerts_by_rule.md   — grouped by rule ID
  .codex/artifacts/codeql_alerts/alerts_fixable.md   — top-N actionable alerts
  .codex/artifacts/codeql_alerts/alerts_summary.json — machine-readable counts

Rate-limit safety
-----------------
- Checks X-RateLimit-Remaining on every response; sleeps when < MIN_REMAINING.
- Respects Retry-After / X-RateLimit-Reset headers.
- Configurable inter-page sleep via --page-sleep (default 1 s) to avoid
  secondary rate-limit (anti-abuse) triggers.
- Hard cap of --max-pages pages (default 10) to prevent runaway fetches.

Security note
-------------
All subprocess and os.path operations use explicit variables — never shell=True
or f-string-into-shell-command patterns.  The GH_TOKEN is injected via the
``Authorization`` HTTP header, never via shell expansion.

Usage (CLI)
-----------
  python scripts/ci/fetch_codeql_alerts.py \\
      --state open \\
      --tool CodeQL \\
      --page-sleep 1.5 \\
      --max-pages 10 \\
      --out-dir .codex/artifacts/codeql_alerts

  python scripts/ci/fetch_codeql_alerts.py --help
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.parse
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Import the shared rate-limit-aware HTTP helpers.  _gh_api.py lives in the
# same directory; we add that directory to sys.path so the import works whether
# the script is invoked directly or via subprocess from the workflow.
_here = Path(__file__).parent
if str(_here) not in sys.path:
    sys.path.insert(0, str(_here))

from _gh_api import (  # noqa: E402  (after sys.path manipulation)
    DEFAULT_MIN_REMAINING,
    DEFAULT_PAGE_SLEEP,
    DEFAULT_PER_PAGE,
    resolve_token,
)
from _gh_api import (
    api_get as _api_get_impl,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
log = logging.getLogger("fetch_codeql_alerts")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MAX_PAGES: int = 10       # hard cap — each page is up to 100 alerts
DEFAULT_STATE: str = "open"
DEFAULT_TOOL: str = "CodeQL"

REPO_OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "Aries-Serpent")
REPO_NAME_FULL = os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")
_repo_parts = REPO_NAME_FULL.split("/", 1)
REPO_NAME = _repo_parts[1] if len(_repo_parts) == 2 else "_codex_"

API_BASE = "https://api.github.com"


# ---------------------------------------------------------------------------
# Thin wrappers that keep the existing public call-sites unchanged
# ---------------------------------------------------------------------------

def _api_get(
    url: str,
    token: str,
    min_remaining: int,
    page_sleep: float,
) -> tuple[Any, dict[str, str]]:
    """Delegate to the shared rate-limit-aware helper in _gh_api.py."""
    return _api_get_impl(url, token, page_sleep=page_sleep, min_remaining=min_remaining)



# ---------------------------------------------------------------------------
# Fetcher
# ---------------------------------------------------------------------------


def fetch_alerts(
    *,
    state: str,
    tool_name: str,
    per_page: int,
    max_pages: int,
    page_sleep: float,
    min_remaining: int,
    token: str,
) -> list[dict[str, Any]]:
    """Paginate through all CodeQL alerts matching *state* and *tool_name*."""
    all_alerts: list[dict[str, Any]] = []
    page = 1

    while page <= max_pages:
        url = (
            f"{API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}"
            f"/code-scanning/alerts"
            f"?state={state}"
            f"&tool_name={urllib.parse.quote(tool_name)}"
            f"&per_page={per_page}"
            f"&page={page}"
        )
        log.info("Fetching page %d: %s", page, url)
        data, _headers = _api_get(url, token, min_remaining, page_sleep)

        if not isinstance(data, list):
            log.error("Unexpected API response type: %s", type(data))
            raise SystemExit(1)

        all_alerts.extend(data)
        log.info("Page %d: %d alerts (cumulative: %d)", page, len(data), len(all_alerts))

        if len(data) < per_page:
            log.info("Last page reached (got %d < per_page=%d).", len(data), per_page)
            break

        page += 1

    if page > max_pages:
        log.warning(
            "Reached max-pages cap (%d). There may be more alerts not fetched.",
            max_pages,
        )

    return all_alerts


# ---------------------------------------------------------------------------
# Report generators
# ---------------------------------------------------------------------------


def _rule_id(alert: dict[str, Any]) -> str:
    return alert.get("rule", {}).get("id", "unknown")


def _severity(alert: dict[str, Any]) -> str:
    return (
        alert.get("rule", {}).get("severity")
        or alert.get("rule", {}).get("security_severity_level")
        or "unknown"
    )


def _location(alert: dict[str, Any]) -> str:
    loc = alert.get("most_recent_instance", {}).get("location", {})
    path = loc.get("path", "?")
    start = loc.get("start_line", "?")
    return f"{path}:{start}"


def build_summary(alerts: list[dict[str, Any]]) -> dict[str, Any]:
    by_rule: dict[str, int] = defaultdict(int)
    by_severity: dict[str, int] = defaultdict(int)
    for a in alerts:
        by_rule[_rule_id(a)] += 1
        by_severity[_severity(a)] += 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(alerts),
        "by_rule": dict(sorted(by_rule.items(), key=lambda kv: -kv[1])),
        "by_severity": dict(sorted(by_severity.items(), key=lambda kv: -kv[1])),
        "repo": REPO_NAME_FULL,
    }


def build_by_rule_md(alerts: list[dict[str, Any]]) -> str:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for a in alerts:
        grouped[_rule_id(a)].append(a)

    lines = [
        "# CodeQL Alerts — Grouped by Rule",
        f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')} · {len(alerts)} open alerts_",
        "",
    ]
    for rule_id, rule_alerts in sorted(grouped.items(), key=lambda kv: -len(kv[1])):
        desc = rule_alerts[0].get("rule", {}).get("description", "")
        sev = _severity(rule_alerts[0])
        lines.append(f"## `{rule_id}` ({len(rule_alerts)} alerts) — severity: {sev}")
        lines.append(f"> {desc}")
        lines.append("")
        lines.append("| Row | File:Line | Alert# | State |")
        lines.append("|-----|-----------|--------|-------|")
        for row, a in enumerate(rule_alerts, 1):
            lines.append(
                f"| {row} "
                f"| `{_location(a)}` "
                f"| [{a.get('number', '?')}]({a.get('html_url', '#')}) "
                f"| {a.get('state', '?')} |"
            )
        lines.append("")

    return "\n".join(lines)


def build_fixable_md(alerts: list[dict[str, Any]], top_n: int = 20) -> str:
    """Produce a prioritised fix-list for the next Copilot session."""
    high_sev = {"critical", "high", "error"}
    prioritised = sorted(
        alerts,
        key=lambda a: (0 if _severity(a).lower() in high_sev else 1, _rule_id(a)),
    )[:top_n]

    lines = [
        "# CodeQL Alerts — Fixable (Priority List)",
        f"_Top {min(top_n, len(prioritised))} of {len(alerts)} open alerts_",
        f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}_",
        "",
        "| Alert# | Rule | Severity | File:Line | URL |",
        "|--------|------|----------|-----------|-----|",
    ]
    for a in prioritised:
        lines.append(
            f"| {a.get('number', '?')} "
            f"| `{_rule_id(a)}` "
            f"| {_severity(a)} "
            f"| `{_location(a)}` "
            f"| [view]({a.get('html_url', '#')}) |"
        )

    lines += [
        "",
        "## Suggested fix command for next session",
        "```bash",
        "# Dispatch the fetcher to refresh this list:",
        "# (check codeql-alert-fetcher.yml in WEC then push)",
        "# Then download artifact:  codeql-alerts-open-all-rules-<RUN_ID>",
        "```",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--state",
        default=DEFAULT_STATE,
        choices=["open", "dismissed", "fixed", "auto_dismissed"],
        help="Alert state filter (default: open)",
    )
    p.add_argument(
        "--tool",
        default=DEFAULT_TOOL,
        metavar="TOOL_NAME",
        help="Code-scanning tool name filter (default: CodeQL)",
    )
    p.add_argument(
        "--page-sleep",
        type=float,
        default=DEFAULT_PAGE_SLEEP,
        metavar="SECS",
        help="Seconds to sleep between paginated requests (default: 1.0)",
    )
    p.add_argument(
        "--max-pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        metavar="N",
        help="Hard cap on pages to fetch, 1–100 (default: 10)",
    )
    p.add_argument(
        "--min-remaining",
        type=int,
        default=DEFAULT_MIN_REMAINING,
        metavar="N",
        help="Pause when REST remaining drops below N (default: 20)",
    )
    p.add_argument(
        "--out-dir",
        default=".codex/artifacts/codeql_alerts",
        metavar="DIR",
        help="Output directory for report files",
    )
    p.add_argument(
        "--top-n",
        type=int,
        default=20,
        metavar="N",
        help="Number of prioritised alerts in fixable report (default: 20)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    # Clamp max-pages to a safe range
    if args.max_pages < 1:
        args.max_pages = 1
    elif args.max_pages > 100:
        args.max_pages = 100

    token = resolve_token()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    log.info(
        "Fetching %s CodeQL alerts (tool=%s, max_pages=%d, page_sleep=%.1fs)",
        args.state,
        args.tool,
        args.max_pages,
        args.page_sleep,
    )

    alerts = fetch_alerts(
        state=args.state,
        tool_name=args.tool,
        per_page=DEFAULT_PER_PAGE,
        max_pages=args.max_pages,
        page_sleep=args.page_sleep,
        min_remaining=args.min_remaining,
        token=token,
    )

    # Write raw JSON
    raw_path = out_dir / "alerts_raw.json"
    raw_path.write_text(json.dumps(alerts, indent=2), encoding="utf-8")
    log.info("Wrote %s (%d alerts)", raw_path, len(alerts))

    # Write summary JSON
    summary = build_summary(alerts)
    summary_path = out_dir / "alerts_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log.info("Wrote %s", summary_path)

    # Write grouped-by-rule Markdown
    by_rule_path = out_dir / "alerts_by_rule.md"
    by_rule_path.write_text(build_by_rule_md(alerts), encoding="utf-8")
    log.info("Wrote %s", by_rule_path)

    # Write fixable priority list
    fixable_path = out_dir / "alerts_fixable.md"
    fixable_path.write_text(build_fixable_md(alerts, top_n=args.top_n), encoding="utf-8")
    log.info("Wrote %s", fixable_path)

    # Print summary to stdout so CI log is informative
    print(f"\n{'='*60}")
    print(f"CodeQL Alert Fetch Complete — {args.state} alerts")
    print(f"{'='*60}")
    print(f"  Total alerts : {summary['total']}")
    print("  By rule:")
    for rule_id, count in summary["by_rule"].items():
        print(f"    {rule_id:<50} {count:>4}")
    print("  By severity:")
    for sev, count in summary["by_severity"].items():
        print(f"    {sev:<20} {count:>4}")
    print(f"  Output dir   : {out_dir.resolve()}")
    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
