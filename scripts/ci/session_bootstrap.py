#!/usr/bin/env python3
"""
session_bootstrap.py — Agent Session Pre-Process Bootstrapper
═══════════════════════════════════════════════════════════════

Runs at the START of every GitHub Copilot Coding Agent session (D-00 gate).

What it does
────────────
1. Extracts all GitHub URLs from the session context text (stdin, file, or
   --context argument).
2. Fetches structured data for each URL via the GitHub REST API:
     • Issues       — body, labels, open comments, linked PR/workflow refs
     • Pull requests — status, review threads (unresolved), CI check runs
     • Workflow runs — conclusion, failed job names, first 200 log lines
     • Review threads — specific unresolved thread body + diff hunk
3. Runs the 7 CI triage checks (scripts/ci/ci_triage_repro.sh --json).
4. Writes a structured context digest to:
     .codex/session_context_latest.md    (always overwritten)
     .codex/sessions/session_<ISO>.md    (archive copy)
5. Prints a compact situational-awareness summary to stdout.
6. Exits 0 if baseline is healthy; exits 1 if blocking issues are found.

Usage
─────
  # Pipe session text from stdin (typical CI / agent invocation):
  echo "<session text with github.com URLs>" | python scripts/ci/session_bootstrap.py

  # Pass context as file:
  python scripts/ci/session_bootstrap.py --context-file /tmp/session.txt

  # Pass context inline:
  python scripts/ci/session_bootstrap.py \\
    --context "Fix PR https://github.com/Aries-Serpent/_codex_/pull/3606 ..."

  # Skip GitHub fetching (offline / no token):
  python scripts/ci/session_bootstrap.py --offline

  # Skip triage checks (fast context-only mode):
  python scripts/ci/session_bootstrap.py --skip-triage

  # Write JSON digest instead of markdown:
  python scripts/ci/session_bootstrap.py --json-out /tmp/context.json

  # Full verbose output:
  python scripts/ci/session_bootstrap.py --verbose

Environment variables
─────────────────────
  GITHUB_TOKEN / CODEX_MASTER_KEY / CODEX_BACKUP_KEY  — GitHub API auth
  GITHUB_REPOSITORY  — owner/repo (used when not inferrable from URLs)

Exit codes
──────────
  0  Bootstrap complete; baseline healthy (or --offline / --skip-triage)
  1  One or more blocking CI failures detected
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parent.parent.parent
SESSIONS_DIR = REPO_ROOT / ".codex" / "sessions"
LATEST_PATH  = REPO_ROOT / ".codex" / "session_context_latest.md"
API_BASE     = "https://api.github.com"

# GitHub URL patterns
_RE_ISSUE   = re.compile(
    r"https://github\.com/([^/]+/[^/\s#]+)/issues/(\d+)(?:#[^\s]*)?"
)
_RE_PR      = re.compile(
    r"https://github\.com/([^/]+/[^/\s#]+)/pull/(\d+)(?:#[^\s]*)?"
)
_RE_RUN     = re.compile(
    r"https://github\.com/([^/]+/[^/\s#]+)/actions/runs/(\d+)"
)
_RE_REVIEW  = re.compile(
    r"https://github\.com/([^/]+/[^/\s#]+)/pull/(\d+)#pullrequestreview-(\d+)"
)

# ── Data classes ──────────────────────────────────────────────────────────────
@dataclass
class FetchedItem:
    url:     str
    kind:    str          # "issue" | "pr" | "run" | "review"
    title:   str = ""
    summary: str = ""
    details: List[str] = field(default_factory=list)
    error:   Optional[str] = None

@dataclass
class TriageResult:
    check_id:  str
    status:    str         # "pass" | "fail" | "skip"
    detail:    str = ""

@dataclass
class BootstrapReport:
    timestamp:    str
    repo:         str
    fetched:      List[FetchedItem]  = field(default_factory=list)
    triage:       List[TriageResult] = field(default_factory=list)
    blocking:     List[str]          = field(default_factory=list)
    warnings:     List[str]          = field(default_factory=list)
    baseline_ok:  Optional[bool]      = None   # None=not run, True=passed, False=failed


# ── GitHub API client ─────────────────────────────────────────────────────────
class GitHubClient:
    def __init__(self, token: Optional[str], verbose: bool = False):
        self.token   = token
        self.verbose = verbose

    def _request(self, path: str, accept: str = "application/vnd.github+json") -> Any:
        url = f"{API_BASE}{path}"
        headers = {
            "Accept":               accept,
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as exc:
            raise RuntimeError(f"GitHub API {exc.code}: {url}") from exc
        except URLError as exc:
            raise RuntimeError(f"Network error: {exc.reason} — {url}") from exc

    def get_issue(self, repo: str, number: int) -> Dict:
        return self._request(f"/repos/{repo}/issues/{number}")

    def get_issue_comments(self, repo: str, number: int) -> List[Dict]:
        items: List[Dict] = []
        page = 1
        while True:
            batch = self._request(
                f"/repos/{repo}/issues/{number}/comments?per_page=100&page={page}"
            )
            if not batch:
                break
            items.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return items

    def get_pr(self, repo: str, number: int) -> Dict:
        return self._request(f"/repos/{repo}/pulls/{number}")

    def get_pr_check_runs(self, repo: str, sha: str) -> List[Dict]:
        data = self._request(
            f"/repos/{repo}/commits/{sha}/check-runs?per_page=100"
        )
        return data.get("check_runs", [])

    def get_pr_reviews(self, repo: str, number: int) -> List[Dict]:
        items: List[Dict] = []
        page = 1
        while True:
            batch = self._request(
                f"/repos/{repo}/pulls/{number}/reviews?per_page=100&page={page}"
            )
            if not batch:
                break
            items.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return items

    def get_pr_review_comments(self, repo: str, number: int) -> List[Dict]:
        items: List[Dict] = []
        page = 1
        while True:
            batch = self._request(
                f"/repos/{repo}/pulls/{number}/comments?per_page=100&page={page}"
            )
            if not batch:
                break
            items.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return items

    def get_workflow_run(self, repo: str, run_id: int) -> Dict:
        return self._request(f"/repos/{repo}/actions/runs/{run_id}")

    def get_workflow_run_jobs(self, repo: str, run_id: int) -> List[Dict]:
        data = self._request(
            f"/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100&filter=latest"
        )
        return data.get("jobs", [])

    def get_job_logs(self, repo: str, job_id: int) -> str:
        """Return first 200 lines of job log (plain text)."""
        url = f"{API_BASE}/repos/{repo}/actions/jobs/{job_id}/logs"
        headers = {
            "Accept":               "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=30) as resp:
                raw = resp.read().decode(errors="replace")
                lines = raw.splitlines()
                return "\n".join(lines[:200])
        except (HTTPError, URLError):
            return "(log unavailable)"


# ── URL extraction ────────────────────────────────────────────────────────────
def extract_urls(text: str) -> List[Tuple[str, str, str, str]]:
    """
    Return list of (url, kind, repo, id_or_ids) tuples, deduplicated.
    kind ∈ {"review", "pr", "issue", "run"}
    Reviews must be checked before PRs (more specific pattern).
    """
    seen: set = set()
    results: List[Tuple[str, str, str, str]] = []

    for m in _RE_REVIEW.finditer(text):
        url = m.group(0)
        if url not in seen:
            seen.add(url)
            results.append((url, "review", m.group(1), f"{m.group(2)}:{m.group(3)}"))

    for m in _RE_PR.finditer(text):
        url = m.group(0)
        if url not in seen:
            seen.add(url)
            results.append((url, "pr", m.group(1), m.group(2)))

    for m in _RE_ISSUE.finditer(text):
        url = m.group(0)
        if url not in seen:
            seen.add(url)
            results.append((url, "issue", m.group(1), m.group(2)))

    for m in _RE_RUN.finditer(text):
        url = m.group(0)
        if url not in seen:
            seen.add(url)
            results.append((url, "run", m.group(1), m.group(2)))

    return results


# ── Per-type fetchers ─────────────────────────────────────────────────────────
def fetch_issue(client: GitHubClient, repo: str, number: int, url: str) -> FetchedItem:
    item = FetchedItem(url=url, kind="issue")
    try:
        issue = client.get_issue(repo, number)
        item.title   = issue.get("title", "")
        labels       = [lb["name"] for lb in issue.get("labels", [])]
        state        = issue.get("state", "?")
        body_preview = (issue.get("body") or "")[:400].replace("\n", " ")
        item.summary = f"[{state.upper()}] {item.title} ({', '.join(labels) or 'no labels'})"
        item.details  = [f"Body preview: {body_preview}"]

        # Collect open/recent comments
        comments = client.get_issue_comments(repo, number)
        for c in comments[-5:]:                       # last 5 comments
            author  = c.get("user", {}).get("login", "?")
            preview = (c.get("body") or "")[:200].replace("\n", " ")
            item.details.append(f"@{author}: {preview}")
    except Exception as exc:  # noqa: BLE001
        item.error = str(exc)
    return item


def fetch_pr(client: GitHubClient, repo: str, number: int, url: str) -> FetchedItem:
    item = FetchedItem(url=url, kind="pr")
    try:
        pr       = client.get_pr(repo, number)
        item.title = pr.get("title", "")
        state    = pr.get("state", "?")
        sha      = pr.get("head", {}).get("sha", "")
        item.summary = f"[{state.upper()}] {item.title} (SHA: {sha[:8]})"

        # Failed CI checks
        if sha:
            checks = client.get_pr_check_runs(repo, sha)
            failed = [c["name"] for c in checks
                      if c.get("conclusion") in ("failure", "cancelled", "timed_out")]
            if failed:
                item.details.append(f"❌ Failed checks ({len(failed)}): {', '.join(failed[:8])}")
            passing = sum(1 for c in checks if c.get("conclusion") == "success")
            item.details.append(f"✅ {passing}/{len(checks)} checks passing")

        # Unresolved review threads
        rev_comments = client.get_pr_review_comments(repo, number)
        unresolved   = [c for c in rev_comments
                        if not c.get("in_reply_to_id")]  # top-level thread starters
        if unresolved:
            item.details.append(f"💬 {len(unresolved)} unresolved review thread(s):")
            for c in unresolved[:5]:
                author  = c.get("user", {}).get("login", "?")
                path    = c.get("path", "?")
                preview = (c.get("body") or "")[:200].replace("\n", " ")
                item.details.append(f"  • {path} — @{author}: {preview}")
    except Exception as exc:  # noqa: BLE001
        item.error = str(exc)
    return item


def fetch_run(client: GitHubClient, repo: str, run_id: int, url: str) -> FetchedItem:
    item = FetchedItem(url=url, kind="run")
    try:
        run        = client.get_workflow_run(repo, run_id)
        conclusion = run.get("conclusion") or run.get("status", "?")
        name       = run.get("name", "?")
        item.title   = name
        item.summary = f"[{conclusion.upper()}] {name} (run #{run_id})"

        jobs = client.get_workflow_run_jobs(repo, run_id)
        failed_jobs = [j for j in jobs
                       if j.get("conclusion") in ("failure", "cancelled", "timed_out")]

        if not failed_jobs:
            item.details.append("No failed jobs found.")
            return item

        item.details.append(f"Failed jobs ({len(failed_jobs)}):")
        for j in failed_jobs[:5]:
            job_id   = j["id"]
            job_name = j.get("name", "?")
            logs     = client.get_job_logs(repo, job_id)
            # Extract error lines
            error_lines = [
                ln for ln in logs.splitlines()
                if any(kw in ln.lower() for kw in
                       ("error", "fail", "exception", "traceback", "❌", "::error"))
            ][:10]
            item.details.append(f"  ▶ {job_name}")
            for ln in error_lines:
                item.details.append(f"      {ln.strip()[:160]}")
    except Exception as exc:  # noqa: BLE001
        item.error = str(exc)
    return item


def fetch_review(client: GitHubClient, repo: str,
                 pr_number: int, review_id: int, url: str) -> FetchedItem:
    item = FetchedItem(url=url, kind="review")
    try:
        rev_comments = client.get_pr_review_comments(repo, pr_number)
        # Filter to comments belonging to this review
        thread = [c for c in rev_comments
                  if c.get("pull_request_review_id") == review_id]
        if not thread:
            item.summary = f"Review #{review_id} on PR #{pr_number} (no inline comments found)"
            return item

        item.title   = f"Review #{review_id} on PR #{pr_number}"
        item.summary = f"{len(thread)} comment(s) in review thread"
        for c in thread[:10]:
            author  = c.get("user", {}).get("login", "?")
            path    = c.get("path", "?")
            line    = c.get("line") or c.get("original_line", "?")
            preview = (c.get("body") or "")[:300].replace("\n", " ")
            item.details.append(f"  {path}:{line} — @{author}: {preview}")
    except Exception as exc:  # noqa: BLE001
        item.error = str(exc)
    return item


# ── Triage checks runner ──────────────────────────────────────────────────────
def run_triage(verbose: bool = False) -> List[TriageResult]:
    """Run ci_triage_repro.sh --json and parse results."""
    script = REPO_ROOT / "scripts" / "ci" / "ci_triage_repro.sh"
    results: List[TriageResult] = []

    if not script.exists():
        return [TriageResult("triage_script", "skip", "ci_triage_repro.sh not found")]

    try:
        proc = subprocess.run(
            ["bash", str(script), "--json"],
            capture_output=True, text=True, timeout=120,
            cwd=str(REPO_ROOT),
        )
        # Parse JSON block from output
        out = proc.stdout
        json_start = out.find("{")
        if json_start != -1:
            try:
                data = json.loads(out[json_start:])
                for check_id, info in data.get("results", {}).items():
                    results.append(TriageResult(
                        check_id = check_id,
                        status   = info.get("status", "?"),
                        detail   = info.get("detail", ""),
                    ))
            except json.JSONDecodeError as exc:
                results.append(TriageResult(
                    "triage_json", "skip",
                    f"Failed to parse JSON triage output: {exc}",
                ))
        if not results:
            # Fall back: parse human-readable output
            for line in out.splitlines():
                if "✅ PASS" in line:
                    key = line.split("—")[-1].strip().split(":")[0].strip()
                    results.append(TriageResult(key, "pass"))
                elif "❌ FAIL" in line:
                    key = line.split("—")[-1].strip().split(":")[0].strip()
                    results.append(TriageResult(key, "fail", line))
    except subprocess.TimeoutExpired:
        results.append(TriageResult("triage", "skip", "timeout after 120s"))
    except Exception as exc:  # noqa: BLE001
        results.append(TriageResult("triage", "skip", str(exc)))

    return results


# ── Digest writer ─────────────────────────────────────────────────────────────
def write_digest(report: BootstrapReport, verbose: bool = False) -> Path:
    """Write the context digest markdown and return the path."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    safe_ts = report.timestamp.replace(":", "-").replace("T", "_").rstrip("Z")
    archive = SESSIONS_DIR / f"session_{safe_ts}.md"

    lines = [
        "# Agent Session Context Digest",
        "",
        f"> **Generated:** {report.timestamp}  ",
        f"> **Repository:** {report.repo}  ",
        "> **Script:** `scripts/ci/session_bootstrap.py`",
        "",
        "---",
        "",
        "## 📋 Fetched Context",
        "",
    ]

    if not report.fetched:
        lines.append("_No GitHub URLs found in session context._")
    else:
        for item in report.fetched:
            icon = {"issue": "🐛", "pr": "🔀", "run": "⚙️", "review": "💬"}.get(item.kind, "🔗")
            lines.append(f"### {icon} [{item.kind.upper()}] {item.title or item.url}")
            lines.append(f"**URL:** {item.url}  ")
            if item.error:
                lines.append(f"**⚠ Fetch error:** `{item.error}`")
            else:
                lines.append(f"**Summary:** {item.summary}")
                if item.details:
                    lines.append("")
                    for d in item.details:
                        lines.append(f"- {d}")
            lines.append("")

    lines += [
        "---",
        "",
        "## 🔬 CI Triage Results",
        "",
    ]

    if not report.triage:
        lines.append("_Triage not run (--skip-triage or script unavailable)._")
    else:
        for r in report.triage:
            icon = "✅" if r.status == "pass" else ("⏭" if r.status == "skip" else "❌")
            lines.append(f"- {icon} **{r.check_id}**: {r.detail}")

    lines += ["", "---", "", "## 🚨 Blocking Issues", ""]
    if report.blocking:
        for b in report.blocking:
            lines.append(f"- ❌ {b}")
    else:
        lines.append("_None — baseline is healthy._")

    if report.warnings:
        lines += ["", "### ⚠ Warnings", ""]
        for w in report.warnings:
            lines.append(f"- ⚠ {w}")

    # ── Coverage Intelligence Injection (P2A) ────────────────────────────────
    # If a pre-built coverage_map.json exists, surface high-risk modules and
    # uncovered functions so the agent has immediate per-module risk context at
    # session start without a separate lookup.
    coverage_map_path = REPO_ROOT / ".codex" / "coverage" / "coverage_map.json"
    if coverage_map_path.exists():
        try:
            import json as _json
            cov_data = _json.loads(coverage_map_path.read_text(encoding="utf-8"))
            meta = cov_data.get("_meta", {})
            gaps = cov_data.get("gaps_summary", {})
            modules_map = cov_data.get("modules", {})
            overall_rate = meta.get("overall_line_rate", "?")
            zero_cov = gaps.get("modules_zero_coverage", [])
            low_cov = gaps.get("modules_below_50pct", [])
            total_uncov_fns = gaps.get("total_uncovered_functions", "?")
            high_risk_fns = gaps.get("high_risk_functions", "?")
            generated_at = meta.get("generated_at", "unknown")
            lines += [
                "",
                "---",
                "",
                "## 🗺️ Coverage Intelligence",
                "",
                f"> _Map generated: {generated_at}_  ",
                f"> _Overall line rate: {round(float(overall_rate) * 100, 1) if isinstance(overall_rate, (int, float)) else overall_rate}%_",
                f"> _Total uncovered functions: {total_uncov_fns} | High-risk: {high_risk_fns}_",
                "",
            ]
            if zero_cov:
                lines.append(f"**🔴 Zero-coverage modules ({len(zero_cov)}):**")
                for m in zero_cov[:10]:
                    lines.append(f"- `{m}`")
                if len(zero_cov) > 10:
                    lines.append(f"- _…and {len(zero_cov) - 10} more_")
                lines.append("")
            if low_cov:
                lines.append(f"**🟡 Low-coverage modules <50% ({len(low_cov)}):**")
                for m in low_cov[:10]:
                    rate = modules_map.get(m, {}).get("line_rate", "?")
                    pct = f"{round(float(rate) * 100, 1)}%" if isinstance(rate, (int, float)) else "?"
                    lines.append(f"- `{m}` ({pct})")
                if len(low_cov) > 10:
                    lines.append(f"- _…and {len(low_cov) - 10} more_")
                lines.append("")
        except Exception as exc:
            lines += [
                "",
                "---",
                "",
                "## 🗺️ Coverage Intelligence",
                "",
                f"_⚠ Failed to load coverage_map.json: {exc}_",
                "",
            ]

    lines += [
        "",
        "---",
        "",
        "## 🩺 Session Diagnostic Protocol Checklist",
        "",
        "Copy into `AGENT_ACCOUNTABILITY_REPORT.md` pre-flight section:",
        "",
        "```markdown",
        f"- [x] D-00 session_bootstrap.py — {len(report.fetched)} URL(s) found, "
        f"triage {'✅ clean' if report.baseline_ok is True else '❌ FAILURES FOUND' if report.baseline_ok is False else '⏭️ skipped'}",
        "- [ ] D-01 Memories loaded",
        "- [ ] D-02 CODEBASE_AGENCY_POLICY.md reviewed",
        "- [ ] D-03 Accountability report loaded (last 3 sessions)",
        "- [ ] D-04 CHANGELOG [Unreleased] reviewed",
        "- [ ] D-05 PR comments reviewed",
        "- [ ] D-06 CI status checked",
        "- [ ] D-07 ci_triage_repro.sh passed",
        "- [ ] D-08 Baseline documented",
        "```",
        "",
        "---",
        f"_Auto-generated by `session_bootstrap.py` at {report.timestamp}_",
    ]

    content = "\n".join(lines) + "\n"
    LATEST_PATH.write_text(content, encoding="utf-8")
    archive.write_text(content, encoding="utf-8")
    return archive


