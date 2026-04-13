#!/usr/bin/env python3
"""
scripts/ci/verify_issue_resolution.py
══════════════════════════════════════

In-session GitHub Issue / PR resolution verifier for Copilot agent sessions.

Purpose
───────
After fixing a bug or resolving a merge conflict, a Copilot agent can call
this script to CONFIRM that the referenced GitHub issue/PR is actually resolved
before ending the session — preventing premature session closure.

Resolution logic
────────────────
• **GitHub Issue** (github.com/.../issues/N):
    1. RESOLVED     — issue.state == "closed"
    2. LINKED-PR    — issue has a linked merged PR in its timeline
    3. UNRESOLVED   — issue is still open with no merged fix
    4. INVESTIGATE  — body references a workflow name; verifies latest run passes

• **Pull Request** (github.com/.../pull/N):
    1. RESOLVED     — PR is merged
    2. READY        — PR is open, mergeable_state == "clean", all required checks pass
    3. CONFLICTED   — PR has a merge conflict  (mergeable_state == "dirty")
    4. BLOCKED      — required CI checks are failing

• **Workflow run** (github.com/.../actions/runs/N):
    1. RESOLVED     — run conclusion == "success"
    2. UNRESOLVED   — run conclusion is "failure" / "timed_out" / etc.
    3. IN_PROGRESS  — run still running

• **auto** mode — infers kind from URL structure.

Usage
─────
  # Check specific issues/PRs:
  python scripts/ci/verify_issue_resolution.py \\
      --issues 3951 3953 \\
      --repo Aries-Serpent/_codex_

  # Check via full URLs (mixed issue + PR):
  python scripts/ci/verify_issue_resolution.py \\
      --urls https://github.com/Aries-Serpent/_codex_/issues/3951 \\
             https://github.com/Aries-Serpent/_codex_/pull/3954

  # JSON output for programmatic consumption:
  python scripts/ci/verify_issue_resolution.py --issues 3951 3953 --json

  # Emit GitHub step summary (for CI use):
  python scripts/ci/verify_issue_resolution.py --issues 3951 3953 --step-summary

  # Also verify that the current PR's HEAD commit passes all required checks:
  python scripts/ci/verify_issue_resolution.py --issues 3951 3953 --also-check-pr 3954

Exit codes
──────────
  0  All items verified resolved
  1  One or more items are NOT resolved
  2  Unable to determine status (API error / missing token)
  3  Bad arguments

Environment
───────────
  GH_TOKEN / GITHUB_TOKEN / CODEX_MASTER_KEY / CODEX_BACKUP_KEY
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

_OWNER = "Aries-Serpent"
_REPO  = "_codex_"

# ── Resolution status enum ────────────────────────────────────────────────────

class Status(str, Enum):
    RESOLVED    = "RESOLVED"
    READY       = "READY"           # PR is clean and ready to merge
    UNRESOLVED  = "UNRESOLVED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED     = "BLOCKED"
    CONFLICTED  = "CONFLICTED"
    UNKNOWN     = "UNKNOWN"

_RESOLVED_STATUSES = {Status.RESOLVED, Status.READY}

_ICONS = {
    Status.RESOLVED:    "✅",
    Status.READY:       "🟢",
    Status.UNRESOLVED:  "❌",
    Status.IN_PROGRESS: "⏳",
    Status.BLOCKED:     "🚫",
    Status.CONFLICTED:  "⚠️",
    Status.UNKNOWN:     "❓",
}

# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class VerificationResult:
    url:        str
    kind:       str          # "issue" | "pr" | "run"
    number:     int | str
    title:      str  = ""
    status:     Status = Status.UNKNOWN
    reason:     str  = ""
    details:    list[str] = field(default_factory=list)
    checked_at: str  = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def icon(self) -> str:
        return _ICONS.get(self.status, "❓")

    @property
    def resolved(self) -> bool:
        return self.status in _RESOLVED_STATUSES

    def to_dict(self) -> dict[str, Any]:
        return {
            "url":        self.url,
            "kind":       self.kind,
            "number":     self.number,
            "title":      self.title,
            "status":     self.status.value,
            "resolved":   self.resolved,
            "reason":     self.reason,
            "details":    self.details,
            "checked_at": self.checked_at,
        }

# ── GitHub API helpers ────────────────────────────────────────────────────────

def _token() -> str | None:
    for var in ("GH_TOKEN", "GITHUB_TOKEN", "CODEX_MASTER_KEY", "CODEX_BACKUP_KEY"):
        val = os.environ.get(var, "").strip()
        if val:
            return val
    return None


def _api(path: str, token: str | None = None, *, base: str = "https://api.github.com") -> Any:
    """GET {base}{path} and return parsed JSON.  Raises on non-2xx."""
    tok = token or _token()
    url = f"{base}{path}"
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Codex-Issue-Verifier/1.0",
    }
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raise exc


def _api_safe(path: str, token: str | None = None) -> Any | None:
    """Like _api() but returns None on error instead of raising."""
    try:
        return _api(path, token)
    except Exception:
        return None


def _paginated(path: str, token: str | None = None) -> list[Any]:
    """Fetch all pages of a list endpoint."""
    results: list[Any] = []
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        chunk = _api_safe(f"{path}{sep}per_page=100&page={page}", token)
        if not chunk:
            break
        results.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return results

# ── URL parsing ───────────────────────────────────────────────────────────────

_ISSUE_RE = re.compile(
    r"https://github\.com/([^/]+)/([^/\s#]+)/issues/(\d+)"
)
_PR_RE = re.compile(
    r"https://github\.com/([^/]+)/([^/\s#]+)/pull/(\d+)"
)
_RUN_RE = re.compile(
    r"https://github\.com/([^/]+)/([^/\s#]+)/actions/runs/(\d+)"
)


def parse_url(url: str) -> tuple[str, str, str, str]:
    """Return (owner, repo, kind, number_str) or raise ValueError."""
    for pattern, kind in ((_ISSUE_RE, "issue"), (_PR_RE, "pr"), (_RUN_RE, "run")):
        m = pattern.match(url.strip())
        if m:
            return m.group(1), m.group(2), kind, m.group(3)
    raise ValueError(f"Cannot parse GitHub URL: {url!r}")


def build_url(owner: str, repo: str, kind: str, number: str | int) -> str:
    paths = {"issue": "issues", "pr": "pull", "run": "actions/runs"}
    return f"https://github.com/{owner}/{repo}/{paths[kind]}/{number}"

# ── Verifiers ─────────────────────────────────────────────────────────────────

def verify_issue(owner: str, repo: str, number: int, token: str | None) -> VerificationResult:
    url = build_url(owner, repo, "issue", number)
    result = VerificationResult(url=url, kind="issue", number=number)

    issue = _api_safe(f"/repos/{owner}/{repo}/issues/{number}", token)
    if issue is None:
        result.status = Status.UNKNOWN
        result.reason = "GitHub API returned no data (token missing or 404)"
        return result

    result.title = issue.get("title", "")
    state = issue.get("state", "open")

    # ── 1. Simply closed ─────────────────────────────────────────────────────
    if state == "closed":
        result.status = Status.RESOLVED
        reason_detail = issue.get("state_reason") or "closed"
        result.reason = f"Issue is closed ({reason_detail})"
        return result

    # ── 2. Open — look for merged linked PR in timeline ──────────────────────
    events = _paginated(f"/repos/{owner}/{repo}/issues/{number}/events", token)
    for ev in events:
        if ev.get("event") == "cross-referenced":
            src = ev.get("source", {})
            ref_issue = src.get("issue", {})
            if ref_issue.get("pull_request") and ref_issue.get("state") == "closed":
                pr_url = ref_issue.get("html_url", "")
                result.status = Status.RESOLVED
                result.reason = f"Fixed by merged PR: {pr_url}"
                return result

    # ── 3. Open — check body/comments for referenced workflow name ───────────
    body = (issue.get("body") or "").lower()
    workflow_hit = _check_body_for_workflow(body, owner, repo, token, result)
    if workflow_hit:
        return result

    # ── 4. Still open with no evidence of resolution ─────────────────────────
    result.status = Status.UNRESOLVED
    labels = [lb["name"] for lb in issue.get("labels", [])]
    result.reason = f"Issue is open (labels: {', '.join(labels) or 'none'})"
    result.details.append(f"URL: {url}")
    return result


def _check_body_for_workflow(
    body: str,
    owner: str,
    repo: str,
    token: str | None,
    result: VerificationResult,
) -> bool:
    """If body mentions a workflow name, verify its latest run passes.

    Returns True if a determination was made (sets result.status).
    """
    # Common patterns: "validation pipeline failed", "fast validation", etc.
    wf_hints = re.findall(
        r"(?:workflow|run|pipeline|check)[:\s]+['\"`]?([a-z0-9 _\-]{4,60})['\"`]?",
        body,
        re.IGNORECASE,
    )
    if not wf_hints:
        return False

    runs = _api_safe(f"/repos/{owner}/{repo}/actions/runs?per_page=10", token)
    if not runs:
        return False

    run_list: list[dict] = runs.get("workflow_runs", [])
    for hint in wf_hints[:3]:
        hint_clean = hint.strip().lower()
        for run in run_list:
            if hint_clean in run.get("name", "").lower():
                conclusion = run.get("conclusion") or run.get("status", "")
                if conclusion == "success":
                    result.status = Status.RESOLVED
                    result.reason = (
                        f"Referenced workflow '{run['name']}' latest run: SUCCESS"
                    )
                    result.details.append(run.get("html_url", ""))
                elif conclusion in ("failure", "timed_out", "cancelled"):
                    result.status = Status.UNRESOLVED
                    result.reason = (
                        f"Referenced workflow '{run['name']}' latest run: {conclusion.upper()}"
                    )
                    result.details.append(run.get("html_url", ""))
                else:
                    result.status = Status.IN_PROGRESS
                    result.reason = (
                        f"Referenced workflow '{run['name']}' is still {conclusion or 'in_progress'}"
                    )
                return True
    return False


def verify_pr(owner: str, repo: str, number: int, token: str | None) -> VerificationResult:
    url = build_url(owner, repo, "pr", number)
    result = VerificationResult(url=url, kind="pr", number=number)

    pr = _api_safe(f"/repos/{owner}/{repo}/pulls/{number}", token)
    if pr is None:
        result.status = Status.UNKNOWN
        result.reason = "GitHub API returned no data (token missing or 404)"
        return result

    result.title = pr.get("title", "")
    state = pr.get("state", "open")

    # ── 1. Merged ─────────────────────────────────────────────────────────────
    if pr.get("merged"):
        result.status = Status.RESOLVED
        merged_at = pr.get("merged_at", "")
        result.reason = f"PR was merged at {merged_at}"
        return result

    # ── 2. Closed (not merged) ────────────────────────────────────────────────
    if state == "closed":
        result.status = Status.RESOLVED
        result.reason = "PR is closed (not merged — may have been superseded)"
        return result

    # ── 3. Merge conflict ─────────────────────────────────────────────────────
    mergeable_state = pr.get("mergeable_state", "unknown")
    if mergeable_state == "dirty":
        result.status = Status.CONFLICTED
        result.reason = "PR has a merge conflict (mergeable_state=dirty)"
        result.details.append("Run: git merge origin/<base-branch> and push to resolve")
        return result

    # ── 4. Check required CI ──────────────────────────────────────────────────
    sha = pr.get("head", {}).get("sha", "")
    if sha:
        check_result = _check_required_ci(owner, repo, sha, token)
        if check_result:
            result.details.extend(check_result["details"])
            if check_result["all_pass"]:
                result.status = Status.READY
                result.reason = (
                    f"PR is open, mergeable_state={mergeable_state!r}, "
                    f"all required checks pass ({check_result['passed']}/{check_result['total']})"
                )
            elif check_result["any_fail"]:
                result.status = Status.BLOCKED
                result.reason = (
                    f"PR has failing required checks "
                    f"({check_result['failed']}/{check_result['total']} failing)"
                )
            elif check_result["any_pending"]:
                result.status = Status.IN_PROGRESS
                result.reason = (
                    f"PR has pending checks "
                    f"({check_result['pending']}/{check_result['total']} pending)"
                )
            else:
                result.status = Status.READY
                result.reason = f"PR is open, mergeable_state={mergeable_state!r}"
            return result

    result.status = Status.READY if mergeable_state == "clean" else Status.IN_PROGRESS
    result.reason = f"PR is open, mergeable_state={mergeable_state!r}"
    return result


def _check_required_ci(
    owner: str, repo: str, sha: str, token: str | None
) -> dict[str, Any] | None:
    """Return a summary of required check-run statuses for a commit SHA."""
    data = _api_safe(
        f"/repos/{owner}/{repo}/commits/{sha}/check-runs?per_page=100", token
    )
    if not data:
        return None

    runs = data.get("check_runs", [])
    if not runs:
        return None

    passed  = [r for r in runs if r.get("conclusion") == "success"]
    failed  = [r for r in runs if r.get("conclusion") in ("failure", "timed_out", "cancelled")]
    pending = [r for r in runs if r.get("status") in ("queued", "in_progress")]
    skipped = [r for r in runs if r.get("conclusion") in ("skipped", "neutral", "action_required")]

    details = []
    for r in failed:
        details.append(f"  ❌ {r['name']} — {r.get('conclusion','?')} | {r.get('html_url','')}")
    for r in pending:
        details.append(f"  ⏳ {r['name']} — {r.get('status','?')}")

    return {
        "total":       len(runs),
        "passed":      len(passed),
        "failed":      len(failed),
        "pending":     len(pending),
        "skipped":     len(skipped),
        "all_pass":    len(failed) == 0 and len(pending) == 0,
        "any_fail":    len(failed) > 0,
        "any_pending": len(pending) > 0,
        "details":     details,
    }


def verify_run(owner: str, repo: str, run_id: int, token: str | None) -> VerificationResult:
    url = build_url(owner, repo, "run", run_id)
    result = VerificationResult(url=url, kind="run", number=run_id)

    run = _api_safe(f"/repos/{owner}/{repo}/actions/runs/{run_id}", token)
    if run is None:
        result.status = Status.UNKNOWN
        result.reason = "GitHub API returned no data (token missing or 404)"
        return result

    result.title = run.get("display_title") or run.get("name", "")
    status     = run.get("status", "")
    conclusion = run.get("conclusion") or ""

    if status in ("queued", "in_progress", "waiting", "requested"):
        result.status = Status.IN_PROGRESS
        result.reason = f"Workflow run is {status}"
    elif conclusion == "success":
        result.status = Status.RESOLVED
        result.reason = "Workflow run completed successfully"
    elif conclusion in ("failure", "timed_out", "cancelled", "startup_failure"):
        result.status = Status.UNRESOLVED
        result.reason = f"Workflow run concluded: {conclusion}"
        result.details.append(f"View logs: {run.get('html_url','')}")
    elif conclusion == "action_required":
        result.status = Status.BLOCKED
        result.reason = "Workflow run requires manual approval"
    elif conclusion in ("skipped", "neutral"):
        result.status = Status.RESOLVED
        result.reason = f"Workflow run was {conclusion} (counts as resolved)"
    else:
        result.status = Status.UNKNOWN
        result.reason = f"Unrecognised status={status!r} conclusion={conclusion!r}"

    return result

# ── Main verifier entry point ─────────────────────────────────────────────────

def verify_all(
    urls: list[str],
    token: str | None = None,
) -> list[VerificationResult]:
    """Verify every URL and return one VerificationResult per item."""
    results: list[VerificationResult] = []
    for url in urls:
        try:
            owner, repo, kind, num_str = parse_url(url)
            num = int(num_str)
        except ValueError as exc:
            r = VerificationResult(url=url, kind="unknown", number=url)
            r.status = Status.UNKNOWN
            r.reason = str(exc)
            results.append(r)
            continue

        if kind == "issue":
            results.append(verify_issue(owner, repo, num, token))
        elif kind == "pr":
            results.append(verify_pr(owner, repo, num, token))
        elif kind == "run":
            results.append(verify_run(owner, repo, num, token))
        else:
            r = VerificationResult(url=url, kind=kind, number=num)
            r.status = Status.UNKNOWN
            r.reason = f"Unsupported URL kind: {kind!r}"
            results.append(r)

    return results

# ── Output formatters ─────────────────────────────────────────────────────────

def format_text(results: list[VerificationResult]) -> str:
    lines = [
        "",
        "╔══════════════════════════════════════════════════════════════╗",
        "║       Issue Resolution Verification — Copilot Session        ║",
        "╚══════════════════════════════════════════════════════════════╝",
        f"  Checked: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
    ]
    all_resolved = all(r.resolved for r in results)
    for r in results:
        lines.append(f"  {r.icon}  [{r.kind.upper():6s}] #{r.number}  {r.title[:60]}")
        lines.append(f"      Status : {r.status.value}")
        lines.append(f"      Reason : {r.reason}")
        for d in r.details:
            lines.append(f"             {d}")
        lines.append("")

    sep = "─" * 64
    lines.append(sep)
    resolved_count = sum(1 for r in results if r.resolved)
    total = len(results)
    verdict = "✅  ALL RESOLVED" if all_resolved else f"❌  {total - resolved_count}/{total} UNRESOLVED"
    lines.append(f"  {verdict}")
    lines.append(sep)
    return "\n".join(lines)


def format_markdown(results: list[VerificationResult]) -> str:
    """GitHub step-summary markdown."""
    all_resolved = all(r.resolved for r in results)
    resolved_count = sum(1 for r in results if r.resolved)
    total = len(results)

    lines = [
        "## 🔍 Issue Resolution Verification",
        "",
        f"**Checked:** `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        "",
        "| # | Type | Title | Status | Reason |",
        "|---|------|-------|--------|--------|",
    ]
    for r in results:
        title_short = (r.title[:50] + "…") if len(r.title) > 50 else r.title
        lines.append(
            f"| #{r.number} | {r.kind} | {title_short} | {r.icon} {r.status.value} | {r.reason} |"
        )

    lines += [
        "",
        "---",
        "",
        f"**Result:** `{resolved_count}/{total}` resolved",
        "",
    ]
    if all_resolved:
        lines.append("> ✅ **All issues verified resolved. Session may close.**")
    else:
        lines.append("> ❌ **One or more issues are NOT resolved. Do not close the session.**")
        unresolved = [r for r in results if not r.resolved]
        for r in unresolved:
            lines.append(">")
            lines.append(f"> - `{r.kind}` #{r.number}: {r.reason}")

    return "\n".join(lines)


def write_step_summary(md: str) -> None:
    """Write to $GITHUB_STEP_SUMMARY if running inside GitHub Actions."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(md + "\n")

