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
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_REPO = "Aries-Serpent/_codex_"
REBASE_REQUIRED_MARKER = "BRANCH_REBASE_REQUIRED"
REBASE_RESOLVED_MARKER = "BRANCH_REBASE_RESOLVED"

# Dashboard integration — matches pr_comment_consolidator.py format exactly
_DASHBOARD_MARKER = "<!-- PR_STATUS_DASHBOARD_v1 -->"
_DASHBOARD_SECTION = "🔀 Branch Rebase Gate"


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
        _rc2, _ = _run(["git", "fetch", "origin", branch, "--depth=50"])

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


# ---------------------------------------------------------------------------
# Gap analysis & rich comment helpers (autonomous self-healing)
# ---------------------------------------------------------------------------

# _BOT_LOGINS is defined once in the auto-merge helpers section above (line ~180).


def classify_gap_commits(commits: list[dict]) -> dict:
    """Split gap commits into bot_skip_ci and functional buckets.

    Returns:
        all_bot_skip_ci (bool): True when every commit is an automated skip-ci commit.
        bot_skip_ci     (list): Commits that are safe to auto-merge.
        functional      (list): Human-authored or non-skip-ci commits.
    """
    bot_skip_ci: list[dict] = []
    functional: list[dict] = []
    for entry in commits:
        author_login = ((entry.get("author") or {}).get("login") or "").lower()
        committer_login = ((entry.get("committer") or {}).get("login") or "").lower()
        message = (entry.get("commit") or {}).get("message", "")
        is_bot = any(
            b.lower() in author_login or b.lower() in committer_login
            for b in _BOT_LOGINS
        )
        if is_bot and "[skip ci]" in message.lower():
            bot_skip_ci.append(entry)
        else:
            functional.append(entry)
    return {
        "all_bot_skip_ci": bool(bot_skip_ci) and not functional,
        "bot_skip_ci": bot_skip_ci,
        "functional": functional,
    }


def get_pr_changed_files(repo: str, token: str, pr_number: int) -> list[str]:
    """Return filenames changed by the PR (up to 100)."""
    data = gh_api("GET", f"/repos/{repo}/pulls/{pr_number}/files?per_page=100", token)
    if not isinstance(data, list):
        return []
    return [f.get("filename", "") for f in data if f.get("filename")]


def get_gap_files(repo: str, token: str, commits: list[dict]) -> set[str]:
    """Return all files touched by the gap commits (up to first 10 commits)."""
    files: set[str] = set()
    for entry in commits[:10]:
        sha = entry.get("sha", "")
        if not sha:
            continue
        detail = gh_api("GET", f"/repos/{repo}/commits/{sha}", token)
        if not detail:
            continue
        for f in detail.get("files") or []:
            fname = f.get("filename", "")
            if fname:
                files.add(fname)
    return files


def detect_conflict_risk(pr_files: list[str], gap_files: set[str]) -> list[str]:
    """Return files present in both the PR and the gap (potential conflicts)."""
    return sorted(set(pr_files) & gap_files)


def _commit_row(entry: dict) -> str:
    sha8 = (entry.get("sha") or "")[:8]
    url = entry.get("html_url") or ""
    msg = (entry.get("commit") or {}).get("message", "").split("\n")[0][:72]
    login = ((entry.get("author") or {}).get("login") or
             (entry.get("committer") or {}).get("login") or "unknown")
    date = (((entry.get("commit") or {}).get("committer") or {}).get("date") or "")[:10]
    sha_cell = f"[`{sha8}`]({url})" if url else f"`{sha8}`"
    return f"| {sha_cell} | {date} | `{login}` | {msg} |"