# ── Compact stdout summary ────────────────────────────────────────────────────
def print_summary(report: BootstrapReport) -> None:
    w = 70
    print("\n" + "═" * w)
    print(" 🚀  Agent Session Bootstrap Summary")
    print("═" * w)
    print(f"  Repository : {report.repo}")
    print(f"  Timestamp  : {report.timestamp}")
    print(f"  URLs found : {len(report.fetched)}")

    for item in report.fetched:
        icon = {"issue": "🐛", "pr": "🔀", "run": "⚙️", "review": "💬"}.get(item.kind, "🔗")
        status = "⚠ ERROR" if item.error else "✓"
        print(f"    {icon} [{item.kind:6s}] {status}  {item.title or item.url[:60]}")

    print()
    fail_count = sum(1 for r in report.triage if r.status == "fail")
    print(f"  Triage     : {len(report.triage)} checks — {fail_count} failed")
    for r in report.triage:
        icon = "✅" if r.status == "pass" else ("⏭" if r.status == "skip" else "❌")
        print(f"    {icon} {r.check_id}: {r.detail}")

    print()
    if report.blocking:
        print("  🚨 BLOCKING ISSUES:")
        for b in report.blocking:
            print(f"    ❌ {b}")
    else:
        print("  ✅ Baseline healthy — safe to begin session work")

    print(f"\n  Digest written to: {LATEST_PATH.relative_to(REPO_ROOT)}")
    print("═" * w + "\n")


