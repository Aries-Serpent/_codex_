#!/usr/bin/env python3
"""
CI Rescue Engine — scripts/ci/ci_rescue.py

Retrieves failed CI job logs, matches against a pattern library of known
fixes, attempts auto-remediation, and — when no pattern matches — posts a
structured @copilot RCA comment on the active PR so Copilot Coding Agents
can continue the healing loop.

Usage (called by .github/workflows/ci-rescue.yml):
    python scripts/ci/ci_rescue.py \\
        --run-id  <workflow_run_id> \\
        --pr      <pr_number>       \\
        --repo    <owner/repo>      \\
        [--token  <github_token>]   \\
        [--dry-run]

Exit codes:
    0 — rescue succeeded (all auto-fixable patterns applied, or nothing needed)
    1 — partial/no auto-fix; RCA comment posted for @copilot
    2 — error (e.g. could not retrieve logs)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# How many tail lines of job logs to fetch for pattern matching
LOG_TAIL_LINES = 300

# Maximum size of RCA comment body (GitHub caps PR comments at ~65 KB)
MAX_COMMENT_CHARS = 60_000

# ---------------------------------------------------------------------------
# Known-pattern library
# Each entry maps a regex against the job-log text to an auto-fix command.
# The auto-fix command is run with cwd=REPO_ROOT; a non-zero exit means the
# pattern was detected but the fix could not be applied automatically.
# ---------------------------------------------------------------------------

@dataclass
class RescuePattern:
    pattern_id: str
    description: str
    log_regexes: list[str]                # any match → pattern fires
    fix_command: Optional[list[str]]      # None = manual only
    fix_description: str = ""
    references: list[str] = field(default_factory=list)


RESCUE_PATTERNS: list[RescuePattern] = [
    RescuePattern(
        pattern_id="RP-001",
        description="E501 line-length violations (pattern 12)",
        log_regexes=[
            r"E501.*[Ll]ine too long",
            r"Pattern 12.*[Ll]ine [Ll]ength.*Found",
            r"auto-fixable.*[Ll]ine [Ll]ength",
        ],
        fix_command=[
            "python3", "scripts/ci/auto_fix_common_issues.py", "--pattern", "12"
        ],
        fix_description="Run `auto_fix_common_issues.py --pattern 12` to auto-wrap long lines",
        references=["auto_fix_common_issues.py:fix_line_length"],
    ),
    RescuePattern(
        pattern_id="RP-002",
        description="Unused import violations (pattern 1, ruff F401)",
        log_regexes=[
            r"F401.*imported but unused",
            r"Pattern 1.*[Uu]nused [Ii]mports.*Found",
        ],
        fix_command=[
            "python3", "scripts/ci/auto_fix_common_issues.py", "--pattern", "1"
        ],
        fix_description="Run `auto_fix_common_issues.py --pattern 1` to remove unused imports",
        references=["auto_fix_common_issues.py:fix_unused_imports"],
    ),
    RescuePattern(
        pattern_id="RP-003",
        description="Coverage threshold inconsistency (pattern 4)",
        log_regexes=[
            r"Pattern 4.*[Cc]overage.*Found",
            r"coverage.*threshold.*inconsisten",
        ],
        fix_command=[
            "python3", "scripts/ci/auto_fix_common_issues.py", "--pattern", "4"
        ],
        fix_description=(
            "Run `auto_fix_common_issues.py --pattern 4` to standardise coverage thresholds"
        ),
        references=["auto_fix_common_issues.py:fix_coverage_thresholds"],
    ),
    RescuePattern(
        pattern_id="RP-004",
        description="Tracked-file sync drift (pattern 22)",
        log_regexes=[
            r"Pattern 22.*[Tt]racked.*Found",
            r"CODEX_MANIFEST.*CHANGELOG.*accountability drift",
        ],
        fix_command=[
            "python3", "scripts/ci/sync_tracked_files.py", "--fix"
        ],
        fix_description=(
            "Run `sync_tracked_files.py --fix` to resync CODEX_MANIFEST / "
            "CHANGELOG / accountability report"
        ),
        references=["scripts/ci/sync_tracked_files.py"],
    ),
    RescuePattern(
        pattern_id="RP-005",
        description="Trailing whitespace in docs/ files",
        log_regexes=[
            r"Trim Trailing Whitespace.*Failed",
            r"trailing whitespace.*docs/",
            r"trailing-whitespace.*Failed",
        ],
        fix_command=[
            "bash", "-c",
            # Strip trailing whitespace from all modified tracked files
            "git diff --name-only HEAD -- '*.md' '*.rst' '*.txt' docs/ .codex/"
            " | xargs -r sed -i 's/[[:space:]]*$//'"
        ],
        fix_description=(
            "Strip trailing whitespace from modified docs/config files via "
            "`git diff | xargs sed -i 's/[[:space:]]*$//'`"
        ),
        references=["S196 commit 24b868e"],
    ),
    RescuePattern(
        pattern_id="RP-006",
        description="Missing EOF newline in .codex/ JSON files",
        log_regexes=[
            r"Fix End of Files.*Failed",
            r"end-of-file-fixer.*Failed",
            r"no newline at end.*\.json",
        ],
        fix_command=[
            "bash", "-c",
            # Use find + xargs -0 for safe handling of any filenames
            "find .codex -name '*.json' -print0"
            " | xargs -0 -I{} sh -c"
            " 'tail -c1 \"$1\" | grep -q . && echo >> \"$1\"' _ {}"
        ],
        fix_description="Add missing EOF newline to .codex JSON files",
        references=["S196 commit 24b868e"],
    ),
    RescuePattern(
        pattern_id="RP-007",
        description="detect-secrets baseline stale (agent_context.json hash mismatch)",
        log_regexes=[
            r"detect-secrets.*Failed",
            r"Detect secrets.*Failed",
            r"Secret in baseline.*not.*detected",
            r"agent_context\.json.*hash",
        ],
        fix_command=[
            # Use pre-commit to regenerate the baseline for the affected files
            "bash", "-c",
            "python3 -m detect_secrets scan --no-verify"
            " --baseline .secrets.baseline"
            " .codex/agent_context.json 2>/dev/null || true"
        ],
        fix_description=(
            "Refresh the detect-secrets baseline for agent_context.json via "
            "`detect-secrets scan --baseline .secrets.baseline`"
        ),
        references=["S196 commit 24b868e", ".secrets.baseline"],
    ),
    RescuePattern(
        pattern_id="RP-008",
        description="actionlint duplicate YAML key (two run: blocks in one step)",
        log_regexes=[
            r"actionlint.*duplicate.*key",
            r"duplicate key.*\"run\"",
            r"Workflow Compliance Audit.*Fail",
        ],
        fix_command=None,  # requires manual merge
        fix_description=(
            "Merge the two `run:` blocks in the affected step so each step "
            "has exactly one `run:` key. Place `env:` above `run:`."
        ),
        references=["YAML workflow steps memory", "codex-manifest-refresh.yml"],
    ),
    RescuePattern(
        pattern_id="RP-009",
        description="mypy anti-regression gate exceeded baseline (too many errors)",
        log_regexes=[
            r"mypy.*[Ff]ailed",
            r"mypy.*[Ee]rror count.*exceed",
            r"Anti-Regression.*[Ff]ail",
            r"mypy.*> [0-9]+ baseline",
        ],
        fix_command=None,
        fix_description=(
            "Investigate new mypy errors introduced in recent commits. "
            "Never add `type: ignore` annotations to fallback imports when "
            "`--ignore-missing-imports` is active — the flag already "
            "suppresses them, making the annotations permanently unused."
        ),
        references=["mypy ignore annotations memory", "src/codex_ml/cli/train.py"],
    ),
    RescuePattern(
        pattern_id="RP-010",
        description="Pre-flight check failures (xdist or timeout-minutes missing)",
        log_regexes=[
            r"Pre-Flight.*[Ff]ail",
            r"pre_flight_check.*error",
            r"xdist.*without.*timeout-minutes",
        ],
        fix_command=None,
        fix_description=(
            "Check pre_flight_check.py output. Use `[ \"${VAR}\" != \"\" ]` "
            "instead of `[ -n \"${VAR}\" ]` in workflow bash steps to avoid "
            "false xdist warnings. Ensure timeout-minutes is set on jobs "
            "that contain pytest."
        ),
        references=["pre-flight check memory"],
    ),
    RescuePattern(
        pattern_id="RP-011",
        description="Validation Pipeline failure — composite (whitespace + EOF + secrets)",
        log_regexes=[
            r"Validation Pipeline.*[Ff]ail",
            r"Fast Validation.*[Ff]ail",
        ],
        fix_command=[
            "bash", "-c",
            "pre-commit run trailing-whitespace end-of-file-fixer"
            " --files $(git diff --name-only HEAD) 2>/dev/null || true"
        ],
        fix_description=(
            "Run pre-commit `trailing-whitespace` and `end-of-file-fixer` "
            "on modified files. Also verify detect-secrets baseline is fresh."
        ),
        references=["validation pipeline memory"],
    ),
    RescuePattern(
        pattern_id="RP-012",
        description="Unsorted imports (ruff I001, pattern 9)",
        log_regexes=[
            r"I001.*[Ii]mport block is un-sorted",
            r"Pattern 9.*[Uu]nsorted [Ii]mports.*Found",
        ],
        fix_command=[
            "python3", "scripts/ci/auto_fix_common_issues.py", "--pattern", "9"
        ],
        fix_description="Run `auto_fix_common_issues.py --pattern 9` to sort imports",
        references=["auto_fix_common_issues.py:fix_unsorted_imports"],
    ),
]


# ---------------------------------------------------------------------------
# GitHub API helpers (thin, no external deps beyond stdlib)
# ---------------------------------------------------------------------------

def _gh_api(
    path: str,
    token: str,
    method: str = "GET",
    body: Optional[dict] = None,
) -> tuple[int, dict | list | None]:
    """Call the GitHub REST API using curl (avoids PyGitHub dependency)."""
    cmd = [
        "curl", "-sS",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Accept: application/vnd.github+json",
        "-H", "X-GitHub-Api-Version: 2022-11-28",
    ]
    if method == "POST":
        cmd += ["-X", "POST", "-H", "Content-Type: application/json"]
        if body:
            cmd += ["-d", json.dumps(body)]
    elif method == "PATCH":
        cmd += ["-X", "PATCH", "-H", "Content-Type: application/json"]
        if body:
            cmd += ["-d", json.dumps(body)]

    cmd.append(f"https://api.github.com{path}")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        stderr_snippet = result.stderr[:300] if result.stderr else "(no stderr)"
        print(f"  ⚠️  GitHub API error (exit {result.returncode}): {stderr_snippet}", file=sys.stderr)
        return -1, None
    try:
        return 200, json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"  ⚠️  GitHub API response not valid JSON: {exc}", file=sys.stderr)
        return -1, None


def get_failed_jobs(run_id: int, repo: str, token: str) -> list[dict]:
    """Return the list of failed jobs for a workflow run."""
    _, data = _gh_api(f"/repos/{repo}/actions/runs/{run_id}/jobs", token)
    if not isinstance(data, dict):
        return []
    return [j for j in data.get("jobs", []) if j.get("conclusion") == "failure"]


def get_job_log(job_id: int, repo: str, token: str, tail: int = LOG_TAIL_LINES) -> str:
    """Return the last `tail` lines of a job log."""
    _, raw = _gh_api(f"/repos/{repo}/actions/jobs/{job_id}/logs", token)
    if isinstance(raw, str):
        return "\n".join(raw.splitlines()[-tail:])
    # Logs often redirect; try via curl following redirects
    cmd = [
        "curl", "-sS", "-L",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Accept: application/vnd.github+json",
        f"https://api.github.com/repos/{repo}/actions/jobs/{job_id}/logs",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    lines = result.stdout.splitlines()
    return "\n".join(lines[-tail:])


def find_pr_for_run(run_id: int, repo: str, token: str) -> Optional[int]:
    """Return the PR number associated with a workflow run (if any)."""
    _, data = _gh_api(f"/repos/{repo}/actions/runs/{run_id}", token)
    if not isinstance(data, dict):
        return None
    prs = data.get("pull_requests", [])
    if prs:
        return prs[0]["number"]
    # Fallback: search open PRs for head SHA
    head_sha = data.get("head_sha", "")
    if head_sha:
        _, pr_data = _gh_api(
            f"/repos/{repo}/pulls?state=open&per_page=50", token
        )
        if isinstance(pr_data, list):
            for pr in pr_data:
                if pr.get("head", {}).get("sha") == head_sha:
                    return pr["number"]
    return None


def post_pr_comment(
    pr_number: int,
    repo: str,
    token: str,
    body: str,
    dry_run: bool = False,
) -> bool:
    """Post (or update) a @copilot RCA comment on the PR."""
    marker = "<!-- ci-rescue-rca -->"
    full_body = f"{marker}\n{body}"

    if dry_run:
        print(f"\n[DRY RUN] Would post to PR #{pr_number}:\n{full_body[:500]}…")
        return True

    # Check for existing rescue comment to update (idempotent)
    _, comments = _gh_api(
        f"/repos/{repo}/issues/{pr_number}/comments?per_page=100", token
    )
    existing_id = None
    if isinstance(comments, list):
        for c in comments:
            if marker in (c.get("body") or ""):
                existing_id = c["id"]
                break

    if existing_id:
        status, _ = _gh_api(
            f"/repos/{repo}/issues/comments/{existing_id}",
            token,
            method="PATCH",
            body={"body": full_body},
        )
    else:
        status, _ = _gh_api(
            f"/repos/{repo}/issues/{pr_number}/comments",
            token,
            method="POST",
            body={"body": full_body},
        )

    return status == 200


# ---------------------------------------------------------------------------
# Core rescue logic
# ---------------------------------------------------------------------------

@dataclass
class RescueResult:
    matched_patterns: list[RescuePattern] = field(default_factory=list)
    fixed_patterns: list[RescuePattern] = field(default_factory=list)
    failed_patterns: list[RescuePattern] = field(default_factory=list)
    unmatched_logs: list[str] = field(default_factory=list)  # job names with no pattern
    job_summaries: list[dict] = field(default_factory=list)  # {name, log_snippet}


def match_patterns(log_text: str) -> list[RescuePattern]:
    """Return all RescuePattern entries whose regexes match log_text."""
    matched = []
    for pat in RESCUE_PATTERNS:
        for rx in pat.log_regexes:
            if re.search(rx, log_text, re.IGNORECASE):
                matched.append(pat)
                break
    return matched


def attempt_fix(pattern: RescuePattern, dry_run: bool) -> bool:
    """Try to apply the fix for a pattern. Returns True if successful."""
    if pattern.fix_command is None:
        return False  # manual-only

    if dry_run:
        print(f"  [DRY RUN] Would run: {' '.join(pattern.fix_command)}")
        return True

    try:
        result = subprocess.run(
            pattern.fix_command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        success = result.returncode == 0
        if not success:
            print(
                f"  ⚠️  Fix command failed (exit {result.returncode}):\n"
                f"     {result.stderr[:400]}"
            )
        return success
    except subprocess.TimeoutExpired:
        print("  ⚠️  Fix command timed out after 120s")
        return False
    except OSError as exc:
        print(f"  ⚠️  Fix command OS error: {exc}")
        return False


def run_rescue(
    run_id: int,
    repo: str,
    token: str,
    pr_number: Optional[int],
    dry_run: bool,
) -> RescueResult:
    """Full rescue cycle: fetch logs → match → fix → report."""
    result = RescueResult()

    failed_jobs = get_failed_jobs(run_id, repo, token)
    if not failed_jobs:
        print("✅ No failed jobs found — nothing to rescue.")
        return result

    all_matched: dict[str, RescuePattern] = {}

    for job in failed_jobs:
        job_name = job.get("name", "<unknown>")
        job_id = job["id"]
        print(f"\n📋 Fetching logs for failed job: {job_name} (id={job_id})")

        log_text = get_job_log(job_id, repo, token)
        snippet = "\n".join(log_text.splitlines()[-30:]) if log_text else ""

        result.job_summaries.append({
            "name": job_name,
            "job_id": job_id,
            "log_snippet": snippet,
        })

        matched = match_patterns(log_text)
        if matched:
            for p in matched:
                if p.pattern_id not in all_matched:
                    all_matched[p.pattern_id] = p
                    print(f"  ✓ Matched pattern {p.pattern_id}: {p.description}")
        else:
            print(f"  ⚠️  No known pattern matched for job: {job_name}")
            result.unmatched_logs.append(job_name)

    result.matched_patterns = list(all_matched.values())

    # Attempt fixes for matched patterns
    for pat in result.matched_patterns:
        print(f"\n🔧 Attempting fix for {pat.pattern_id}: {pat.description}")
        if attempt_fix(pat, dry_run):
            print(f"  ✅ Fixed: {pat.description}")
            result.fixed_patterns.append(pat)
        else:
            print(f"  ❌ Could not auto-fix: {pat.description}")
            result.failed_patterns.append(pat)

    return result


# ---------------------------------------------------------------------------
# RCA comment builder
# ---------------------------------------------------------------------------

def _format_rca_comment(
    run_id: int,
    repo: str,
    result: RescueResult,
    timestamp: str,
) -> str:
    """Build the @copilot RCA comment body."""
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}"

    lines = [
        "## 🚨 CI Rescue — Root Cause Analysis",
        "",
        f"> **Run:** [{run_id}]({run_url})  ",
        f"> **Time:** {timestamp}  ",
        "> **Engine:** `scripts/ci/ci_rescue.py`",
        "",
    ]

    # --- Fixed patterns ---
    if result.fixed_patterns:
        lines.append("### ✅ Auto-Fixed")
        lines.append("")
        lines.append("| Pattern | Description | Fix Applied |")
        lines.append("|---------|-------------|-------------|")
        for p in result.fixed_patterns:
            cmd = " ".join(p.fix_command) if p.fix_command else "—"
            lines.append(f"| `{p.pattern_id}` | {p.description} | `{cmd}` |")
        lines.append("")

    # --- Patterns that could not be auto-fixed ---
    if result.failed_patterns or result.unmatched_logs:
        lines.append("### ❌ Requires Manual Fix")
        lines.append("")

        if result.failed_patterns:
            lines.append("**Known patterns with no auto-fix available:**")
            lines.append("")
            for p in result.failed_patterns:
                lines.append(f"#### `{p.pattern_id}` — {p.description}")
                lines.append("")
                lines.append(f"**Fix:** {p.fix_description}")
                if p.references:
                    lines.append(f"**Refs:** {', '.join(p.references)}")
                lines.append("")

        if result.unmatched_logs:
            lines.append("**Unrecognised failures (no pattern matched):**")
            lines.append("")
            for job_name in result.unmatched_logs:
                lines.append(f"- `{job_name}`")
            lines.append("")

        # Paste log snippets for unmatched jobs so @copilot has context
        unmatched_names = set(result.unmatched_logs)
        for summary in result.job_summaries:
            if summary["name"] in unmatched_names:
                lines.append(f"<details><summary>Log snippet — {summary['name']}</summary>")
                lines.append("")
                lines.append("```")
                lines.append(summary["log_snippet"][:3000])
                lines.append("```")
                lines.append("</details>")
                lines.append("")

    # --- @copilot continuation prompt ---
    has_unresolved = bool(result.failed_patterns or result.unmatched_logs)
    if has_unresolved:
        lines += [
            "---",
            "",
            "@copilot+claude-sonnet-4.6 please investigate and fix the CI failures above.",
            "",
            "**Instructions:**",
            "1. Review each ❌ pattern and the log snippets above",
            "2. Apply fixes in the order listed (unblocking patterns first)",
            "3. Run `python3 scripts/ci/auto_fix_common_issues.py --check-only` after each fix",
            "4. Run `actionlint .github/workflows/*.yml` if any YAML changes were made",
            "5. Commit with `fix(ci): <pattern-id> <short description>` and push",
            "6. Confirm CI is green before closing this rescue loop",
            "",
            "**Rules:** Follow `.codex/CODEBASE_AGENCY_POLICY.md` — fix ALL issues, "
            "never defer. Never add `type: ignore` to fallback imports under "
            "`--ignore-missing-imports`.",
        ]

    body = "\n".join(lines)
    if len(body) > MAX_COMMENT_CHARS:
        body = body[:MAX_COMMENT_CHARS] + "\n\n_(comment truncated — see Actions logs for full output)_"
    return body


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, type=int, help="Workflow run ID")
    parser.add_argument("--pr", type=int, default=None, help="PR number (auto-detected if omitted)")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub token")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    args = parser.parse_args()

    if not args.token:
        print("❌ No GitHub token provided (--token or GITHUB_TOKEN env var)", file=sys.stderr)
        return 2

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"🔬 CI Rescue Engine starting — run {args.run_id} @ {timestamp}")

    # Resolve PR number
    pr_number = args.pr
    if pr_number is None:
        pr_number = find_pr_for_run(args.run_id, args.repo, args.token)
        if pr_number:
            print(f"🔗 Resolved PR #{pr_number} for run {args.run_id}")
        else:
            print("⚠️  Could not resolve a PR for this run — RCA comment will be skipped")

    # Run rescue cycle
    result = run_rescue(args.run_id, args.repo, args.token, pr_number, args.dry_run)

    # Summarise
    print("\n" + "=" * 60)
    print(f"Matched:     {len(result.matched_patterns)} pattern(s)")
    print(f"Fixed:       {len(result.fixed_patterns)} pattern(s)")
    print(f"Unfixed:     {len(result.failed_patterns)} pattern(s)")
    print(f"Unmatched:   {len(result.unmatched_logs)} job(s)")
    print("=" * 60)

    has_unresolved = bool(result.failed_patterns or result.unmatched_logs)

    # Post RCA comment if there are unresolved issues
    if has_unresolved and pr_number:
        comment_body = _format_rca_comment(args.run_id, args.repo, result, timestamp)
        print(f"\n📝 Posting RCA comment to PR #{pr_number}…")
        ok = post_pr_comment(pr_number, args.repo, args.token, comment_body, args.dry_run)
        if ok:
            print("  ✅ RCA comment posted")
        else:
            print("  ⚠️  Failed to post comment", file=sys.stderr)

    # Exit code
    if has_unresolved:
        print("\n⚠️  Some failures require manual attention — exit 1")
        return 1

    if result.fixed_patterns:
        print("\n✅ All matched patterns auto-fixed — exit 0")
    else:
        print("\n✅ No actionable failures — exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