def build_rich_divergence_comment(
    repo: str,
    head_branch: str,
    base_branch: str,
    behind_by: int,
    ahead_by: int,
    status: str,
    pr_number: int,
    gap_commits: list[dict],
    pr_files: list[str],
    gap_files: set[str],
    run_url: str = "",
) -> str:
    """Build the full rich PR helper comment.

    Contains:
     • Gap commit table with authors, dates and links
     • Conflict risk assessment (file overlap analysis)
     • Click-by-click resolution instructions (UI + CLI)
     • Copy-pasteable Copilot Coding Agent prompt
    """
    classified = classify_gap_commits(gap_commits)
    conflict_files = detect_conflict_risk(pr_files, gap_files)
    now_iso = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    pr_url = f"https://github.com/{repo}/pull/{pr_number}"
    run_link = f" · [View run]({run_url})" if run_url else ""

    # ── Status headline ───────────────────────────────────────────────────
    if status == "diverged":
        headline = (
            f"Branch `{head_branch}` has **diverged** from `{base_branch}` "
            f"(behind **{behind_by}**, ahead **{ahead_by}**)."
        )
    else:
        headline = (
            f"Branch `{head_branch}` is **{behind_by} commit(s) behind** `{base_branch}`."
        )

    # ── Conflict risk ─────────────────────────────────────────────────────
    if conflict_files:
        risk_badge = "🔴 **HIGH** — overlapping edits detected"
        risk_block = (
            "\n> ⚠️ **These files were modified in both the PR and the gap commits "
            "(manual conflict resolution may be required):**\n"
            + "".join(f"\n> - `{f}`" for f in conflict_files)
            + "\n"
        )
    else:
        risk_badge = "🟢 **LOW** — no overlapping file edits"
        risk_block = ""

    # ── Gap commit table ──────────────────────────────────────────────────
    if gap_commits:
        rows = "\n".join(_commit_row(c) for c in gap_commits)
        gap_note = ""
        if classified["all_bot_skip_ci"]:
            gap_note = (
                f"\n> ℹ️ All **{len(gap_commits)}** gap commit(s) are automated "
                f"`[skip ci]` `github-actions[bot]` commits — no functional code changes.\n"
            )
        elif classified["functional"]:
            n = len(classified["functional"])
            gap_note = (
                f"\n> ⚠️ **{n} functional commit(s)** require manual review.\n"
            )
        commit_table = (
            f"\n**{len(gap_commits)} commit(s) in `{base_branch}` "
            f"not yet in `{head_branch}`:**\n\n"
            f"| SHA | Date | Author | Message |\n"
            f"|-----|------|--------|---------|\n"
            f"{rows}\n"
            f"{gap_note}"
        )
    else:
        commit_table = "\n_(Gap commit details unavailable.)_\n"

    # ── Resolution options ────────────────────────────────────────────────
    resolution = f"""\
### ✅ How to resolve — choose one option

**Option A — GitHub UI (click-by-click):**
1. Open the PR: [{repo}#{pr_number}]({pr_url})
2. Scroll to the **merge box** at the bottom of the page
3. Click the **▼ dropdown** next to "Merge pull request"
4. Select **"Update branch"** → choose **"Update with merge commit"**
5. Wait for CI — REQ-10 clears automatically on the next push event

**Option B — Command line:**
```bash
git fetch origin {base_branch}
git checkout {head_branch}
git merge origin/{base_branch}
git push
```
"""
    if conflict_files:
        resolution += f"""
**⚠️ If merge conflicts appear, resolve these files first:**
{chr(10).join(f"  - `{f}`" for f in conflict_files)}

```bash
# After editing conflicted files:
git add <resolved-files>
git merge --continue
git push
```
"""

    # ── Copilot Coding Agent prompt ───────────────────────────────────────
    if classified["all_bot_skip_ci"]:
        conflict_note = "No conflicts expected — all gap commits are metadata-only bot commits."
        resolution_cmd = (
            f"git fetch origin {base_branch} && "
            f"git merge origin/{base_branch} && git push"
        )
    else:
        resolution_cmd = (
            f"git fetch origin {base_branch} && "
            f"git merge origin/{base_branch} && git push"
        )
        conflict_note = (
            f"Potential conflicts in: {', '.join(f'`{f}`' for f in conflict_files[:5])}. "
            "Resolve manually if conflicts appear."
            if conflict_files
            else "Low conflict risk — review gap commits before merging."
        )

    gap_commit_lines = "\n".join(
        f"  - {(c.get('sha') or '')[:8]}: "
        f"{(c.get('commit') or {}).get('message', '').split(chr(10))[0][:70]}"
        for c in gap_commits[:8]
    )

    copilot_prompt = f"""\
### 🤖 Copilot Coding Agent — copy-paste this prompt

> **Paste the block below directly into a Copilot Coding Agent session on this PR:**

```
@copilot Fix branch divergence on PR #{pr_number} (REQ-10 autonomous self-healing action).

Branch:  `{head_branch}`
Base:    `{base_branch}`
Status:  {status} (behind={behind_by}, ahead={ahead_by})

Gap commits ({len(gap_commits)} total):
{gap_commit_lines}

Conflict risk: {conflict_note}

Action required:
1. Run: `{resolution_cmd}`
2. If any merge conflicts appear{f" in {', '.join(conflict_files[:3])}" if conflict_files else ""}, resolve and commit.
3. Push — branch-rebase-gate.yml clears REQ-10 automatically on the next push.

PR: {pr_url}
```
"""

    return (
        f"## ⚠️ {REBASE_REQUIRED_MARKER} — Branch Must Be Updated\n\n"
        f"<!-- {REBASE_REQUIRED_MARKER} -->\n\n"
        f"{headline}\n\n"
        f"**Conflict risk:** {risk_badge}\n"
        f"{risk_block}"
        f"{commit_table}\n"
        f"---\n\n"
        f"{resolution}\n"
        f"---\n\n"
        f"{copilot_prompt}\n"
        f"---\n"
        f"_Auto-posted by `branch-rebase-gate.yml` (Phase 5 autonomous self-healing) "
        f"at {now_iso}{run_link}_"
    )