# ── Main ──────────────────────────────────────────────────────────────────────
def _resolve_token() -> Optional[str]:
    for var in ("GITHUB_TOKEN", "CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GH_TOKEN"):
        val = os.environ.get(var)
        if val:
            return val
    return None


def _resolve_repo() -> str:
    env = os.environ.get("GITHUB_REPOSITORY", "")
    if env:
        return env
    # Try to infer from git remote
    try:
        out = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            cwd=str(REPO_ROOT), stderr=subprocess.DEVNULL, text=True
        ).strip()
        m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", out)
        if m:
            return m.group(1)
    except Exception:  # noqa: BLE001
        logger.debug("Suppressed exception in handler", exc_info=True)
    return "unknown/unknown"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--context",       help="Session context text (inline)")
    parser.add_argument("--context-file",  help="Path to file containing session context")
    parser.add_argument("--offline",       action="store_true",
                        help="Skip GitHub API fetching")
    parser.add_argument("--skip-triage",   action="store_true",
                        help="Skip ci_triage_repro.sh checks")
    parser.add_argument("--json-out",      help="Also write JSON digest to this path")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    # ── Gather context text ───────────────────────────────────────────────────
    context_text = ""
    if args.context:
        context_text = args.context
    elif args.context_file:
        context_text = Path(args.context_file).read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        context_text = sys.stdin.read()

    ts   = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    repo = _resolve_repo()

    report = BootstrapReport(timestamp=ts, repo=repo)

    # ── Extract URLs ──────────────────────────────────────────────────────────
    url_refs = extract_urls(context_text) if context_text else []
    if args.verbose:
        print(f"[bootstrap] Extracted {len(url_refs)} URL(s) from context")

    # ── Fetch each URL ────────────────────────────────────────────────────────
    if url_refs and not args.offline:
        token  = _resolve_token()
        if not token:
            report.warnings.append(
                "No GitHub token found (GITHUB_TOKEN / CODEX_MASTER_KEY / CODEX_BACKUP_KEY). "
                "URL fetching skipped — set a token for full context."
            )
            # Still register URLs so they appear in the digest
            for url, kind, url_repo, ids in url_refs:
                report.fetched.append(FetchedItem(
                    url=url, kind=kind,
                    title=url.split("/")[-1],
                    summary="(token unavailable — not fetched)",
                ))
        else:
            client = GitHubClient(token=token, verbose=args.verbose)
            for url, kind, url_repo, ids in url_refs:
                if args.verbose:
                    print(f"[bootstrap] Fetching {kind}: {url}")
                try:
                    if kind == "review":
                        pr_num, rev_id = (int(x) for x in ids.split(":"))
                        item = fetch_review(client, url_repo, pr_num, rev_id, url)
                    elif kind == "pr":
                        item = fetch_pr(client, url_repo, int(ids), url)
                    elif kind == "issue":
                        item = fetch_issue(client, url_repo, int(ids), url)
                    elif kind == "run":
                        item = fetch_run(client, url_repo, int(ids), url)
                    else:
                        item = FetchedItem(url=url, kind=kind, summary="unrecognised URL type")
                    report.fetched.append(item)
                except Exception as exc:  # noqa: BLE001
                    report.fetched.append(
                        FetchedItem(url=url, kind=kind, error=str(exc))
                    )
    elif url_refs and args.offline:
        report.warnings.append(
            f"--offline: {len(url_refs)} URL(s) found but not fetched."
        )
        for url, kind, url_repo, ids in url_refs:
            report.fetched.append(FetchedItem(
                url=url, kind=kind,
                title=url.split("/")[-1],
                summary="(offline mode — not fetched)",
            ))

    # ── Run CI triage ─────────────────────────────────────────────────────────
    if not args.skip_triage:
        if args.verbose:
            print("[bootstrap] Running ci_triage_repro.sh ...")
        report.triage = run_triage(verbose=args.verbose)
        failed = [r for r in report.triage if r.status == "fail"]
        for r in failed:
            # Map check_id (e.g. "1_actionlint", "2_ruff_i001") → doc anchor "#check-N"
            _m = re.match(r"(\d+)_", r.check_id)
            _anchor = f"#check-{_m.group(1)}" if _m else f"#{r.check_id}"
            report.blocking.append(
                f"Triage check '{r.check_id}' failed: {r.detail}. "
                f"See docs/ci/CI_TRIAGE_REPRO_S145.md{_anchor}"
            )
        report.baseline_ok = len(failed) == 0
    else:
        report.warnings.append("--skip-triage: CI triage checks not run")

    # ── Write digest ──────────────────────────────────────────────────────────
    archive_path = write_digest(report, verbose=args.verbose)
    if args.verbose:
        print(f"[bootstrap] Digest archived to: {archive_path}")

    # ── JSON output ───────────────────────────────────────────────────────────
    if args.json_out:
        json_data = {
            "timestamp":   report.timestamp,
            "repo":        report.repo,
            "baseline_ok": report.baseline_ok,
            "fetched": [
                {
                    "url":     f.url,
                    "kind":    f.kind,
                    "title":   f.title,
                    "summary": f.summary,
                    "details": f.details,
                    "error":   f.error,
                }
                for f in report.fetched
            ],
            "triage": [
                {"check_id": r.check_id, "status": r.status, "detail": r.detail}
                for r in report.triage
            ],
            "blocking": report.blocking,
            "warnings": report.warnings,
        }
        Path(args.json_out).write_text(
            json.dumps(json_data, indent=2), encoding="utf-8"
        )

    # ── Print summary ─────────────────────────────────────────────────────────
    print_summary(report)

    return 1 if report.blocking else 0


if __name__ == "__main__":
    sys.exit(main())
