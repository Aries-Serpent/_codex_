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
import csv
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
DEFAULT_EXPORT_DIR = ".codex/security/code_scanning_inventory"
LEGACY_EXPORT_DIR = ".codex/artifacts/codeql_alerts"

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

        if page >= max_pages:
            raise SystemExit(
                "Reached the configured max-pages cap without exhausting the repository inventory; "
                "refusing to silently publish a partial CodeQL snapshot."
            )

        page += 1

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


def _path(alert: dict[str, Any]) -> str:
    loc = alert.get("most_recent_instance", {}).get("location", {})
    return str(loc.get("path") or "unknown")


def _build_by_rule_csv(alerts: list[dict[str, Any]]) -> str:
    """Return a CSV table of rule totals and representative locations."""
    rows = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for alert in alerts:
        grouped[_rule_id(alert)].append(alert)
    for rule_id, rule_alerts in sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        sev = _severity(rule_alerts[0])
        rows.append({
            "rule_id": rule_id,
            "severity": sev,
            "count": len(rule_alerts),
            "description": rule_alerts[0].get("rule", {}).get("description", ""),
            "first_location": _location(rule_alerts[0]),
        })

    fieldnames = ["rule_id", "severity", "count", "description", "first_location"]
    out = [",".join(fieldnames)]
    for row in rows:
        values = [row.get("rule_id", ""), row.get("severity", ""), str(row.get("count", 0)), row.get("description", ""), row.get("first_location", "")]
        escaped = []
        for value in values:
            if any(ch in value for ch in [",", '"', "\n"]):
                escaped.append('"' + value.replace('"', '""') + '"')
            else:
                escaped.append(value)
        out.append(",".join(escaped))
    return "\n".join(out) + "\n"


def _build_severity_csv(summary: dict[str, Any]) -> str:
    by_sev = summary.get("by_severity", {})
    lines = ["severity,count"]
    for sev, count in sorted(by_sev.items(), key=lambda kv: kv[0].lower()):
        lines.append(f"{sev},{count}")
    return "\n".join(lines) + "\n"


