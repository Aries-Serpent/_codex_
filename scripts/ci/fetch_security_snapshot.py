#!/usr/bin/env python3
"""
fetch_security_snapshot.py — Rate-limit-aware, cached GitHub security snapshot fetcher.

Fetches all security-relevant data for a repository using CODEX_MASTER_KEY
(security_events scope required) and writes agent-ready output files.

Supported --types
-----------------
  dependabot   Open Dependabot vulnerability alerts (paginated, cached)
  secrets      Open secret-scanning alerts (paginated, cached)
  policy       Community-health profile + security policy file content
  analyses     Recent code-scanning analysis runs + default-setup status
  autofix      Request GitHub Copilot Autofix for open CodeQL alerts
  context      Generate AGENT_SECURITY_CONTEXT.md from collected JSON files
  all          All of the above except autofix (use collect,autofix,prompt pipeline)

Rate-limit safety
-----------------
- Every HTTP call goes through _gh_api.py helpers which check
  X-RateLimit-Remaining on every response and sleep until X-RateLimit-Reset
  when the budget drops below --min-remaining.
- 429 / 403 responses are retried after Retry-After (default 60 s).
- Network errors are retried up to 3 times with exponential back-off.
- --page-sleep (default 0.8 s) is inserted between each paginated page.
- --autofix-inter-sleep (default 2.0 s) is inserted between each
  Copilot Autofix API call to avoid secondary rate limits.

Disk cache
----------
- --cache-dir (default ~/.cache/codex_gh_api) activates per-URL TTL caching.
- --cache-ttl (default 3600 s = 1 hour) controls how long cached responses
  are reused before re-fetching.
- Set CODEX_API_CACHE_DISABLED=1 to bypass the cache entirely.
- Cache writes are atomic (temp-file rename) to be safe under concurrent use.

Output files
------------
  dependabot/alerts_open.json      All open Dependabot alerts
  dependabot/alerts_critical.json  Critical + high severity only
  dependabot/summary.json          Counts by severity / ecosystem
  secrets/alerts_open.json         All open secret-scanning alerts
  secrets/alerts_active.json       Validity == active (confirmed) only
  secrets/summary.json             Counts by type / validity
  policy/community_profile.json    Community health API response
  policy/security_policy.json      Resolved policy file path + content
  analyses/recent.json             Last 100 code-scanning analysis runs
  analyses/default_setup.json      CodeQL default-setup status
  autofix/results.json             Per-alert autofix request results
  autofix/state.json               Persisted set of already-requested IDs
  AGENT_SECURITY_CONTEXT.md        Single-file summary for Copilot agent

Usage
-----
  python scripts/ci/fetch_security_snapshot.py --types all
  python scripts/ci/fetch_security_snapshot.py --types dependabot,secrets
  python scripts/ci/fetch_security_snapshot.py --types autofix --autofix-max 20
  python scripts/ci/fetch_security_snapshot.py --types context
"""

from __future__ import annotations

import argparse
import base64
import json
import logging
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure the scripts/ci directory is on sys.path so _gh_api can be imported
# whether this script is run directly or via subprocess.
_here = Path(__file__).parent
if str(_here) not in sys.path:
    sys.path.insert(0, str(_here))