# ---------------------------------------------------------------------------
# PR Status Dashboard integration
# ---------------------------------------------------------------------------

def _encode_dashboard_section(
    name: str, status: str, summary: str, details: str
) -> str:
    """Encode one section in the pr_comment_consolidator.py wire format."""
    payload = json.dumps({"status": status, "summary": summary, "details": details})
    return (
        f"<!-- SECTION:{name} -->\n"
        f"<!-- PAYLOAD:{payload} -->\n"
        f"<!-- /SECTION:{name} -->"
    )


def upsert_dashboard_alert(
    repo: str,
    token: str,
    pr_number: int,
    status: str,
    summary: str,
    details: str,
    run_url: str = "",
) -> None:
    """Write/update the Branch Rebase Gate section in the PR Status Dashboard.

    This function updates ONLY the hidden SECTION/PAYLOAD blob for this gate
    in the existing dashboard comment body, leaving the visible layout (Merge
    Readiness score, other sections) fully owned by pr_comment_consolidator.py.

    If no canonical dashboard comment exists yet, creation is deferred to
    pr_comment_consolidator.py — this avoids writing a stripped-down duplicate
    that would later be overwritten with incorrect formatting.
    """
    payload = {
        "status": status,
        "summary": summary,
        "details": details,
    }
    new_payload_json = json.dumps(payload, separators=(",", ":"))
    replacement = (
        f"<!-- SECTION:{_DASHBOARD_SECTION} -->\n"
        f"<!-- PAYLOAD:{new_payload_json} -->\n"
        f"<!-- /SECTION:{_DASHBOARD_SECTION} -->"
    )
    section_pattern = re.compile(
        rf"<!-- SECTION:{re.escape(_DASHBOARD_SECTION)} -->"
        r"\s*<!-- PAYLOAD:(\{{.*?\}}) -->"
        rf"\s*<!-- /SECTION:{re.escape(_DASHBOARD_SECTION)} -->",
        re.DOTALL,
    )

    comments = get_pr_comments(repo, token, pr_number)

    # Find existing canonical dashboard comment (most recently updated)
    dashboard: Optional[dict] = None
    for c in reversed(comments):
        if _DASHBOARD_MARKER in (c.get("body") or ""):
            dashboard = c
            break

    if not dashboard:
        # No canonical dashboard comment yet — defer creation to
        # pr_comment_consolidator.py so the full layout (Merge Readiness etc.)
        # is rendered correctly.
        print(
            f"  ℹ️  No dashboard comment found on PR #{pr_number} — "
            "deferring to pr_comment_consolidator.py"
        )
        return

    existing_body = dashboard["body"]
    updated_body = section_pattern.sub(lambda _: replacement, existing_body)
    if updated_body == existing_body:
        # Section not present yet — append the hidden payload block without
        # touching the visible dashboard layout.
        updated_body = f"{existing_body.rstrip()}\n\n{replacement}\n"

    gh_api(
        "PATCH",
        f"/repos/{repo}/issues/comments/{dashboard['id']}",
        token,
        json.dumps({"body": updated_body}).encode(),
    )
    print(f"  📊 Updated dashboard section in comment #{dashboard['id']} on PR #{pr_number}")


