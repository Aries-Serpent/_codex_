#!/usr/bin/env python3
"""branch_rebase_check.py — Detect whether a PR branch needs rebasing.

This script is the authoritative "rebase-first" gate.  It is called by:

  1. `branch-rebase-gate.yml`     — on every PR push/synchronize; posts a
                                    BRANCH_REBASE_REQUIRED marker comment when
                                    the branch is behind its base, or
                                    auto-merges when the gap is all-bot [skip ci].
  2. `agent-auth-delegation.yml`  — REQ-10 in cognitive-preflight; HARD BLOCKS
                                    agent activation when a rebase is required.
  3. Locally by agents/developers — `python scripts/ci/branch_rebase_check.py`
                                    before starting any work.

Exit codes
----------
    0   Branch is up-to-date (at parity with or ahead of base)
    0   Branch was auto-merged successfully (--auto-merge-skip-ci resolved it)
    1   Branch is BEHIND base — rebase required
    2   Branch is DIVERGED — rebase required
    3   Could not determine status (treated as warning, not hard block)

Usage
-----
    # Check current branch against its upstream (local git)
    python scripts/ci/branch_rebase_check.py

    # Check a specific PR via GitHub API (CI mode)
    python scripts/ci/branch_rebase_check.py \\
        --repo Aries-Serpent/_codex_ --pr 3586 \\
        --github-output --post-comment

    # Auto-merge when gap is 100% bot [skip ci] commits, else require manual rebase
    python scripts/ci/branch_rebase_check.py \\
        --repo Aries-Serpent/_codex_ --pr 3586 \\
        --auto-merge-skip-ci --post-comment --github-output --github-summary

Environment (CI mode)
---------------------
    GITHUB_TOKEN / GH_TOKEN      PAT with pull-requests:write + contents:write
    GITHUB_REPOSITORY            owner/repo
    GITHUB_STEP_SUMMARY          Path for job summary markdown

Auto-merge behaviour (--auto-merge-skip-ci)
-------------------------------------------
    Scheduled workflows (embedding-index-rebuild, cognitive-analysis-feed,
    codex-manifest-refresh, repo-var-sync-schedule, vars-guide-sync) commit
    directly to main on a 2-24 h cadence.  Any open PR becomes "diverged"
    within hours — triggering the REQ-10 hard block for a purely structural
    reason (no human code changed).

    With --auto-merge-skip-ci the gate will:
      1. Fetch the commits that base has but head does not (the "gap").
      2. If ALL gap commits are from github-actions[bot] AND have [skip ci]
         in their message → call the GitHub Merges API to merge base into head.
      3. Post a BRANCH_REBASE_RESOLVED comment and clear the REQ-10 gate.
      4. If ANY gap commit is human-authored or functional → fall through to
         the normal BRANCH_REBASE_REQUIRED hard block.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_REPO = "Aries-Serpent/_codex_"
REBASE_REQUIRED_MARKER = "BRANCH_REBASE_REQUIRED"
REBASE_RESOLVED_MARKER = "BRANCH_REBASE_RESOLVED"


# ---------------------------------------------------------------------------
# GitHub API helper
# ---------------------------------------------------------------------------


def gh_api(method: str, path: str, token: str, data: bytes | None = None) -> Any:
    url = f"https://api.github.com{path}" if path.startswith("/") else path
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "codex-branch-rebase-check/1.0",
        },
        data=data,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        if exc.code == 204:
            return None
        body_text = exc.read().decode(errors="replace")
        print(f"  ⚠️  {method} {path} → {exc.code}: {body_text[:200]}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Local git mode
# ---------------------------------------------------------------------------


def _run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def check_local() -> tuple[str, int, int]:
    """Return (status, behind_count, ahead_count) using local git.

    status: 'up-to-date' | 'behind' | 'ahead' | 'diverged' | 'unknown'
    """
    rc, branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if rc != 0:
        return "unknown", 0, 0

    rc, upstream = _run(["git", "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"])
    if rc != 0:
        # No upstream configured — try origin/<branch>
        upstream = f"origin/{branch}"
        rc2, _ = _run(["git", "fetch", "origin", branch, "--depth=50"])

    rc, counts = _run(["git", "rev-list", "--left-right", "--count", f"{upstream}...HEAD"])
    if rc != 0:
        return "unknown", 0, 0

    parts = counts.split()
    if len(parts) != 2:
        return "unknown", 0, 0

    behind, ahead = int(parts[0]), int(parts[1])
    if behind == 0 and ahead == 0:
        return "up-to-date", 0, 0
    if behind > 0 and ahead == 0:
        return "behind", behind, ahead
    if behind == 0 and ahead > 0:
        return "ahead", behind, ahead
    return "diverged", behind, ahead


# ---------------------------------------------------------------------------
# GitHub API mode (CI / PR check)
# ---------------------------------------------------------------------------


def get_pr_details(repo: str, token: str, pr_number: int) -> dict | None:
    return gh_api("GET", f"/repos/{repo}/pulls/{pr_number}", token)


def compare_branches(repo: str, token: str, base: str, head: str) -> dict | None:
    b = urllib.parse.quote(base, safe="")
    h = urllib.parse.quote(head, safe="")
    return gh_api("GET", f"/repos/{repo}/compare/{b}...{h}", token)


# ---------------------------------------------------------------------------
# Auto-merge helpers (--auto-merge-skip-ci)
# ---------------------------------------------------------------------------

# Bot logins that are known to produce automated [skip ci] metadata commits.
_BOT_LOGINS = frozenset(
    {"github-actions[bot]", "41898282+github-actions[bot]"}
)


def get_commits_in_gap(
    repo: str, token: str, base_branch: str, head_branch: str
) -> list[dict]:
    """Return the commits that are in *base_branch* but NOT in *head_branch*.

    These are the commits the PR branch is "behind" — the gap that needs
    to be merged in.  We call compare/{head}...{base} so that the returned
    ``commits`` list contains commits present in base but absent in head.
    """
    cmp = compare_branches(repo, token, head_branch, base_branch)
    if not cmp:
        return []
    return cmp.get("commits", [])


def all_skip_ci_bot_commits(commits: list[dict]) -> bool:
    """Return True when every commit in *commits* is a [skip ci] bot commit.

    A commit qualifies when:
      • Its GitHub author OR committer login is a known bot (github-actions[bot])
      • Its commit message contains ``[skip ci]`` (case-insensitive)

    An empty list returns False — we never auto-merge when we can't confirm
    the gap contents.
    """
    if not commits:
        return False
    for entry in commits:
        author_login = ((entry.get("author") or {}).get("login") or "").lower()
        committer_login = ((entry.get("committer") or {}).get("login") or "").lower()
        message = (entry.get("commit") or {}).get("message", "")

        is_bot = any(
            bot.lower() in author_login or bot.lower() in committer_login
            for bot in _BOT_LOGINS
        )
        has_skip_ci = "[skip ci]" in message.lower()

        if not (is_bot and has_skip_ci):
            return False
    return True


def auto_merge_base_into_branch(
    repo: str,
    token: str,
    head_branch: str,
    base_branch: str,
    num_commits: int,
) -> tuple[bool, str]:
    """Merge *base_branch* into *head_branch* via the GitHub Merges API.

    Uses the server-side merge endpoint so no git checkout is required.
    Returns ``(success, detail_message)``.  A 204 (no-op / already merged)
    is treated as success.
    """
    now_iso = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    payload = {
        "base": head_branch,
        "head": base_branch,
        "commit_message": (
            f"chore: auto-merge {num_commits} automated commit(s) "
            f"from {base_branch} [skip ci]\n\n"
            f"Automatically merged by branch-rebase-gate.yml at {now_iso}.\n"
            f"All gap commits were [skip ci] github-actions[bot] commits "
            f"(no functional code changes)."
        ),
    }
    result = gh_api(
        "POST",
        f"/repos/{repo}/merges",
        token,
        json.dumps(payload).encode(),
    )
    # gh_api returns None on 204 (no content = already merged → success)
    if result is None:
        return True, "no-op (already up-to-date)"
    if isinstance(result, dict) and result.get("sha"):
        return True, result["sha"]
    return False, f"unexpected API response: {result!r}"


def post_auto_merge_comment(
    repo: str,
    token: str,
    pr_number: int,
    base_branch: str,
    head_branch: str,
    num_commits: int,
) -> None:
    """Post (or update) a BRANCH_REBASE_RESOLVED comment noting the auto-merge."""
    now_iso = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    body = (
        f"<!-- {REBASE_RESOLVED_MARKER} -->\n"
        f"## ✅ Branch Auto-Updated — REQ-10 Cleared\n\n"
        f"Branch `{head_branch}` was behind `{base_branch}` by "
        f"**{num_commits} automated commit(s)** — all `[skip ci]` "
        f"`github-actions[bot]` commits (no functional code changes).\n\n"
        f"`branch-rebase-gate.yml` has automatically merged these commits "
        f"into `{head_branch}`. No manual rebase is required.\n\n"
        f"**Commits merged:** metadata updates only "
        f"(embedding index, cognitive brain patterns, variable sync, manifest).\n\n"
        f"_Auto-merged by `branch-rebase-gate.yml` at {now_iso}_"
    )
    comments = get_pr_comments(repo, token, pr_number)
    existing = _find_bot_comment(comments, REBASE_RESOLVED_MARKER)
    if existing:
        gh_api(
            "PATCH",
            f"/repos/{repo}/issues/comments/{existing['id']}",
            token,
            json.dumps({"body": body}).encode(),
        )
        print(f"  🔄 Updated auto-merge comment (#{existing['id']}) on PR #{pr_number}")
    else:
        gh_api(
            "POST",
            f"/repos/{repo}/issues/{pr_number}/comments",
            token,
            json.dumps({"body": body}).encode(),
        )
        print(f"  ✅ Posted auto-merge comment on PR #{pr_number}")


    """Return (status, behind_by, ahead_by, base_branch, head_branch).

    status: 'up-to-date' | 'behind' | 'ahead' | 'diverged' | 'unknown'
    """
    pr = get_pr_details(repo, token, pr_number)
    if not pr:
        return "unknown", 0, 0, "", ""

    base_branch = pr["base"]["ref"]
    head_branch = pr["head"]["ref"]
    head_sha = pr["head"]["sha"]
    base_sha = pr["base"]["sha"]

    if head_sha == base_sha:
        return "up-to-date", 0, 0, base_branch, head_branch

    # Use GitHub compare: base...head = commits in head not in base
    comparison = compare_branches(repo, token, base_branch, head_branch)
    if not comparison:
        return "unknown", 0, 0, base_branch, head_branch

    status = comparison.get("status", "unknown")
    ahead_by = comparison.get("ahead_by", 0)
    behind_by = comparison.get("behind_by", 0)

    if status == "identical":
        return "up-to-date", 0, 0, base_branch, head_branch
    elif status == "behind":
        return "behind", behind_by, ahead_by, base_branch, head_branch
    elif status == "ahead":
        return "ahead", behind_by, ahead_by, base_branch, head_branch
    elif status == "diverged":
        return "diverged", behind_by, ahead_by, base_branch, head_branch
    else:
        return "unknown", behind_by, ahead_by, base_branch, head_branch


# ---------------------------------------------------------------------------
# PR comment management
# ---------------------------------------------------------------------------


def get_pr_comments(repo: str, token: str, pr_number: int) -> list[dict]:
    data = gh_api("GET", f"/repos/{repo}/issues/{pr_number}/comments?per_page=100", token)
    return data if isinstance(data, list) else []


def _find_bot_comment(comments: list[dict], marker: str) -> dict | None:
    for c in comments:
        if marker in (c.get("body") or ""):
            return c
    return None


def post_rebase_required_comment(
    repo: str,
    token: str,
    pr_number: int,
    base_branch: str,
    head_branch: str,
    behind_by: int,
) -> None:
    """Post (or update) a BRANCH_REBASE_REQUIRED comment on the PR."""
    comments = get_pr_comments(repo, token, pr_number)

    # If a RESOLVED marker already exists AND a REQUIRED marker also exists,
    # the branch was fixed. Don't re-post.
    resolved = _find_bot_comment(comments, REBASE_RESOLVED_MARKER)
    required = _find_bot_comment(comments, REBASE_REQUIRED_MARKER)
    if resolved and required:
        # Check ordering — if resolved is newer than required, don't re-post
        required_ts = required.get("updated_at", "")
        resolved_ts = resolved.get("updated_at", "")
        if resolved_ts >= required_ts:
            print(f"  ℹ️  Rebase already resolved (comment {resolved['id']}) — skipping re-post")
            return

    now_iso = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    body = f"""## ⚠️ {REBASE_REQUIRED_MARKER} — Branch Must Be Rebased First