from _gh_api import (  # noqa: E402
    DEFAULT_MIN_REMAINING,
    DEFAULT_PAGE_SLEEP,
    api_get_cached,
    api_post,
    paginate_cached,
    resolve_token,
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
log = logging.getLogger("fetch_security_snapshot")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_CACHE_TTL: int = 3600       # 1 hour
DEFAULT_MAX_PAGES: int = 10
DEFAULT_AUTOFIX_MAX: int = 20
DEFAULT_AUTOFIX_SEVERITIES = {"error", "critical", "high"}
DEFAULT_AUTOFIX_INTER_SLEEP: float = 2.0
DEFAULT_POLICY_PATHS = [".github/SECURITY.md", "SECURITY.md", "docs/SECURITY.md"]
FIX_HINTS: dict[str, str] = {
    "py/unused-import": "Remove import or add to `__all__`",
    "py/unused-global-variable": "Remove, use, or add to `__all__`",
    "py/ineffectual-statement": "Remove `...` after docstring in Protocol/ABC",
    "py/import-self": "Use `importlib.import_module()` at runtime",
    "py/shell-command-injection": "Replace `os.popen()` with `subprocess` + list args",
    "py/sql-injection": "Use parameterised queries",
    "py/path-injection": "Validate/sanitise user-supplied paths",
    "py/clear-text-storage-sensitive-data": "Hash or redact before storage",
    "py/code-injection": "Never pass user input to `eval()` or `exec()`",
    "py/bind-socket-all-network-interfaces": "Bind to 127.0.0.1 instead of 0.0.0.0",
    "py/incomplete-url-scheme-check": "Use an allowlist of accepted URL schemes",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _repo_info() -> tuple[str, str, str]:
    """Return (owner, name, full_name) from env."""
    full = os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")
    parts = full.split("/", 1)
    owner = parts[0] if len(parts) == 2 else "Aries-Serpent"
    name = parts[1] if len(parts) == 2 else full
    return owner, name, full


def _api_base(owner: str, name: str) -> str:
    return f"https://api.github.com/repos/{owner}/{name}"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    log.info("Wrote %s (%d bytes)", path, path.stat().st_size)


def _load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return default if default is not None else {}


# ---------------------------------------------------------------------------
# Stage: dependabot
# ---------------------------------------------------------------------------


def fetch_dependabot(
    out_dir: Path,
    token: str,
    *,
    cache_dir: Path | None,
    cache_ttl: int,
    max_pages: int,
    page_sleep: float,
    min_remaining: int,
) -> dict[str, Any]:
    owner, name, _ = _repo_info()
    base = f"{_api_base(owner, name)}/dependabot/alerts?state=open"

    log.info("Fetching Dependabot alerts …")
    alerts = paginate_cached(
        base,
        token,
        cache_dir=cache_dir,
        ttl_seconds=cache_ttl,
        max_pages=max_pages,
        page_sleep=page_sleep,
        min_remaining=min_remaining,
    )

    dep_out = out_dir / "dependabot"
    _write_json(dep_out / "alerts_open.json", alerts)

    urgent = [
        a for a in alerts
        if a.get("security_vulnerability", {}).get("severity") in ("critical", "high")
    ]
    _write_json(dep_out / "alerts_critical.json", urgent)

    sev = Counter(
        a.get("security_vulnerability", {}).get("severity", "unknown") for a in alerts
    )
    eco = Counter(
        a.get("dependency", {}).get("package", {}).get("ecosystem", "unknown")
        for a in alerts
    )
    summary = {
        "total": len(alerts),
        "critical_and_high": len(urgent),
        "by_severity": dict(sev.most_common()),
        "by_ecosystem": dict(eco.most_common()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(dep_out / "summary.json", summary)
    log.info("Dependabot: %d open (%d critical/high)", len(alerts), len(urgent))
    return summary


# ---------------------------------------------------------------------------
# Stage: secrets
# ---------------------------------------------------------------------------


def fetch_secrets(
    out_dir: Path,
    token: str,
    *,
    cache_dir: Path | None,
    cache_ttl: int,
    max_pages: int,
    page_sleep: float,
    min_remaining: int,
) -> dict[str, Any]:
    owner, name, _ = _repo_info()
    base = f"{_api_base(owner, name)}/secret-scanning/alerts?state=open"

    log.info("Fetching secret-scanning alerts …")
    alerts = paginate_cached(
        base,
        token,
        cache_dir=cache_dir,
        ttl_seconds=cache_ttl,
        max_pages=max_pages,
        page_sleep=page_sleep,
        min_remaining=min_remaining,
    )

    sec_out = out_dir / "secrets"
    _write_json(sec_out / "alerts_open.json", alerts)

    active = [a for a in alerts if a.get("validity") == "active"]
    _write_json(sec_out / "alerts_active.json", active)

    by_type = Counter(a.get("secret_type", "unknown") for a in alerts)
    by_validity = Counter(a.get("validity", "unknown") for a in alerts)
    summary = {
        "total": len(alerts),
        "active_confirmed": len(active),
        "by_type": dict(by_type.most_common(20)),
        "by_validity": dict(by_validity),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(sec_out / "summary.json", summary)
    log.info("Secrets: %d open (%d active)", len(alerts), len(active))
    return summary


# ---------------------------------------------------------------------------
# Stage: policy
# ---------------------------------------------------------------------------


def fetch_policy(
    out_dir: Path,
    token: str,
    *,
    cache_dir: Path | None,
    cache_ttl: int,
    page_sleep: float,
    min_remaining: int,
) -> dict[str, Any]:
    owner, name, _ = _repo_info()
    base = _api_base(owner, name)
    pol_out = out_dir / "policy"

    log.info("Fetching community health profile …")
    profile, _ = api_get_cached(
        f"{base}/community/profile",
        token,
        cache_dir=cache_dir,
        ttl_seconds=cache_ttl,
        page_sleep=page_sleep,
        min_remaining=min_remaining,
    )
    _write_json(pol_out / "community_profile.json", profile)

    # Try known security policy paths in order
    policy_doc: dict[str, Any] = {"error": "no security policy file found"}
    for candidate in DEFAULT_POLICY_PATHS:
        url = f"{base}/contents/{candidate}"
        log.info("Checking policy path: %s", candidate)
        try:
            data, _ = api_get_cached(
                url,
                token,
                cache_dir=cache_dir,
                ttl_seconds=cache_ttl,
                page_sleep=page_sleep * 0.5,
                min_remaining=min_remaining,
            )
        except SystemExit:
            continue
        if isinstance(data, dict) and data.get("type") == "file":
            raw_b64 = data.get("content", "").replace("\n", "")
            try:
                content = base64.b64decode(raw_b64).decode("utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                content = ""
            policy_doc = {
                "path": data.get("path"),
                "sha": data.get("sha"),
                "size": data.get("size"),
                "content": content[:8000],
            }
            log.info("Security policy found at: %s", candidate)
            break
    else:
        log.warning("No SECURITY.md found at standard paths: %s", DEFAULT_POLICY_PATHS)

    _write_json(pol_out / "security_policy.json", policy_doc)
    return {"health_percentage": profile.get("health_percentage", 0),
            "policy_found": "error" not in policy_doc}


# ---------------------------------------------------------------------------
# Stage: analyses
# ---------------------------------------------------------------------------


def fetch_analyses(
    out_dir: Path,
    token: str,
    *,
    cache_dir: Path | None,
    cache_ttl: int,
    page_sleep: float,
    min_remaining: int,
) -> dict[str, Any]:
    owner, name, _ = _repo_info()
    base = _api_base(owner, name)
    ana_out = out_dir / "analyses"

    log.info("Fetching code-scanning analyses metadata …")
    recent, _ = api_get_cached(
        f"{base}/code-scanning/analyses?per_page=100&page=1",
        token,
        cache_dir=cache_dir,
        ttl_seconds=cache_ttl,
        page_sleep=page_sleep,
        min_remaining=min_remaining,
    )
    if not isinstance(recent, list):
        recent = []
    _write_json(ana_out / "recent.json", recent)

    setup, _ = api_get_cached(
        f"{base}/code-scanning/default-setup",
        token,
        cache_dir=cache_dir,
        ttl_seconds=cache_ttl,
        page_sleep=page_sleep * 0.5,
        min_remaining=min_remaining,
    )
    _write_json(ana_out / "default_setup.json", setup)

    last = recent[0].get("created_at", "unknown") if recent else "none"
    state = setup.get("state", "unknown") if isinstance(setup, dict) else "unknown"
    log.info("Analyses: %d runs found, default-setup state=%s", len(recent), state)
    return {"total_analyses": len(recent), "last_analysis": last, "default_setup_state": state}


# ---------------------------------------------------------------------------
# Stage: autofix
# ---------------------------------------------------------------------------


def request_autofixes(
    out_dir: Path,
    token: str,
    *,
    autofix_max: int,
    autofix_severities: set[str],
    autofix_inter_sleep: float,
    min_remaining: int,
    codeql_alerts_path: Path | None = None,
    page_sleep: float = DEFAULT_PAGE_SLEEP,
    cache_dir: Path | None = None,
    cache_ttl: int = DEFAULT_CACHE_TTL,
) -> dict[str, Any]:
    """Request GitHub Copilot Autofix for open CodeQL alerts.

    Reads alert IDs either from *codeql_alerts_path* (pre-collected JSON) or
    fetches them live from the API.  Skips alerts that were already requested
    in a previous run (persisted in autofix/state.json).  Applies
    ``autofix_inter_sleep`` between each POST to avoid secondary rate limits.
    """
    owner, name, _ = _repo_info()
    base = _api_base(owner, name)
    fix_out = out_dir / "autofix"
    fix_out.mkdir(parents=True, exist_ok=True)

    # Load or initialise the persisted set of already-requested alert numbers
    state_path = fix_out / "state.json"
    already_requested: set[int] = set(
        _load_json(state_path, {}).get("requested_alert_numbers", [])
    )
    log.info("Autofix: %d alerts already requested in previous runs.", len(already_requested))

    # Source alert list
    alerts: list[dict[str, Any]] = []
    if codeql_alerts_path and codeql_alerts_path.exists():
        alerts = _load_json(codeql_alerts_path, [])
        log.info("Autofix: loaded %d alerts from %s", len(alerts), codeql_alerts_path)
    else:
        log.info("Autofix: fetching alert list from API …")
        alerts = paginate_cached(
            f"{base}/code-scanning/alerts?state=open&tool_name=CodeQL",
            token,
            cache_dir=cache_dir,
            ttl_seconds=cache_ttl,
            max_pages=10,
            page_sleep=page_sleep,
            min_remaining=min_remaining,
        )

    # Filter to target severities, skip already requested, cap at autofix_max
    def _alert_severity(a: dict[str, Any]) -> str:
        return (
            a.get("rule", {}).get("severity")
            or a.get("rule", {}).get("security_severity_level")
            or "unknown"
        )

    candidates = [
        a for a in alerts
        if _alert_severity(a).lower() in autofix_severities
        and int(a.get("number", 0)) not in already_requested
    ]
    log.info(
        "Autofix: %d candidates (severity in %s, not already requested)",
        len(candidates), sorted(autofix_severities),
    )
    to_fix = candidates[:autofix_max]
    log.info("Autofix: requesting fixes for %d/%d alerts (max=%d).", len(to_fix), len(candidates), autofix_max)

    results: list[dict[str, Any]] = []
    newly_requested: set[int] = set()

    for alert in to_fix:
        num = int(alert.get("number", 0))
        rule = alert.get("rule", {}).get("id", "unknown")
        loc = (
            alert.get("most_recent_instance", {})
            .get("location", {})
            .get("path", "unknown")
        )
        autofix_url = f"{base}/code-scanning/alerts/{num}/autofix"
        log.info("Requesting autofix for alert #%d (%s @ %s) …", num, rule, loc)

        resp, _ = api_post(
            autofix_url,
            token,
            payload=None,
            min_remaining=min_remaining,
            inter_call_sleep=autofix_inter_sleep,
        )

        status = resp.get("status", resp.get("error", "requested"))
        result = {
            "alert_number": num,
            "rule_id": rule,
            "location": loc,
            "autofix_status": status,
            "requested_at": datetime.now(timezone.utc).isoformat(),
        }
        results.append(result)

        if status not in ("not_found", "unsupported"):
            newly_requested.add(num)

        log.info("  → alert #%d autofix status: %s", num, status)

    # Persist updated state so future runs skip these alerts
    all_requested = sorted(already_requested | newly_requested)
    _write_json(state_path, {
        "requested_alert_numbers": all_requested,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    })
    _write_json(fix_out / "results.json", results)

    summary = {
        "total_candidates": len(candidates),
        "requested_this_run": len(newly_requested),
        "skipped_already_done": len(already_requested),
        "unsupported": sum(1 for r in results if r["autofix_status"] == "unsupported"),
        "results": results,
    }
    log.info(
        "Autofix: requested=%d  skipped=%d  unsupported=%d",
        len(newly_requested),
        len(already_requested),
        summary["unsupported"],
    )
    return summary


# ---------------------------------------------------------------------------
# Stage: context  (AGENT_SECURITY_CONTEXT.md)
# ---------------------------------------------------------------------------


def generate_context(out_dir: Path, top_n: int = 30) -> None:
    """Read collected JSON files from *out_dir* and write AGENT_SECURITY_CONTEXT.md."""
    codeql_summary = _load_json(out_dir / "codeql" / "alerts_summary.json")
    dep_summary    = _load_json(out_dir / "dependabot" / "summary.json")
    sec_summary    = _load_json(out_dir / "secrets" / "summary.json")
    community      = _load_json(out_dir / "policy" / "community_profile.json")
    policy_file    = _load_json(out_dir / "policy" / "security_policy.json")
    analyses       = _load_json(out_dir / "analyses" / "recent.json", [])
    default_setup  = _load_json(out_dir / "analyses" / "default_setup.json")
    autofix_res    = _load_json(out_dir / "autofix" / "results.json", [])

    repo_full = os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    run_url = (
        f"https://github.com/{repo_full}/actions/runs/{run_id}"
        if run_id != "local" else "N/A"
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

    codeql_total = codeql_summary.get("total", "?")
    dep_total    = dep_summary.get("total", "?")
    sec_total    = sec_summary.get("total", "?")
    sec_active   = sec_summary.get("active_confirmed", 0)
    health_pct   = community.get("health_percentage", "?")
    policy_path  = policy_file.get("path", None)
    policy_err   = policy_file.get("error")
    dep_by_sev   = dep_summary.get("by_severity", {})
    dep_critical = dep_by_sev.get("critical", 0)
    dep_high     = dep_by_sev.get("high", 0)
    codeql_by_rule = codeql_summary.get("by_rule", {})
    codeql_by_sev  = codeql_summary.get("by_severity", {})
    last_analysis  = analyses[0].get("created_at", "none") if analyses else "none"
    setup_state    = default_setup.get("state", "?") if isinstance(default_setup, dict) else "?"

    lines = [
        f"# Security Snapshot — `{repo_full}`",
        "",
        f"> **Generated:** {now}  ",
        f"> **Run:** [{run_id}]({run_url})  ",
        "> **Audience:** Copilot Cloud / Coding Agents",
        "",
        "---",
        "",
        "## 🚨 Priority Action Items",
        "",
    ]

    has_critical = False
    if isinstance(dep_critical, int) and dep_critical > 0:
        lines.append(f"- ❗ **CRITICAL** — {dep_critical} critical Dependabot vulnerability alert(s) requiring immediate upgrade")
        has_critical = True
    if isinstance(dep_high, int) and dep_high > 0:
        lines.append(f"- ⚠️ **HIGH** — {dep_high} high-severity Dependabot vulnerability alert(s)")
        has_critical = True
    if isinstance(sec_active, int) and sec_active > 0:
        lines.append(f"- ❗ **CRITICAL** — {sec_active} active/confirmed secret(s) detected — **revoke immediately**")
        has_critical = True
    codeql_crit = codeql_by_sev.get("critical", codeql_by_sev.get("error", 0))
    if isinstance(codeql_crit, int) and codeql_crit > 0:
        lines.append(f"- ⚠️ **HIGH** — {codeql_crit} critical/error CodeQL finding(s) to remediate")
        has_critical = True
    if policy_err:
        lines.append("- 📋 **INFO** — No security policy file found; create `.github/SECURITY.md`")
    if not has_critical:
        lines.append("- ✅ No critical/high priority items detected in this snapshot")

    if autofix_res:
        requested = [r for r in autofix_res if r.get("autofix_status") not in ("unsupported", "not_found")]
        lines += [
            "",
            "### 🤖 Copilot Autofix Status",
            "",
            f"Autofix was requested for **{len(requested)}/{len(autofix_res)}** eligible alerts this run.",
            f"Unsupported/not-found: {len(autofix_res) - len(requested)}.",
            "Check the GitHub Security tab for generated fix suggestions.",
        ]

    lines += [
        "",
        "---",
        "",
        "## Security Overview Counts",
        "",
        "| Area | Open Alerts | Notes |",
        "|------|-------------|-------|",
        f"| Dependabot (vulnerabilities) | {dep_total} | {dep_critical} critical, {dep_high} high |",
        f"| CodeQL (code scanning) | {codeql_total} | See rule breakdown below |",
        f"| Secret scanning | {sec_total} | {sec_active} active/confirmed |",
        f"| Community health | {health_pct}% | Policy: {policy_path or ('NOT FOUND' if policy_err else '?')} |",
        "",
        "---",
        "",
        "## CodeQL Alerts by Rule",
        "",
        "| Rule ID | Count | Recommended Fix |",
        "|---------|-------|-----------------|",
    ]

    for rule_id, count in sorted(codeql_by_rule.items(), key=lambda kv: -kv[1]):
        hint = FIX_HINTS.get(rule_id, "See [CodeQL docs](https://codeql.github.com/codeql-query-help/python/)")
        lines.append(f"| `{rule_id}` | {count} | {hint} |")

    lines += [
        "",
        "## CodeQL Alerts by Severity",
        "",
        "| Severity | Count |",
        "|----------|-------|",
    ]
    for sev, cnt in sorted(codeql_by_sev.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {sev} | {cnt} |")

    lines += [
        "",
        "## Dependabot by Severity & Ecosystem",
        "",
        "| Severity | Count |",
        "|----------|-------|",
    ]
    for sev, cnt in sorted(dep_by_sev.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {sev} | {cnt} |")

    lines += ["", "| Ecosystem | Count |", "|-----------|-------|"]
    for eco, cnt in sorted(dep_summary.get("by_ecosystem", {}).items(), key=lambda kv: -kv[1]):
        lines.append(f"| {eco} | {cnt} |")

    sec_by_type = sec_summary.get("by_type", {})
    if sec_by_type:
        lines += ["", "## Secret Scanning by Type", "", "| Secret Type | Count |", "|-------------|-------|"]
        for stype, cnt in list(sec_by_type.items())[:15]:
            lines.append(f"| `{stype}` | {cnt} |")

    lines += [
        "",
        "---",
        "",
        "## CodeQL Analysis Provenance",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Default setup state | `{setup_state}` |",
        f"| Last analysis run | {last_analysis} |",
        f"| Total recent analyses | {len(analyses) if isinstance(analyses, list) else '?'} |",
        "",
        "---",
        "",
        "## Artifact File Index",
        "",
        "| File | Contents |",
        "|------|---------|",
        "| `codeql/alerts_raw.json` | Full CodeQL alert JSON array |",
        "| `codeql/alerts_by_rule.md` | Alerts grouped by rule ID |",
        f"| `codeql/alerts_fixable.md` | Top-{top_n} prioritised fix list |",
        "| `codeql/alerts_summary.json` | Machine-readable counts |",
        "| `dependabot/alerts_open.json` | All open Dependabot alerts |",
        "| `dependabot/alerts_critical.json` | Critical + high only |",
        "| `dependabot/summary.json` | Counts by severity / ecosystem |",
        "| `secrets/alerts_open.json` | All open secret alerts |",
        "| `secrets/alerts_active.json` | Confirmed active secrets |",
        "| `secrets/summary.json` | Counts by type / validity |",
        "| `policy/community_profile.json` | Community health data |",
        "| `policy/security_policy.json` | Security policy file content |",
        "| `analyses/recent.json` | Last 100 code-scanning analyses |",
        "| `analyses/default_setup.json` | CodeQL default-setup status |",
        "| `autofix/results.json` | Copilot Autofix request results |",
        "| `autofix/state.json` | Persisted set of already-requested IDs |",
        "| `AGENT_SECURITY_CONTEXT.md` | This file |",
        "",
        "---",
        "",
        "## How to Use This Artifact (Copilot Agent)",
        "",
        "1. **Start here**: Read this file (`AGENT_SECURITY_CONTEXT.md`) for the full picture.",
        f"2. **CodeQL fixes**: Open `codeql/alerts_fixable.md` for the top-{top_n} prioritised fixes.",
        "3. **Dependabot**: Open `dependabot/alerts_critical.json` for packages to upgrade.",
        "4. **Secrets**: Open `secrets/alerts_active.json` — revoke all active secrets immediately.",
        "5. **Autofix**: Check GitHub Security tab for AI-generated fix suggestions from Copilot.",
        "6. **Rule reference**: For per-rule fix patterns, consult the GitHub Security tab "
            "and the CodeQL documentation at https://codeql.github.com/codeql-query-help/python/.",
    ]

    dest = out_dir / "AGENT_SECURITY_CONTEXT.md"
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.info("Wrote %s", dest)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Fetch GitHub security snapshot with rate-limit awareness and caching.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--types",
        default="all",
        help=(
            "Comma-separated list of stages to run: "
            "dependabot, secrets, policy, analyses, autofix, context, all "
            "(default: all)"
        ),
    )
    p.add_argument("--out-dir", default=".codex/artifacts/security_snapshot", metavar="DIR")
    p.add_argument(
        "--cache-dir",
        default=str(Path.home() / ".cache" / "codex_gh_api"),
        metavar="DIR",
        help="Disk cache directory for API responses (default: ~/.cache/codex_gh_api)",
    )
    p.add_argument(
        "--cache-ttl",
        type=int,
        default=DEFAULT_CACHE_TTL,
        metavar="SECS",
        help=f"Cache TTL in seconds (default: {DEFAULT_CACHE_TTL})",
    )
    p.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable disk cache (equivalent to CODEX_API_CACHE_DISABLED=1)",
    )
    p.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES, metavar="N")
    p.add_argument(
        "--page-sleep",
        type=float,
        default=DEFAULT_PAGE_SLEEP,
        metavar="SECS",
        help=f"Sleep between paginated requests (default: {DEFAULT_PAGE_SLEEP})",
    )
    p.add_argument(
        "--min-remaining",
        type=int,
        default=DEFAULT_MIN_REMAINING,
        metavar="N",
        help=f"Pause when REST budget drops below N (default: {DEFAULT_MIN_REMAINING})",
    )
    p.add_argument("--autofix-max", type=int, default=DEFAULT_AUTOFIX_MAX, metavar="N")
    p.add_argument(
        "--autofix-severities",
        default=",".join(sorted(DEFAULT_AUTOFIX_SEVERITIES)),
        metavar="LIST",
        help="Comma-separated severities to request autofix for (default: critical,error,high)",
    )
    p.add_argument(
        "--autofix-inter-sleep",
        type=float,
        default=DEFAULT_AUTOFIX_INTER_SLEEP,
        metavar="SECS",
        help=f"Sleep between Copilot Autofix API calls (default: {DEFAULT_AUTOFIX_INTER_SLEEP})",
    )
    p.add_argument(
        "--top-n",
        type=int,
        default=30,
        metavar="N",
        help="Top N alerts in AGENT_SECURITY_CONTEXT.md (default: 30)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.no_cache:
        os.environ["CODEX_API_CACHE_DISABLED"] = "1"

    token = resolve_token()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cache_dir: Path | None = None
    if os.environ.get("CODEX_API_CACHE_DISABLED", "0") != "1":
        cache_dir = Path(args.cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        log.info("Disk cache: %s  (TTL %ds)", cache_dir, args.cache_ttl)
    else:
        log.info("Disk cache: disabled")

    types_raw = args.types.lower().replace(" ", "")
    if types_raw == "all":
        types = {"dependabot", "secrets", "policy", "analyses", "context"}
    else:
        types = {t.strip() for t in types_raw.split(",")}

    common = dict(
        cache_dir=cache_dir,
        cache_ttl=args.cache_ttl,
        page_sleep=args.page_sleep,
        min_remaining=args.min_remaining,
    )

    summaries: dict[str, Any] = {}

    if "dependabot" in types:
        summaries["dependabot"] = fetch_dependabot(
            out_dir, token, max_pages=args.max_pages, **common
        )

    if "secrets" in types:
        summaries["secrets"] = fetch_secrets(
            out_dir, token, max_pages=args.max_pages, **common
        )

    if "policy" in types:
        summaries["policy"] = fetch_policy(out_dir, token, **common)

    if "analyses" in types:
        summaries["analyses"] = fetch_analyses(out_dir, token, **common)

    if "autofix" in types:
        codeql_path = out_dir / "codeql" / "alerts_raw.json"
        summaries["autofix"] = request_autofixes(
            out_dir,
            token,
            autofix_max=args.autofix_max,
            autofix_severities={s.strip() for s in args.autofix_severities.split(",")},
            autofix_inter_sleep=args.autofix_inter_sleep,
            min_remaining=args.min_remaining,
            codeql_alerts_path=codeql_path if codeql_path.exists() else None,
            page_sleep=args.page_sleep,
            cache_dir=cache_dir,
            cache_ttl=args.cache_ttl,
        )

    if "context" in types:
        generate_context(out_dir, top_n=args.top_n)

    # Print summary table
    print(f"\n{'='*62}")
    print(f"  Security Snapshot — {os.environ.get('GITHUB_REPOSITORY','?')}")
    print(f"{'='*62}")
    for stage, summary in summaries.items():
        print(f"  {stage}:")
        for k, v in summary.items():
            if k not in ("results", "generated_at"):
                print(f"    {k:<30} {v}")
    print(f"  Output dir : {out_dir.resolve()}")
    print(f"{'='*62}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
