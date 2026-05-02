#!/usr/bin/env python3
"""
pre_session_context.py — Hardened Copilot pre-session context briefing (P6-B, S297).

ALWAYS run this script FIRST at the start of every Copilot coding session.
It produces a single structured markdown briefing that gives the agent immediate
situational awareness across five dimensions before any code change is attempted:

  § A  Workflow Status      — failing + in-progress check-runs with ETA for HEAD SHA
  § B  Unaddressed Comments — blocking comment list with IDs + body previews
  § C  CI Log Snippets      — last 60 lines of each failing job for instant diagnosis
  § D  Action Queue         — prioritised fix list derived from §A + §B
  § E  Skills Manifest      — which grounded solution patterns apply

Grounded sources:
  * GitHub Check Runs API  — live per-SHA status (no caching)
  * GitHub PR Comments API — live unaddressed comment state
  * GitHub Actions Logs    — actual failure output, not cached
  * .codex/aftermath/failure_pattern_solutions.yaml — RP-XXX pattern library

Usage:
  python scripts/ci/pre_session_context.py --pr N --sha SHA
  python scripts/ci/pre_session_context.py --pr N --sha SHA --output-file context.md
  python scripts/ci/pre_session_context.py --pr N --sha SHA --json

  SHA may be the full SHA or any HEAD-resolvable ref.

Exit codes:
  0 — briefing produced; zero blocking issues
  1 — briefing produced; one or more blocking comments or failing checks
  2 — GitHub API error / missing token

Environment:
  GH_TOKEN, GITHUB_TOKEN, CODEX_MASTER_KEY, or CODEX_BACKUP_KEY — any one is enough
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_OWNER = "Aries-Serpent"
_REPO = "_codex_"
_MAX_LOG_LINES = 60          # lines of CI log to include per failing job
_MAX_BLOCKING_BODY = 200     # chars of comment body to preview
_ETA_THRESHOLD_MINUTES = 40  # flag in-progress runs completing soon

# ---------------------------------------------------------------------------
# Shared GitHub helpers
# ---------------------------------------------------------------------------

def _token() -> str:
    for var in ("GH_TOKEN", "GITHUB_TOKEN", "CODEX_MASTER_KEY", "CODEX_BACKUP_KEY"):
        val = os.environ.get(var, "")
        if val:
            return val
    return ""


def _api_get(path: str, token: str, base: str = "https://api.github.com") -> Any | None:
    url = f"{base}{path}" if path.startswith("/") else path
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        snippet = exc.read()[:200].decode("utf-8", errors="replace")
        print(f"[pre_session_context] HTTP {exc.code} for {url}: {snippet}", file=sys.stderr)
        return None
    except Exception as exc:  # network error — return None so caller can degrade gracefully
        print(f"[pre_session_context] Error fetching {url}: {exc}", file=sys.stderr)
        return None


def _api_get_all(path: str, token: str) -> list[Any]:
    results: list[Any] = []
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        data = _api_get(f"{path}{sep}per_page=100&page={page}", token)
        if not isinstance(data, list):
            if isinstance(data, dict):
                for key in ("check_runs", "workflow_runs", "jobs", "comments"):
                    if key in data:
                        data = data[key]
                        break
                else:
                    if data:
                        results.append(data)
                    break
            else:
                break
        if not data:
            break
        results.extend(data)
        if len(data) < 100:
            break
        page += 1
    return results


# ---------------------------------------------------------------------------
# § A — Workflow / Check-Run Status
# ---------------------------------------------------------------------------

def _fetch_check_runs(owner: str, repo: str, sha: str, token: str) -> list[dict]:
    runs: list[dict] = []
    page = 1
    while True:
        data = _api_get(
            f"/repos/{owner}/{repo}/commits/{sha}/check-runs?per_page=100&page={page}",
            token,
        )
        if not data or "check_runs" not in data:
            break
        batch = data["check_runs"]
        runs.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return runs


def _parse_dt(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _eta_str(run: dict, history_median_s: float | None) -> str:
    if history_median_s is None:
        return "ETA unknown"
    started = _parse_dt(run.get("started_at") or run.get("created_at") or "")
    if started is None:
        return "ETA unknown"
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    remaining = history_median_s - elapsed
    if remaining <= 0:
        return "~finishing"
    return f"~{int(remaining / 60)} min"


def _median_s(runs: list[dict]) -> float | None:
    durations = []
    for r in runs:
        t0 = _parse_dt(r.get("created_at") or r.get("run_started_at") or "")
        t1 = _parse_dt(r.get("updated_at") or "")
        if t0 and t1:
            durations.append((t1 - t0).total_seconds())
    if not durations:
        return None
    durations.sort()
    return durations[len(durations) // 2]


def section_a_workflow_status(
    owner: str, repo: str, sha: str, token: str
) -> tuple[str, list[dict], list[dict]]:
    """Return (markdown_section, failing_list, in_progress_list)."""
    check_runs = _fetch_check_runs(owner, repo, sha, token)
    if not check_runs:
        return (
            "### § A — Workflow Status\n\n_⚠️ Unable to fetch check runs (token scope?)._\n",
            [],
            [],
        )

    failing: list[dict] = []
    in_prog: list[dict] = []
    monitor: list[dict] = []

    for run in check_runs:
        status = run.get("status", "")
        conclusion = run.get("conclusion") or ""
        name = run.get("name", "unknown")
        url = run.get("html_url", "")
        run_id = run.get("id", "")

        if status == "completed" and conclusion not in (
            "success", "neutral", "skipped"
        ):
            failing.append({"name": name, "conclusion": conclusion, "url": url, "id": run_id})

        elif status in ("in_progress", "queued", "waiting", "requested"):
            # Estimate ETA from the last 10 runs of the same workflow
            history_data = _api_get(
                f"/repos/{owner}/{repo}/actions/runs?status=completed&per_page=10",
                token,
            )
            history = [
                r for r in (history_data or {}).get("workflow_runs", [])
                if r.get("name") == name
            ]
            median = _median_s(history)
            eta = _eta_str(run, median)
            eta_mins: int | None = None
            if eta.startswith("~") and "min" in eta:
                try:
                    eta_mins = int(eta.replace("~", "").replace(" min", ""))
                except ValueError:
                    pass  # not a plain "~N min" string — leave as None

            entry = {
                "name": name, "status": status, "url": url,
                "id": run_id, "eta": eta, "eta_minutes": eta_mins,
            }
            in_prog.append(entry)
            if eta_mins is not None and eta_mins < _ETA_THRESHOLD_MINUTES:
                monitor.append(entry)

    lines = [f"### § A — Workflow Status  (`{sha[:12]}`)", ""]

    if not failing and not in_prog:
        lines += ["**✅ All checks passed — no failures, no in-progress runs.**", ""]
    else:
        if failing:
            lines += [
                f"**❌ {len(failing)} failing check(s) — fix these before anything else:**",
                "",
                "| # | Workflow | Conclusion | Run |",
                "|---|----------|-----------|-----|",
            ]
            for i, f in enumerate(failing, 1):
                lines.append(
                    f"| {i} | `{f['name']}` | `{f['conclusion']}` "
                    f"| [#{f['id']}]({f['url']}) |"
                )
            lines.append("")

        if in_prog:
            lines += [
                f"**⏳ {len(in_prog)} in-progress "
                f"({'🔔 ' + str(len(monitor)) + ' finishing soon' if monitor else 'none finishing soon'}):**",
                "",
                "| Workflow | Status | ETA | Watch? |",
                "|----------|--------|-----|--------|",
            ]
            for ip in in_prog:
                flag = "🔔 YES — re-scan after fix" if ip in monitor else "—"
                lines.append(
                    f"| `{ip['name']}` | {ip['status']} | {ip['eta']} | {flag} |"
                )
            lines.append("")

    return "\n".join(lines), failing, in_prog


# ---------------------------------------------------------------------------
# § B — Unaddressed Blocking Comments
# ---------------------------------------------------------------------------

# Mirror the blocking sets from check_pr_comments.py
_BLOCKING_AUTHORS = {"mbaetiong"}
_BLOCKING_BOTS = {
    "github-actions[bot]",
    "copilot-pull-request-reviewer[bot]",
    "github-advanced-security[bot]",
    "github-code-quality[bot]",
}
_COPILOT_AGENTS = {"copilot-swe-agent[bot]", "github-copilot[bot]", "Copilot"}
_SKIP_BODY_MARKERS = (
    "<!-- comment-review-gate",
    "<!-- ci-rescue:",
    "<!-- pre-merge-validation-summary -->",
    "<!-- auto-fix-ci-issues -->",
    "<!-- copilot-escalation:",
    "<!-- self-healing-escalation -->",
    "<!-- workflow-execution-gate:",
    "<!-- session-requirements-pending -->",
    "<!-- pr-followup-prompt-generated -->",
    "<!-- compiled-bot-feedback",
    "<!-- session-done-retrigger -->",
    "<!-- session-done-loop-break -->",
    "<!-- root-org-validation-v1 -->",
    "<!-- cost-check-bot -->",
    "<!-- agent-file-size-gate -->",
    "<!-- session-gate-queued -->",
)
_SKIP_TEXT_PATTERNS = (
    "## Self-Healing Escalation",
    "## 🤖 Copilot Self-Healing Escalation",
)


def section_b_blocking_comments(
    pr_number: int, repo: str, token: str
) -> tuple[str, list[dict]]:
    """Return (markdown_section, blocking_list)."""
    issue_comments = _api_get_all(f"/repos/{repo}/issues/{pr_number}/comments", token)
    review_comments = _api_get_all(f"/repos/{repo}/pulls/{pr_number}/comments", token)

    # Build Copilot response timeline for the timestamp heuristic
    copilot_times: list[datetime] = []
    copilot_reply_index: dict[int, list[datetime]] = {}

    for c in [*issue_comments, *review_comments]:
        login = (c.get("user") or {}).get("login", "")
        if login in _COPILOT_AGENTS:
            dt = _parse_dt(c.get("created_at", ""))
            if dt:
                copilot_times.append(dt)
            parent_id = c.get("in_reply_to_id")
            if parent_id and dt:
                copilot_reply_index.setdefault(int(parent_id), []).append(dt)

    def _addressed(ts_str: str, comment_id: int | None = None) -> bool:
        dt = _parse_dt(ts_str)
        if dt is None:
            return False
        if comment_id is not None and copilot_reply_index.get(comment_id):
            return True
        return any(rt > dt for rt in copilot_times)

    blocking: list[dict] = []

    def _scan(comments: list[dict], ctype: str) -> None:
        for c in comments:
            login = (c.get("user") or {}).get("login", "")
            if login in _COPILOT_AGENTS:
                continue
            body_raw = (c.get("body") or "")
            body_start = body_raw.lstrip()[:80]
            if any(body_start.startswith(m) for m in _SKIP_BODY_MARKERS):
                continue
            if any(body_start.startswith(p) for p in _SKIP_TEXT_PATTERNS):
                continue
            if login not in _BLOCKING_AUTHORS and login not in _BLOCKING_BOTS:
                continue
            ts = c.get("created_at", "")
            cid = c.get("id")
            if _addressed(ts, cid if ctype == "review" else None):
                continue
            blocking.append({
                "id": cid,
                "author": login,
                "type": ctype,
                "url": c.get("html_url", ""),
                "created_at": ts,
                "preview": body_raw[:_MAX_BLOCKING_BODY].replace("\n", " "),
            })

    _scan(issue_comments, "issue_comment")
    _scan(review_comments, "review_comment")

    lines = ["### § B — Unaddressed Blocking Comments", ""]

    if not blocking:
        lines += ["**✅ No unaddressed blocking comments — Comment Review Gate will pass.**", ""]
    else:
        lines += [
            f"**🚨 {len(blocking)} unaddressed blocking comment(s) — "
            "Comment Review Gate will FAIL until all are replied to:**",
            "",
            "| # | Author | Type | Created | Preview | Link |",
            "|---|--------|------|---------|---------|------|",
        ]
        for i, b in enumerate(blocking, 1):
            preview = b["preview"][:80].rstrip()
            ts_short = b["created_at"][:16].replace("T", " ")
            lines.append(
                f"| {i} | `{b['author']}` | {b['type']} | {ts_short} "
                f"| {preview}… | [view]({b['url']}) |"
            )
        lines += [
            "",
            "> **Reply format** (satisfies S221 guard + comment gate):",
            "> `Fixed at <7-char-SHA>.` / `Addressed at <SHA>.` / `Resolved at <SHA>.`",
            "",
        ]

    return "\n".join(lines), blocking


# ---------------------------------------------------------------------------
# § C — CI Log Snippets
# ---------------------------------------------------------------------------

def _get_failing_jobs(owner: str, repo: str, run_id: int | str, token: str) -> list[dict]:
    data = _api_get(f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs", token)
    if not data:
        return []
    return [
        j for j in data.get("jobs", [])
        if j.get("conclusion") in ("failure", "cancelled")
    ]


def _get_job_log_tail(owner: str, repo: str, job_id: int | str, token: str, lines: int) -> str:
    """Download job log and return the last *lines* lines."""
    data = _api_get(
        f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
        token,
    )
    if data is None:
        # The logs endpoint redirects; urllib follows redirects automatically.
        # If _api_get returns None it means we got an error response.
        return "_Log unavailable (may require actions:read scope)._"
    raw = data if isinstance(data, str) else str(data)
    # Strip ANSI escape sequences for readability
    # re is imported at module level
    raw = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", raw)
    tail = raw.strip().splitlines()[-lines:]
    return "\n".join(tail)


def section_c_log_snippets(
    owner: str, repo: str, failing: list[dict], token: str
) -> str:
    """Return markdown section with last N log lines from each failing job."""
    if not failing:
        return "### § C — CI Log Snippets\n\n_No failing checks — no logs needed._\n"

    lines = ["### § C — CI Log Snippets  (last 60 lines per failing job)", ""]

    for check in failing[:5]:  # cap at 5 checks to avoid token overload
        run_id = check.get("id")
        name = check.get("name", "unknown")
        lines += [f"#### ❌ `{name}`", ""]

        if not run_id:
            lines += ["_Run ID unavailable._", ""]
            continue

        # Check runs != workflow runs — we need the associated workflow run
        # The check run's "app" is GitHub Actions; drill via check run details
        cr_detail = _api_get(
            f"/repos/{owner}/{repo}/check-runs/{run_id}", token
        )
        # Try to get the workflow run ID from the check suite
        suite_id = None
        if cr_detail:
            suite_id = (cr_detail.get("check_suite") or {}).get("id")

        if suite_id:
            # Find workflow run associated with this check suite
            wr_data = _api_get(
                f"/repos/{owner}/{repo}/actions/runs?check_suite_id={suite_id}",
                token,
            )
            wf_runs = (wr_data or {}).get("workflow_runs", [])
        else:
            wf_runs = []

        if not wf_runs:
            lines += [
                f"> _Could not resolve workflow run for check `{name}` "
                f"(run #{run_id}). View manually: {check.get('url', '')}_",
                "",
            ]
            continue

        wf_run_id = wf_runs[0]["id"]
        failing_jobs = _get_failing_jobs(owner, repo, wf_run_id, token)

        if not failing_jobs:
            lines += [f"_No failed jobs found in workflow run #{wf_run_id}._", ""]
            continue

        for job in failing_jobs[:3]:  # cap at 3 jobs per check
            job_name = job.get("name", "unknown")
            job_id = job.get("id")
            lines += [f"**Job:** `{job_name}`", ""]
            if job_id:
                log_tail = _get_job_log_tail(owner, repo, job_id, token, _MAX_LOG_LINES)
                lines += ["```", log_tail, "```", ""]
            else:
                lines += ["_Job ID unavailable._", ""]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# § D — Prioritised Action Queue
# ---------------------------------------------------------------------------

def section_d_action_queue(
    failing: list[dict],
    blocking: list[dict],
    in_prog: list[dict],
) -> str:
    lines = ["### § D — Immediate Action Queue  (fix in this order)", ""]

    queue: list[str] = []

    # 1. Blocking comments first — gate will never clear otherwise
    if blocking:
        queue.append(
            f"**① Reply to {len(blocking)} blocking comment(s)** — "
            "use `reply_to_comment` for `<comment_new>` items; the global timestamp "
            "heuristic in `check_pr_comments.py` will mark all earlier comments addressed "
            "once a new `@copilot` PR comment is posted."
        )

    # 2. Failing checks — in conclusion-severity order
    if failing:
        names = ", ".join(f"`{f['name']}`" for f in failing[:5])
        queue.append(
            f"**② Fix {len(failing)} failing check(s):** {names}  "
            "— See § C for log snippets. Check § E for matching RP-XXX patterns."
        )

    # 3. In-progress finishing soon — monitor, don't start new commits yet
    if in_prog:
        soon = [ip for ip in in_prog if ip.get("eta_minutes") and ip["eta_minutes"] < _ETA_THRESHOLD_MINUTES]
        if soon:
            names = ", ".join(f"`{ip['name']}`" for ip in soon[:3])
            queue.append(
                f"**③ 🔔 Monitor:** {names} — completing in "
                f"< {_ETA_THRESHOLD_MINUTES} min. Wait for result before "
                "committing a fix that may conflict."
            )

    # 4. End-of-session mandatory items
    queue += [
        (
            "**④ Before final commit:** `python -m ruff check src/ tests/ --fix`\n"
            "→ `python scripts/ci/mypy_baseline.py --require-baseline`\n"
            "→ `python scripts/ci/auto_fix_common_issues.py --check-only`"
        ),
        "**⑤ Update CHANGELOG.md** with `### Fixed (SN)` entry under `## [Unreleased]`",
        "**⑥ Update docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md** with today's session entry",
    ]

    if not queue:
        lines += ["**✅ Nothing to do — all checks passing and all comments addressed.**", ""]
    else:
        for item in queue:
            lines += [f"- {item}", ""]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# § E — Skills & Pattern Library
# ---------------------------------------------------------------------------

def section_e_skills(owner: str, repo: str) -> str:
    """Load grounded RP-XXX patterns from the PDA library if available."""
    pattern_file = Path(__file__).parents[2] / ".codex" / "aftermath" / "failure_pattern_solutions.yaml"

    lines = ["### § E — Grounded Skills & Pattern Library", ""]

    if pattern_file.exists():
        try:
            raw = pattern_file.read_text(encoding="utf-8")
            # Extract pattern IDs and one-line descriptions without a full YAML parse
            # re is imported at module level
            entries = re.findall(r"pattern_id:\s*(\S+).*?description:\s*(.+)", raw, re.DOTALL)
            if entries:
                lines += [
                    "**Grounded RP-XXX patterns from `.codex/aftermath/failure_pattern_solutions.yaml`:**",
                    "",
                    "| Pattern | Description |",
                    "|---------|-------------|",
                ]
                for pid, desc in entries[:20]:
                    lines.append(f"| `{pid}` | {desc.strip()[:90]} |")
                lines.append("")
        except Exception:  # file read error — degrade gracefully
            lines += ["_Pattern library unreadable._", ""]
    else:
        lines += ["_Pattern library not found at `.codex/aftermath/failure_pattern_solutions.yaml`._", ""]

    lines += [
        "**Key skills to invoke for diagnosis:**",
        "- `python scripts/ci/pda_failure_logger.py summarize` — query grounded solutions for known patterns",
        "- `python scripts/ci/auto_fix_common_issues.py --check-only --json-output /tmp/diag.json` — detect auto-fixable issues",
        "- `python scripts/ci/scan_failing_workflows.py --sha <SHA>` — live check-run status",
        "- `python scripts/ci/check_pr_comments.py --pr <N> --repo <owner/repo>` — full comment gate audit",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Assembler
# ---------------------------------------------------------------------------

def build_briefing(
    pr_number: int,
    sha: str,
    repo: str,
    token: str,
) -> tuple[str, int]:
    """
    Build the complete pre-session briefing.

    Returns (markdown_text, exit_code) where exit_code is:
      0 — no blocking issues
      1 — blocking comments or failing checks present
    """
    owner, repo_name = repo.split("/", 1)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    header = "\n".join([
        "# 🧠 Copilot Pre-Session Context Briefing",
        "",
        f"> **PR:** #{pr_number}  |  **Repo:** `{repo}`  "
        f"|  **HEAD SHA:** `{sha[:12]}`  |  **Generated:** {ts}",
        ">",
        "> ⚠️ **ALWAYS read this entire document before touching any file.**",
        "> Fix § D items in order. Do NOT skip § B (blocking comments block CI merge).",
        "",
        "---",
        "",
    ])

    sec_a, failing, in_prog = section_a_workflow_status(owner, repo_name, sha, token)
    sec_b, blocking = section_b_blocking_comments(pr_number, repo, token)
    sec_c = section_c_log_snippets(owner, repo_name, failing, token)
    sec_d = section_d_action_queue(failing, blocking, in_prog)
    sec_e = section_e_skills(owner, repo_name)

    footer = "\n".join([
        "---",
        "",
        "## 📌 Session Protocol Reminders",
        "",
        "Per `docs/ci/PR_LIFECYCLE.md` §14.5 — mandatory end-of-session checklist:",
        "",
        "- [ ] Replied to **all** `<comment_new>` blocking comments with `Fixed at <SHA>` / `Addressed at <SHA>` / `Resolved at <SHA>`",
        "- [ ] `CHANGELOG.md` has `### Fixed (SN)` entry under `## [Unreleased]`",
        "- [ ] `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` updated (today's date)",
        "- [ ] `python scripts/ci/auto_fix_common_issues.py --check-only` → 0 auto-fixable issues",
        "- [ ] `python scripts/ci/mypy_baseline.py --require-baseline` → passes",
        "- [ ] No `${{ }}` inside `run: |` blocks in changed workflow files",
        "",
        "_Generated by `scripts/ci/pre_session_context.py` (P6-B, S297)_",
    ])

    full = "\n\n".join([header, sec_a, sec_b, sec_c, sec_d, sec_e, footer])
    exit_code = 1 if (failing or blocking) else 0
    return full, exit_code


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Copilot pre-session context briefing (always run first)"
    )
    parser.add_argument("--pr", required=True, type=int, help="PR number")
    parser.add_argument("--sha", required=True, help="HEAD commit SHA")
    parser.add_argument("--repo", default=f"{_OWNER}/{_REPO}", help="owner/repo")
    parser.add_argument(
        "--output-file", dest="output_file", metavar="FILE",
        help="Write briefing to this file instead of stdout"
    )
    parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Output JSON summary (blocking count, failing count) instead of full markdown"
    )
    args = parser.parse_args()

    token = _token()
    if not token:
        print(
            "::error::No GitHub token found. "
            "Set GH_TOKEN, GITHUB_TOKEN, CODEX_MASTER_KEY, or CODEX_BACKUP_KEY.",
            file=sys.stderr,
        )
        return 2

    briefing, exit_code = build_briefing(args.pr, args.sha, args.repo, token)

    if args.as_json:
        # Parse counts from the assembled text (quick and dirty but avoids re-running API calls)
        owner, repo_name = args.repo.split("/", 1)
        _, failing, in_prog = section_a_workflow_status(owner, repo_name, args.sha, token)
        _, blocking = section_b_blocking_comments(args.pr, args.repo, token)
        print(json.dumps({
            "pr": args.pr,
            "sha": args.sha[:12],
            "failing_checks": len(failing),
            "in_progress_checks": len(in_prog),
            "blocking_comments": len(blocking),
            "exit_code": exit_code,
        }, indent=2))
    elif args.output_file:
        Path(args.output_file).write_text(briefing, encoding="utf-8")
        print(f"[pre_session_context] Briefing written to {args.output_file}", file=sys.stderr)
        print(briefing)  # also print to stdout for GitHub Actions step summary
    else:
        print(briefing)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