# ── CLI ───────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="verify_issue_resolution",
        description="Verify GitHub issues/PRs are resolved before ending a Copilot session.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--issues", "-i",
        nargs="+",
        metavar="NUMBER",
        help="Issue numbers to verify (relative to --repo).",
    )
    p.add_argument(
        "--prs",
        nargs="+",
        metavar="NUMBER",
        help="Pull-request numbers to verify (relative to --repo).",
    )
    p.add_argument(
        "--runs",
        nargs="+",
        metavar="RUN_ID",
        help="Workflow run IDs to verify (relative to --repo).",
    )
    p.add_argument(
        "--urls", "-u",
        nargs="+",
        metavar="URL",
        help="Full GitHub URLs to verify (issues, PRs, or workflow runs).",
    )
    p.add_argument(
        "--repo", "-r",
        default=f"{_OWNER}/{_REPO}",
        help=f"owner/repo (default: {_OWNER}/{_REPO}).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON array to stdout instead of human-readable text.",
    )
    p.add_argument(
        "--step-summary",
        action="store_true",
        help="Write GitHub-flavoured Markdown to $GITHUB_STEP_SUMMARY.",
    )
    p.add_argument(
        "--output-json",
        metavar="FILE",
        help="Write JSON report to FILE.",
    )
    p.add_argument(
        "--allow-in-progress",
        action="store_true",
        help="Treat IN_PROGRESS as resolved (don't fail on still-running checks).",
    )
    p.add_argument(
        "--token",
        metavar="TOKEN",
        help="GitHub token (overrides env vars).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # ── Collect URLs ─────────────────────────────────────────────────────────
    token = args.token or _token()
    try:
        owner, repo = args.repo.split("/", 1)
    except ValueError:
        print(f"ERROR: --repo must be owner/repo, got {args.repo!r}", file=sys.stderr)
        return 3

    urls: list[str] = list(args.urls or [])
    for n in args.issues or []:
        urls.append(build_url(owner, repo, "issue", n))
    for n in args.prs or []:
        urls.append(build_url(owner, repo, "pr", n))
    for n in args.runs or []:
        urls.append(build_url(owner, repo, "run", n))

    if not urls:
        parser.error("Provide at least one of: --issues, --prs, --runs, --urls")

    # ── Verify ────────────────────────────────────────────────────────────────
    results = verify_all(urls, token=token)

    # Apply --allow-in-progress option
    if args.allow_in_progress:
        for r in results:
            if r.status == Status.IN_PROGRESS:
                r.status = Status.READY
                r.reason += " (treated as resolved via --allow-in-progress)"

    # ── Output ────────────────────────────────────────────────────────────────
    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        print(format_text(results))

    if args.step_summary:
        md = format_markdown(results)
        write_step_summary(md)
        if not args.json:
            print("\n--- GitHub Step Summary ---")
            print(md)

    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps([r.to_dict() for r in results], indent=2))

    # ── Exit code ─────────────────────────────────────────────────────────────
    all_resolved = all(r.resolved for r in results)
    if all(r.status == Status.UNKNOWN for r in results):
        return 2  # API failure / no token
    return 0 if all_resolved else 1


if __name__ == "__main__":
    sys.exit(main())