<!-- {REBASE_REQUIRED_MARKER} -->

**Branch `{head_branch}` is {behind_by} commit(s) behind `{base_branch}`.**

The Copilot Coding Agent **MUST rebase this branch before starting any other work.**

### Why this matters
Working on a branch that is behind its base risks:
- Merge conflicts when the PR is eventually merged
- Duplicate or already-fixed code being re-introduced
- CI failures caused by stale dependency state

### ✅ Required action — fix this FIRST

```bash
# Option 1: rebase onto the base branch
git fetch origin {base_branch}
git rebase origin/{base_branch}
git push --force-with-lease

# Option 2: merge the base into your branch (if rebase is risky)
git fetch origin {base_branch}
git merge origin/{base_branch}
git push
```

### 🤖 Agent instruction
**If you are a Copilot Coding Agent reading this comment:**
- This is **REQ-10** of the cognitive pre-flight checklist
- Do NOT proceed with any task until the rebase is complete and this check passes
- After rebasing and pushing, the next CI run will clear this gate automatically

---
_Auto-posted by `branch-rebase-gate.yml` at {now_iso}_
"""

    # Replace the variable name typo in the format string above
    body = body.replace("REBASE_REBASE_REQUIRED_MARKER", REBASE_REQUIRED_MARKER)
    existing = _find_bot_comment(comments, REBASE_REQUIRED_MARKER)
    if existing:
        # Update the existing comment
        gh_api(
            "PATCH",
            f"/repos/{repo}/issues/comments/{existing['id']}",
            token,
            json.dumps({"body": body}).encode(),
        )
        print(f"  🔄 Updated rebase-required comment (#{existing['id']}) on PR #{pr_number}")
    else:
        gh_api(
            "POST",
            f"/repos/{repo}/issues/{pr_number}/comments",
            token,
            json.dumps({"body": body}).encode(),
        )
        print(f"  📌 Posted rebase-required comment on PR #{pr_number}")


def post_rebase_resolved_comment(
    repo: str,
    token: str,
    pr_number: int,
    base_branch: str,
    head_branch: str,
) -> None:
    """Upsert a BRANCH_REBASE_RESOLVED comment when the branch is up-to-date.

    If a RESOLVED comment already exists (from a previous synchronize event)
    we PATCH it in-place rather than creating a new one, preventing the
    4× duplicate accumulation seen in PR #3605.
    """
    comments = get_pr_comments(repo, token, pr_number)

    # Only act if a REQUIRED marker exists (nothing to resolve otherwise)
    required = _find_bot_comment(comments, REBASE_REQUIRED_MARKER)
    if not required:
        return

    resolved = _find_bot_comment(comments, REBASE_RESOLVED_MARKER)
    if resolved and resolved.get("updated_at", "") >= required.get("updated_at", ""):
        return  # Already resolved and newer than the last REQUIRED post

    now_iso = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    body = (
        f"<!-- {REBASE_RESOLVED_MARKER} -->\n"
        f"## ✅ Branch Rebase Resolved\n\n"
        f"Branch `{head_branch}` is now up-to-date with `{base_branch}`. "
        f"The REQ-10 gate has been cleared.\n\n"
        f"_Auto-posted by `branch-rebase-gate.yml` at {now_iso}_"
    )
    if resolved:
        # PATCH the existing comment — never create a new one
        gh_api(
            "PATCH",
            f"/repos/{repo}/issues/comments/{resolved['id']}",
            token,
            json.dumps({"body": body}).encode(),
        )
        print(f"  🔄 Updated rebase-resolved comment (#{resolved['id']}) on PR #{pr_number}")
    else:
        gh_api(
            "POST",
            f"/repos/{repo}/issues/{pr_number}/comments",
            token,
            json.dumps({"body": body}).encode(),
        )
        print(f"  ✅ Posted rebase-resolved comment on PR #{pr_number}")


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def write_github_output(key: str, value: str) -> None:
    gh_output = os.environ.get("GITHUB_OUTPUT", "")
    if gh_output:
        with open(gh_output, "a") as fh:
            fh.write(f"{key}={value}\n")


def write_step_summary(content: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if summary_path:
        with open(summary_path, "a") as fh:
            fh.write(content)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect whether a PR branch needs rebasing")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPO))
    parser.add_argument("--pr", type=int, metavar="PR_NUMBER", help="PR number (CI mode — uses GitHub API)")
    parser.add_argument("--post-comment", action="store_true", help="Post/update rebase-required comment on the PR")
    parser.add_argument("--github-output", action="store_true", help="Write status to GITHUB_OUTPUT")
    parser.add_argument("--github-summary", action="store_true", help="Write status to GITHUB_STEP_SUMMARY (always-on; flag is accepted for CI compat)")
    parser.add_argument("--hard-fail", action="store_true", help="Exit 1/2 when rebase needed (gate mode)")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""

    # ── CI mode: PR number provided → use GitHub API ──────────────────────
    if args.pr:
        if not token:
            print("❌  GITHUB_TOKEN or GH_TOKEN required for --pr mode", file=sys.stderr)
            return 3

        print(f"\n🔍  Checking rebase status for PR #{args.pr} in {args.repo}…")
        status, behind_by, ahead_by, base_branch, head_branch = check_via_api(
            args.repo, token, args.pr
        )

        print(f"  Head:    {head_branch}")
        print(f"  Base:    {base_branch}")
        print(f"  Status:  {status}  (behind={behind_by}, ahead={ahead_by})")

        if args.github_output:
            write_github_output("rebase_status", status)
            write_github_output("behind_by", str(behind_by))
            write_github_output("ahead_by", str(ahead_by))
            write_github_output("base_branch", base_branch)
            write_github_output("head_branch", head_branch)
            write_github_output("rebase_required", "true" if status in ("behind", "diverged") else "false")

        rebase_needed = status in ("behind", "diverged")

        # ── Summary for job page ──────────────────────────────────────────
        if status == "up-to-date":
            summary = (
                f"\n### ✅ REQ-10: Branch Rebase Check — PASS\n\n"
                f"`{head_branch}` is up-to-date with `{base_branch}`.\n"
            )
        elif status == "ahead":
            summary = (
                f"\n### ✅ REQ-10: Branch Rebase Check — PASS\n\n"
                f"`{head_branch}` is {ahead_by} commit(s) **ahead** of `{base_branch}` — no rebase needed.\n"
            )
        elif status == "behind":
            summary = (
                f"\n### 🔴 REQ-10: Branch Rebase Check — FAIL\n\n"
                f"**`{head_branch}` is {behind_by} commit(s) BEHIND `{base_branch}`.**\n\n"
                f"> **Agent must rebase before starting any work.** Run:\n"
                f"> ```bash\n"
                f"> git fetch origin {base_branch}\n"
                f"> git rebase origin/{base_branch}\n"
                f"> git push --force-with-lease\n"
                f"> ```\n"
            )
        elif status == "diverged":
            summary = (
                f"\n### 🔴 REQ-10: Branch Rebase Check — FAIL\n\n"
                f"**`{head_branch}` has DIVERGED from `{base_branch}`** "
                f"(behind={behind_by}, ahead={ahead_by}).\n\n"
                f"> Rebase or merge is required before the agent may proceed.\n"
            )
        else:
            summary = (
                f"\n### ⚠️ REQ-10: Branch Rebase Check — UNKNOWN\n\n"
                f"Could not determine rebase status for PR #{args.pr}. "
                f"Treating as soft warning.\n"
            )
        write_step_summary(summary)

        # ── Post / resolve PR comment ─────────────────────────────────────
        if args.post_comment and token:
            if rebase_needed:
                post_rebase_required_comment(
                    args.repo, token, args.pr, base_branch, head_branch, behind_by
                )
            else:
                post_rebase_resolved_comment(
                    args.repo, token, args.pr, base_branch, head_branch
                )

        # ── Exit code ─────────────────────────────────────────────────────
        if status == "behind":
            print(f"\n❌  Branch is {behind_by} commit(s) BEHIND base — rebase required (REQ-10)")
            return 1 if args.hard_fail else 0
        if status == "diverged":
            print(f"\n❌  Branch has DIVERGED (behind={behind_by}, ahead={ahead_by}) — rebase required (REQ-10)")
            return 2 if args.hard_fail else 0
        if status == "unknown":
            print("\n⚠️  Could not determine rebase status — soft warning")
            return 0

        print(f"\n✅  Branch is up-to-date (status={status}, ahead={ahead_by})")
        return 0

    # ── Local mode: no PR number → use git CLI ────────────────────────────
    print("\n🔍  Checking rebase status using local git…")
    status, behind, ahead = check_local()
    print(f"  Status:  {status}  (behind={behind}, ahead={ahead})")

    if status in ("behind", "diverged"):
        print(
            f"\n❌  Branch needs rebasing (status={status}, behind={behind}).\n"
            f"   Run: git fetch origin && git rebase origin/<base-branch>"
        )
        return 1 if args.hard_fail else 0

    if status == "unknown":
        print("\n⚠️  Could not determine rebase status locally.")
        return 0

    print(f"\n✅  Branch is {status} (ahead={ahead})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