def _build_path_csv(alerts: list[dict[str, Any]]) -> str:
    grouped: dict[str, int] = defaultdict(int)
    for alert in alerts:
        grouped[_path(alert)] += 1
    lines = ["path,count"]
    for path, count in sorted(grouped.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"{path},{count}")
    return "\n".join(lines) + "\n"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_manifest(out_dir: Path) -> None:
    manifest = {
        "schema_version": "1.0",
        "source_of_truth": "GitHub REST API /repos/{owner}/{repo}/code-scanning/alerts",
        "security_ui_role": "human validation only",
        "generated_at": _utc_stamp(),
        "files": [
            "api_inventory_raw.json",
            "api_inventory_summary.json",
            "api_inventory_by_rule.csv",
            "api_inventory_by_severity.csv",
            "api_inventory_by_path.csv",
            "api_inventory_fixable.md",
            "ui_validation_report.json",
            "delta_report.json",
            "manifest.json",
        ],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _write_validation_report(out_dir: Path, summary: dict[str, Any]) -> None:
    validation = {
        "generated_at": _utc_stamp(),
        "status": "not_validated" if summary.get("total") is None else "ok",
        "total_alerts": summary.get("total", 0),
        "by_severity": summary.get("by_severity", {}),
        "contract": {
            "source_of_truth": "GitHub REST API /repos/{owner}/{repo}/code-scanning/alerts",
            "requires_json_inventory": True,
            "requires_machine_readable_summary": True,
            "requires_csv_rollups": True,
        },
    }
    (out_dir / "ui_validation_report.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")


def _write_delta_report(out_dir: Path, summary: dict[str, Any]) -> None:
    delta = {
        "generated_at": _utc_stamp(),
        "total_alerts": summary.get("total", 0),
        "changes": {
            "count": 0,
            "direction": "baseline",
        },
        "source_of_truth": "GitHub REST API /repos/{owner}/{repo}/code-scanning/alerts",
    }
    (out_dir / "delta_report.json").write_text(json.dumps(delta, indent=2), encoding="utf-8")


def build_summary(alerts: list[dict[str, Any]], *, state: str | None = None) -> dict[str, Any]:
    by_rule: dict[str, int] = defaultdict(int)
    by_severity: dict[str, int] = defaultdict(int)
    by_tool: dict[str, int] = defaultdict(int)
    by_path: dict[str, int] = defaultdict(int)
    by_age_bucket: dict[str, int] = defaultdict(int)

    now = datetime.now(timezone.utc)
    for a in alerts:
        rule_id = _rule_id(a)
        severity = _severity(a)
        tool_name = str((a.get("tool") or {}).get("name") or a.get("tool_name") or "unknown")
        path = _path(a)
        created_at = a.get("created_at") or a.get("most_recent_instance", {}).get("timestamp")
        by_rule[rule_id] += 1
        by_severity[severity] += 1
        by_tool[tool_name] += 1
        by_path[path] += 1

        if created_at:
            try:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                age_days = (now - created).total_seconds() / 86400.0
                if age_days <= 1:
                    bucket = "0-1d"
                elif age_days <= 7:
                    bucket = "1-7d"
                elif age_days <= 30:
                    bucket = "7-30d"
                else:
                    bucket = "30+d"
                by_age_bucket[bucket] += 1
            except ValueError:
                by_age_bucket["unknown"] += 1
        else:
            by_age_bucket["unknown"] += 1

    return {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "state": state or DEFAULT_STATE,
        "repo": REPO_NAME_FULL,
        "total": len(alerts),
        "by_rule": dict(sorted(by_rule.items(), key=lambda kv: -kv[1])),
        "by_severity": dict(sorted(by_severity.items(), key=lambda kv: -kv[1])),
        "by_tool": dict(sorted(by_tool.items(), key=lambda kv: -kv[1])),
        "by_path": dict(sorted(by_path.items(), key=lambda kv: -kv[1])),
        "by_age_bucket": dict(sorted(by_age_bucket.items())),
    }


def _csv_rows_for_rule(alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for alert in alerts:
        rule_id = _rule_id(alert)
        entry = grouped.setdefault(
            rule_id,
            {"rule_id": rule_id, "count": 0, "severity": _severity(alert), "paths": set(), "alert_numbers": set()},
        )
        entry["count"] += 1
        entry["severity"] = _severity(alert)
        if _path(alert) != "unknown":
            entry["paths"].add(_path(alert))
        entry["alert_numbers"].add(str(alert.get("number", "?")))
    rows: list[dict[str, Any]] = []
    for rule_id, entry in sorted(grouped.items(), key=lambda kv: (-kv[1]["count"], kv[0])):
        rows.append(
            {
                "rule_id": rule_id,
                "count": entry["count"],
                "severity": entry["severity"],
                "path_count": len(entry["paths"]),
                "paths": "; ".join(sorted(entry["paths"])),
                "alert_numbers": "; ".join(sorted(entry["alert_numbers"])),
            }
        )
    return rows


def _csv_rows_for_path(alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, int | str]] = {}
    for alert in alerts:
        path = _path(alert)
        entry = grouped.setdefault(path, {"path": path, "critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0})
        sev = _severity(alert).lower()
        if sev in {"critical", "error"}:
            entry["critical"] = int(entry["critical"]) + 1
        elif sev in {"high", "warning"}:
            entry["high"] = int(entry["high"]) + 1
        elif sev in {"medium", "note"}:
            entry["medium"] = int(entry["medium"]) + 1
        elif sev in {"low"}:
            entry["low"] = int(entry["low"]) + 1
        else:
            entry["unknown"] = int(entry["unknown"]) + 1
    rows = []
    for _, entry in sorted(
        grouped.items(),
        key=lambda kv: (
            -(int(kv[1]["critical"]) + int(kv[1]["high"]) + int(kv[1]["medium"]) + int(kv[1]["low"])),
            str(kv[0]),
        ),
    ):
        rows.append(
            {
                "path": entry["path"],
                "critical": entry["critical"],
                "high": entry["high"],
                "medium": entry["medium"],
                "low": entry["low"],
                "unknown": entry["unknown"],
                "total": (
                    int(entry["critical"])
                    + int(entry["high"])
                    + int(entry["medium"])
                    + int(entry["low"])
                    + int(entry["unknown"])
                ),
            }
        )
    return rows


def _csv_rows_for_severity(alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = defaultdict(int)
    for alert in alerts:
        counts[_severity(alert)] += 1
    rows = [{"severity": severity, "count": count} for severity, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    return rows


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _write_inventory_bundle(alerts: list[dict[str, Any]], out_dir: Path, *, top_n: int = 20, state: str = DEFAULT_STATE) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary(alerts, state=state)

    raw_path = out_dir / "api_inventory_raw.json"
    raw_path.write_text(json.dumps(alerts, indent=2), encoding="utf-8")

    summary_path = out_dir / "api_inventory_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    _write_csv(
        out_dir / "api_inventory_by_rule.csv",
        ["rule_id", "count", "severity", "path_count", "paths", "alert_numbers"],
        _csv_rows_for_rule(alerts),
    )
    _write_csv(
        out_dir / "api_inventory_by_severity.csv",
        ["severity", "count"],
        _csv_rows_for_severity(alerts),
    )
    _write_csv(
        out_dir / "api_inventory_by_path.csv",
        ["path", "critical", "high", "medium", "low", "unknown", "total"],
        _csv_rows_for_path(alerts),
    )

    _write_manifest(out_dir)
    _write_validation_report(out_dir, summary)
    _write_delta_report(out_dir, summary)

    fixable_canonical = out_dir / "api_inventory_fixable.md"
    fixable_canonical.write_text(build_fixable_md(alerts, top_n=top_n, state=state), encoding="utf-8")

    by_rule_md = out_dir / "alerts_by_rule.md"
    by_rule_md.write_text(build_by_rule_md(alerts, state=state), encoding="utf-8")
    fixable_legacy = out_dir / "alerts_fixable.md"
    fixable_legacy.write_text(build_fixable_md(alerts, top_n=top_n, state=state), encoding="utf-8")

    legacy_names = {
        "alerts_raw.json": raw_path,
        "alerts_summary.json": summary_path,
        "alerts_by_rule.csv": out_dir / "api_inventory_by_rule.csv",
        "alerts_by_severity.csv": out_dir / "api_inventory_by_severity.csv",
        "alerts_by_path.csv": out_dir / "api_inventory_by_path.csv",
    }
    for legacy_name, source in legacy_names.items():
        target = out_dir / legacy_name
        if target != source:
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    return summary


def build_by_rule_md(alerts: list[dict[str, Any]], *, state: str = DEFAULT_STATE) -> str:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for a in alerts:
        grouped[_rule_id(a)].append(a)

    lines = [
        "# CodeQL Alerts — Grouped by Rule",
        f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')} · {len(alerts)} {state} alerts_",
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


def build_fixable_md(alerts: list[dict[str, Any]], top_n: int = 20, *, state: str = DEFAULT_STATE) -> str:
    """Produce a prioritised fix-list for the next Copilot session."""
    high_sev = {"critical", "high", "error"}
    prioritised = sorted(
        alerts,
        key=lambda a: (0 if _severity(a).lower() in high_sev else 1, _rule_id(a)),
    )[:top_n]

    lines = [
        "# CodeQL Alerts — Fixable (Priority List)",
        f"_Top {min(top_n, len(prioritised))} of {len(alerts)} {state} alerts_",
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
        "# Refresh the canonical inventory on the active workflow:",
        "# gh workflow run codeql-alert-inventory.yml --ref main",
        "# Then check the latest artifact named codeql-alert-inventory-<RUN_ID>",
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
        default=DEFAULT_EXPORT_DIR,
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

    summary = _write_inventory_bundle(alerts, out_dir, top_n=args.top_n, state=args.state)
    raw_path = out_dir / "api_inventory_raw.json"
    log.info("Wrote %s (%d alerts)", raw_path, len(alerts))
    summary_path = out_dir / "api_inventory_summary.json"
    log.info("Wrote %s", summary_path)
    by_rule_path = out_dir / "api_inventory_by_rule.csv"
    log.info("Wrote %s", by_rule_path)
    by_sev_path = out_dir / "api_inventory_by_severity.csv"
    log.info("Wrote %s", by_sev_path)
    by_path_path = out_dir / "api_inventory_by_path.csv"
    log.info("Wrote %s", by_path_path)
    fixable_path = out_dir / "api_inventory_fixable.md"
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
