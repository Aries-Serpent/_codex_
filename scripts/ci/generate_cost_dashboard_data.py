#!/usr/bin/env python3
"""
Generate cost-estimator dashboard data for GitHub Pages.

Queries the GitHub REST API for recent workflow runs, classifies each run
using the same cost-tier logic as cost_estimator.py, and writes a summary
JSON file to docs/ops/cost-data.json so the static dashboard page can
render current data without a backend.

Usage (called by pages-mkdocs.yml before `mkdocs build`):

    python scripts/ci/generate_cost_dashboard_data.py \\
        --owner Aries-Serpent \\
        --repo _codex_ \\
        --out docs/ops/cost-data.json

Requires GITHUB_TOKEN in the environment for authenticated API access
(5,000 req/hr vs 60/hr unauthenticated).
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

# Add parent directory to path for CI execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.ci._token_resolver import get_token


# ── Cost-tier constants (kept in sync with cost_estimator.py) ────────────────
MONTHLY_MINUTES_BUDGET = 3_000
TIER_GREEN_MAX = 30
TIER_YELLOW_MAX = 90

RUNNER_MULTIPLIERS: dict[str, float] = {
    "ubuntu-latest": 1.0,
    "ubuntu-latest-m": 2.0,
    "ubuntu-latest-l": 4.0,
    "ubuntu-latest-xl": 8.0,
    "windows-latest": 2.0,
    "macos-latest": 10.0,
    "macos-latest-xl": 10.0,
    "self-hosted": 0.0,
    "self-hosted-linux": 0.0,
}

# Gated workflows and their static configuration
GATED_WORKFLOWS: list[dict[str, Any]] = [
    {
        "name": "Build & Push Preview Image",
        "file": "build-preview-image.yml",
        "runner": "ubuntu-latest-m",
        "timeout": 30,
        "matrix_count": 2,
        "pushes_to_ghcr": True,
        "tier": "RED",
    },
    {
        "name": "Data Quality Suite",
        "file": "data-quality-suite.yml",
        "runner": "ubuntu-latest",
        "timeout": 60,
        "matrix_count": 3,
        "pushes_to_ghcr": False,
        "tier": "RED",
    },
    {
        "name": "Scheduled Archival",
        "file": "scheduled-archival.yml",
        "runner": "ubuntu-latest",
        "timeout": 60,
        "matrix_count": 3,
        "pushes_to_ghcr": False,
        "tier": "RED",
    },
    {
        "name": "Rust Swarm CI",
        "file": "rust_swarm_ci.yml",
        "runner": "ubuntu-latest",
        "timeout": 60,
        "matrix_count": 3,
        "pushes_to_ghcr": False,
        "tier": "RED",
    },
    {
        "name": "Docker Build & Push",
        "file": "docker-build-push.yml",
        "runner": "ubuntu-latest-m",
        "timeout": 30,
        "matrix_count": 2,
        "pushes_to_ghcr": True,
        "tier": "RED",
    },
    {
        "name": "Embedding Index Rebuild",
        "file": "embedding-index-rebuild.yml",
        "runner": "ubuntu-latest",
        "timeout": 15,
        "matrix_count": 1,
        "pushes_to_ghcr": False,
        "tier": "YELLOW",
    },
]


def _classify_tier(
    *,
    effective_minutes: float,
    pushes_to_ghcr: bool = False,
) -> str:
    if effective_minutes < TIER_GREEN_MAX and not pushes_to_ghcr:
        return "GREEN"
    if effective_minutes <= TIER_YELLOW_MAX and not pushes_to_ghcr:
        return "YELLOW"
    return "RED"


def _effective_minutes(
    timeout: int,
    runner: str,
    matrix_count: int = 1,
) -> float:
    multiplier = RUNNER_MULTIPLIERS.get(runner.lower().replace(" ", "-"), 1.0)
    return timeout * multiplier * matrix_count


def _github_api(
    path: str,
    token: str | None,
    *,
    per_page: int = 30,
) -> Any:
    url = f"https://api.github.com{path}?per_page={per_page}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            return json.loads(resp.read())
    except Exception as exc:  # noqa: BLE001
        print(f"⚠️  GitHub API error for {path}: {exc}", file=sys.stderr)
        return None


def _load_usage_log(log_path: Path) -> list[dict]:
    """Read .codex/logs/usage.ndjson if present."""
    if not log_path.exists():
        return []
    entries: list[dict] = []
    with log_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def _month_prefix() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m")


def build_data(
    owner: str,
    repo: str,
    token: str | None,
    usage_log_path: Path,
) -> dict:
    now = datetime.datetime.now(datetime.timezone.utc)
    month = _month_prefix()

    # ── Usage log entries (gitignored; only present in CI env) ──────────────
    log_entries = _load_usage_log(usage_log_path)
    month_log = [e for e in log_entries if e.get("ts", "").startswith(month)]
    log_minutes_used = sum(float(e.get("effective_minutes", 0)) for e in month_log)

    # ── Recent workflow runs from GitHub API ─────────────────────────────────
    runs_resp = _github_api(
        f"/repos/{owner}/{repo}/actions/runs",
        token,
        per_page=50,
    )
    api_runs: list[dict] = []
    if runs_resp and "workflow_runs" in runs_resp:
        for r in runs_resp["workflow_runs"][:50]:
            if r.get("status") != "completed":
                continue
            run_min = float(r.get("run_duration_ms", 0)) / 60_000
            runner = "ubuntu-latest"  # default; API doesn't expose runner directly
            eff_min = _effective_minutes(int(round(run_min)) or 5, runner, matrix_count=1)
            tier = _classify_tier(effective_minutes=eff_min)
            api_runs.append(
                {
                    "name": r.get("name", ""),
                    "conclusion": r.get("conclusion", ""),
                    "created_at": r.get("created_at", ""),
                    "run_number": r.get("run_number", 0),
                    "html_url": r.get("html_url", ""),
                    "effective_minutes": round(eff_min, 1),
                    "tier": tier,
                }
            )

    # ── Monthly minutes (best estimate) ─────────────────────────────────────
    this_month_runs = [r for r in api_runs if r.get("created_at", "").startswith(month)]
    api_minutes_used = sum(r["effective_minutes"] for r in this_month_runs)
    total_minutes_used = round(max(log_minutes_used, api_minutes_used), 1)
    pct_used = round(total_minutes_used / MONTHLY_MINUTES_BUDGET * 100, 1)

    # ── Tier counts this month ───────────────────────────────────────────────
    tier_counts: dict[str, int] = defaultdict(int)
    for r in this_month_runs:
        tier_counts[r["tier"]] += 1
    for entry in month_log:
        tier_counts[entry.get("tier", "GREEN")] += 1

    # ── Daily usage trend (last 30 days) ────────────────────────────────────
    daily: dict[str, float] = defaultdict(float)
    for r in api_runs:
        day = r["created_at"][:10]
        daily[day] += r["effective_minutes"]
    for entry in log_entries:
        day = entry.get("ts", "")[:10]
        if day:
            daily[day] += float(entry.get("effective_minutes", 0))
    # Keep last 30 calendar days
    cutoff = (now - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    trend = [{"date": k, "minutes": round(v, 1)} for k, v in sorted(daily.items()) if k >= cutoff]

    # ── Gated workflow static config ────────────────────────────────────────
    gated = []
    for wf in GATED_WORKFLOWS:
        eff = _effective_minutes(wf["timeout"], wf["runner"], wf["matrix_count"])
        gated.append(
            {
                "name": wf["name"],
                "file": wf["file"],
                "tier": wf["tier"],
                "effective_minutes": round(eff, 0),
                "runner": wf["runner"],
                "pushes_to_ghcr": wf["pushes_to_ghcr"],
            }
        )

    return {
        "generated_at": now.isoformat(),
        "month": month,
        "budget": {
            "total_minutes": MONTHLY_MINUTES_BUDGET,
            "used_minutes": total_minutes_used,
            "remaining_minutes": round(max(0, MONTHLY_MINUTES_BUDGET - total_minutes_used), 1),
            "pct_used": pct_used,
            "tier_thresholds": {
                "green_max": TIER_GREEN_MAX,
                "yellow_max": TIER_YELLOW_MAX,
            },
        },
        "tier_counts": {
            "GREEN": tier_counts.get("GREEN", 0),
            "YELLOW": tier_counts.get("YELLOW", 0),
            "RED": tier_counts.get("RED", 0),
        },
        "trend": trend,
        "gated_workflows": gated,
        "recent_runs": api_runs[:20],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate cost-dashboard data JSON for GitHub Pages"
    )
    parser.add_argument("--owner", default="Aries-Serpent")
    parser.add_argument("--repo", default="_codex_")
    parser.add_argument(
        "--out",
        default="docs/ops/cost-data.json",
        help="Output JSON path (default: docs/ops/cost-data.json)",
    )
    parser.add_argument(
        "--usage-log",
        default=".codex/logs/usage.ndjson",
        help="Path to NDJSON usage log (optional)",
    )
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or get_token(required_elevated=False)[0]
    if not token:
        print(
            "⚠️  No GITHUB_TOKEN found — API requests will be rate-limited (60/hr)",
            file=sys.stderr,
        )

    print(f"📊 Generating cost dashboard data for {args.owner}/{args.repo}…")
    data = build_data(
        owner=args.owner,
        repo=args.repo,
        token=token,
        usage_log_path=Path(args.usage_log),
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(
        f"✅ Wrote {out} ({len(data['recent_runs'])} recent runs, "
        f"month={data['month']}, used={data['budget']['used_minutes']} min)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