# ---------------------------------------------------------------------------
# GitHub API mode (CI / PR check)
# ---------------------------------------------------------------------------


def check_via_api(repo: str, token: str, pr_number: int) -> tuple[str, int, int, str, str]:
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
    if status == "behind":
        return "behind", behind_by, ahead_by, base_branch, head_branch
    if status == "ahead":
        return "ahead", behind_by, ahead_by, base_branch, head_branch
    if status == "diverged":
        return "diverged", behind_by, ahead_by, base_branch, head_branch
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
    ahead_by: int = 0,
    status: str = "behind",
    gap_commits: Optional[list] = None,
    pr_files: Optional[list] = None,
    run_url: str = "",
    upsert_dashboard: bool = False,
) -> None:
    """Post (or update) the rich BRANCH_REBASE_REQUIRED helper comment.

    When gap_commits and pr_files are provided the comment includes a full
    conflict risk analysis, gap commit table and copy-pasteable Copilot
    Coding Agent prompt.  When omitted a minimal fallback is posted.
    Also writes to the PR Status Dashboard when upsert_dashboard=True.
    """
    comments = get_pr_comments(repo, token, pr_number)

    # Skip re-post when a RESOLVED marker is newer than the REQUIRED marker
    resolved_c = _find_bot_comment(comments, REBASE_RESOLVED_MARKER)
    required_c = _find_bot_comment(comments, REBASE_REQUIRED_MARKER)
    if resolved_c and required_c:
        if resolved_c.get("updated_at", "") >= required_c.get("updated_at", ""):
            print(f"  ℹ️  Rebase already resolved (comment {resolved_c['id']}) — skipping re-post")
            return

    # Build rich body when data is available; fall back to minimal comment
    if gap_commits is not None and pr_files is not None:
        gap_files = get_gap_files(repo, token, gap_commits)
        body = build_rich_divergence_comment(
            repo=repo,
            head_branch=head_branch,
            base_branch=base_branch,
            behind_by=behind_by,
            ahead_by=ahead_by,
            status=status,
            pr_number=pr_number,
            gap_commits=gap_commits,
            pr_files=pr_files,
            gap_files=gap_files,
            run_url=run_url,
        )
    else:
        now_iso = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        body = (
            f"## ⚠️ {REBASE_REQUIRED_MARKER} — Branch Must Be Updated\n\n"
            f"<!-- {REBASE_REQUIRED_MARKER} -->\n\n"
            f"**Branch `{head_branch}` is {behind_by} commit(s) behind `{base_branch}`.**\n\n"
            f"Run:\n```bash\ngit fetch origin {base_branch}\n"
            f"git merge origin/{base_branch}\ngit push\n```\n\n"
            f"_Auto-posted by `branch-rebase-gate.yml` at {now_iso}_"
        )

    existing = _find_bot_comment(comments, REBASE_REQUIRED_MARKER)
    if existing:
        gh_api(
            "PATCH",
            f"/repos/{repo}/issues/comments/{existing['id']}",
            token,
            json.dumps({"body": body}).encode(),
        )
        print(f"  🔄 Updated helper comment (#{existing['id']}) on PR #{pr_number}")
    else:
        gh_api(
            "POST",
            f"/repos/{repo}/issues/{pr_number}/comments",
            token,
            json.dumps({"body": body}).encode(),
        )
        print(f"  📌 Posted helper comment on PR #{pr_number}")

    # Mirror into PR Status Dashboard
    if upsert_dashboard and token:
        classified = classify_gap_commits(gap_commits or [])
        # Compute gap_files for accurate conflict detection (best-effort)
        _gap_files_for_risk: set[str] = set()
        if gap_commits:
            try:
                _gap_files_for_risk = set(get_gap_files(repo, token, gap_commits))
            except Exception as exc:  # best-effort: don't abort if gap-file detection fails
                print(
                    f"[warn] gap-file detection failed (conflict risk degraded): {exc!r}",
                    file=sys.stderr,
                )
        conflict_risk = (
            "🔴 HIGH" if detect_conflict_risk(pr_files or [], _gap_files_for_risk)
            else ("🟢 LOW" if gap_commits else "⚠️ Unknown")
        )
        all_bot = classified.get("all_bot_skip_ci", False)
        n_gap = len(gap_commits) if gap_commits else behind_by
        dash_summary = (
            f"Branch `{head_branch}` is {status} from `{base_branch}` "
            f"(behind={behind_by}, conflict risk={conflict_risk}) — "
            + (f"all {n_gap} gap commits are `[skip ci]` bot commits" if all_bot
               else f"{len(classified.get('functional', []))} functional commit(s) in gap")
        )
        upsert_dashboard_alert(
            repo=repo,
            token=token,
            pr_number=pr_number,
            status="failure",
            summary=dash_summary,
            details=body,
            run_url=run_url,
        )


def post_rebase_resolved_comment(
    repo: str,
    token: str,
    pr_number: int,
    base_branch: str,
    head_branch: str,
    run_url: str = "",
    upsert_dashboard: bool = False,
) -> None:
    """Upsert a BRANCH_REBASE_RESOLVED comment when the branch is up-to-date.

    If a RESOLVED comment already exists (from a previous synchronize event)
    we PATCH it in-place rather than creating a new one, preventing the
    4× duplicate accumulation seen in PR #3605.
    Also clears the Branch Rebase Gate section in the dashboard when
    upsert_dashboard=True.
    """
    comments = get_pr_comments(repo, token, pr_number)

    # Only act if a REQUIRED marker exists (nothing to resolve otherwise)
    required = _find_bot_comment(comments, REBASE_REQUIRED_MARKER)
    if not required:
        # Still update dashboard to success so it doesn't show stale failure
        if upsert_dashboard and token:
            upsert_dashboard_alert(
                repo=repo, token=token, pr_number=pr_number,
                status="success",
                summary=f"Branch `{head_branch}` is up-to-date with `{base_branch}`",
                details="No rebase required.", run_url=run_url,
            )
        return

    resolved = _find_bot_comment(comments, REBASE_RESOLVED_MARKER)
    if resolved and resolved.get("updated_at", "") >= required.get("updated_at", ""):
        return  # Already resolved and newer than the last REQUIRED post

    now_iso = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    run_link = f" · [View run]({run_url})" if run_url else ""
    body = (
        f"<!-- {REBASE_RESOLVED_MARKER} -->\n"
        f"## ✅ Branch Rebase Resolved — REQ-10 Cleared\n\n"
        f"Branch `{head_branch}` is now up-to-date with `{base_branch}`. "
        f"The REQ-10 gate has been cleared automatically.\n\n"
        f"_Auto-posted by `branch-rebase-gate.yml` (Phase 5 self-healing) "
        f"at {now_iso}{run_link}_"
    )
    if resolved:
        gh_api(
            "PATCH",
            f"/repos/{repo}/issues/comments/{resolved['id']}",
            token,
            json.dumps({"body": body}).encode(),
        )
        print(f"  🔄 Updated resolved comment (#{resolved['id']}) on PR #{pr_number}")
    else:
        gh_api(
            "POST",
            f"/repos/{repo}/issues/{pr_number}/comments",
            token,
            json.dumps({"body": body}).encode(),
        )
        print(f"  ✅ Posted resolved comment on PR #{pr_number}")

    if upsert_dashboard and token:
        upsert_dashboard_alert(
            repo=repo, token=token, pr_number=pr_number,
            status="success",
            summary=f"Branch `{head_branch}` is up-to-date with `{base_branch}` ✅",
            details="REQ-10 cleared — no rebase required.",
            run_url=run_url,
        )


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
    parser = argparse.ArgumentParser(
        description="Detect whether a PR branch needs rebasing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPO))
    parser.add_argument("--pr", type=int, metavar="PR_NUMBER",
                        help="PR number (CI mode — uses GitHub API)")
    parser.add_argument("--post-comment", action="store_true",
                        help="Post/update the rich helper comment on the PR")
    parser.add_argument("--github-output", action="store_true",
                        help="Write status to GITHUB_OUTPUT")
    parser.add_argument("--github-summary", action="store_true",
                        help="Write status to GITHUB_STEP_SUMMARY")
    parser.add_argument("--hard-fail", action="store_true",
                        help="Exit 1/2 when rebase needed (gate mode)")
    parser.add_argument("--auto-merge-skip-ci", action="store_true",
                        help=(
                            "When branch is behind/diverged and ALL gap commits are "
                            "[skip ci] github-actions[bot] commits, auto-merge via "
                            "GitHub Merges API instead of hard-blocking"
                        ))
    parser.add_argument("--upsert-dashboard", action="store_true",
                        help=(
                            "Mirror alert status into the PR Status Dashboard comment "
                            "(<!-- PR_STATUS_DASHBOARD_v1 --> format)"
                        ))
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    run_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com") + \
              "/" + os.environ.get("GITHUB_REPOSITORY", "") + \
              "/actions/runs/" + os.environ.get("GITHUB_RUN_ID", "")
    if not os.environ.get("GITHUB_RUN_ID"):
        run_url = ""

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
            write_github_output(
                "rebase_required",
                "true" if status in ("behind", "diverged") else "false"
            )

        rebase_needed = status in ("behind", "diverged")

        # Initialise early so it is always defined regardless of which branch
        # is taken in the auto-merge block below.
        gap_commits_for_comment: list[dict] = []

        # ── Auto-merge when gap is 100% bot [skip ci] commits ────────────
        if rebase_needed and args.auto_merge_skip_ci and token:
            print("  🔍 Checking whether gap commits are all [skip ci] bot commits…")
            gap_commits = get_commits_in_gap(args.repo, token, base_branch, head_branch)
            classified = classify_gap_commits(gap_commits)
            if classified["all_bot_skip_ci"]:
                n = len(gap_commits)
                print(f"  ✅ All {n} gap commit(s) are [skip ci] bot commits — attempting auto-merge…")
                ok, detail = auto_merge_base_into_branch(
                    args.repo, token, head_branch, base_branch, n
                )
                if ok:
                    print(f"  ✅ Auto-merged {base_branch} → {head_branch}: {detail}")
                    if args.post_comment:
                        post_auto_merge_comment(
                            args.repo, token, args.pr, base_branch, head_branch, n
                        )
                    if args.upsert_dashboard:
                        upsert_dashboard_alert(
                            repo=args.repo, token=token, pr_number=args.pr,
                            status="success",
                            summary=(
                                f"Auto-merged {n} `[skip ci]` bot commits from "
                                f"`{base_branch}` into `{head_branch}` ✅"
                            ),
                            details=(
                                f"branch-rebase-gate.yml automatically merged "
                                f"{n} automated metadata commit(s) — REQ-10 cleared."
                            ),
                            run_url=run_url,
                        )
                    if args.github_output:
                        write_github_output("rebase_required", "false")
                        write_github_output("auto_merged", "true")
                        write_github_output("rebase_status", "auto-merged")
                    write_step_summary(
                        f"\n### ✅ REQ-10: Branch Auto-Updated — PASS\n\n"
                        f"`{head_branch}` was {behind_by} commit(s) behind `{base_branch}` "
                        f"(all automated `[skip ci]` commits). "
                        f"Auto-merged by `branch-rebase-gate.yml`.\n"
                    )
                    return 0
                # Auto-merge failed — fall through to rich helper comment.
                # gap_commits_for_comment was initialised to [] above; set it
                # here so the comment includes the full gap table.
                print(f"  ⚠️  Auto-merge failed ({detail}) — falling back to helper comment")
                gap_commits_for_comment = gap_commits
            else:
                n_func = len(classified.get("functional", []))
                print(f"  ℹ️  Gap contains {n_func} functional commit(s) — manual rebase required")
                gap_commits_for_comment = gap_commits

        # ── Step summary ─────────────────────────────────────────────────
        if status == "up-to-date":
            summary_text = (
                f"\n### ✅ REQ-10: Branch Rebase Check — PASS\n\n"
                f"`{head_branch}` is up-to-date with `{base_branch}`.\n"
            )
        elif status == "ahead":
            summary_text = (
                f"\n### ✅ REQ-10: Branch Rebase Check — PASS\n\n"
                f"`{head_branch}` is {ahead_by} commit(s) **ahead** of "
                f"`{base_branch}` — no rebase needed.\n"
            )
        elif status == "behind":
            summary_text = (
                f"\n### 🔴 REQ-10: Branch Rebase Check — FAIL\n\n"
                f"**`{head_branch}` is {behind_by} commit(s) BEHIND `{base_branch}`.**\n\n"
                f"> See helper comment on the PR for step-by-step resolution instructions\n"
                f"> and a copy-pasteable Copilot Coding Agent prompt.\n"
            )
        elif status == "diverged":
            summary_text = (
                f"\n### 🔴 REQ-10: Branch Rebase Check — FAIL\n\n"
                f"**`{head_branch}` has DIVERGED from `{base_branch}`** "
                f"(behind={behind_by}, ahead={ahead_by}).\n\n"
                f"> See helper comment on the PR for step-by-step resolution instructions\n"
                f"> and a copy-pasteable Copilot Coding Agent prompt.\n"
            )
        else:
            summary_text = (
                f"\n### ⚠️ REQ-10: Branch Rebase Check — UNKNOWN\n\n"
                f"Could not determine rebase status for PR #{args.pr}. "
                f"Treating as soft warning.\n"
            )
        write_step_summary(summary_text)

        # ── Post helper comment + dashboard update ────────────────────────
        if args.post_comment and token:
            if rebase_needed:
                # Fetch PR files for conflict analysis (best-effort)
                pr_files: list[str] = []
                if token:
                    try:
                        pr_files = get_pr_changed_files(args.repo, token, args.pr)
                    except Exception as exc:
                        # Best-effort enrichment only: ignore failures so that
                        # the rebase gate remains non-blocking on PR file fetch errors.
                        print(
                            f"[branch_rebase_check] Warning: failed to fetch PR files "
                            f"for #{args.pr}: {exc}",
                            file=sys.stderr,
                        )
                # Use gap_commits already fetched if auto-merge-skip-ci was set,
                # otherwise fetch them now for the comment
                if not gap_commits_for_comment:
                    try:
                        gap_commits_for_comment = get_commits_in_gap(
                            args.repo, token, base_branch, head_branch
                        )
                    except Exception:
                        gap_commits_for_comment = []

                post_rebase_required_comment(
                    repo=args.repo,
                    token=token,
                    pr_number=args.pr,
                    base_branch=base_branch,
                    head_branch=head_branch,
                    behind_by=behind_by,
                    ahead_by=ahead_by,
                    status=status,
                    gap_commits=gap_commits_for_comment,
                    pr_files=pr_files,
                    run_url=run_url,
                    upsert_dashboard=args.upsert_dashboard,
                )
            else:
                post_rebase_resolved_comment(
                    repo=args.repo,
                    token=token,
                    pr_number=args.pr,
                    base_branch=base_branch,
                    head_branch=head_branch,
                    run_url=run_url,
                    upsert_dashboard=args.upsert_dashboard,
                )
        elif args.upsert_dashboard and token and not rebase_needed:
            # No comment requested but dashboard should reflect passing status
            upsert_dashboard_alert(
                repo=args.repo, token=token, pr_number=args.pr,
                status="success",
                summary=f"Branch `{head_branch}` is up-to-date with `{base_branch}` ✅",
                details="REQ-10 passed — no rebase required.",
                run_url=run_url,
            )

        # ── Exit code ─────────────────────────────────────────────────────
        if status == "behind":
            print(f"\n❌  Branch is {behind_by} commit(s) BEHIND base — rebase required (REQ-10)")
            return 1 if args.hard_fail else 0
        if status == "diverged":
            print(
                f"\n❌  Branch has DIVERGED (behind={behind_by}, ahead={ahead_by})"
                f" — rebase required (REQ-10)"
            )
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
