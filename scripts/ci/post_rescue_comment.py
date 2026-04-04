#!/usr/bin/env python3
"""Unified rescue-comment upsert script (S294).

All CI workflows call this script when they fail.  The script maintains
**one rescue comment per head-commit SHA** — every workflow that fails on
the same commit *appends* its failure section to that same comment rather
than creating a new one.

Marker: ``<!-- ci-rescue-sha:{pr_number}:{sha_short} -->``

Two operating modes
-------------------
PR-triggered (default)
    Set ``PR_NUMBER`` explicitly from ``github.event.pull_request.number``.

Push-triggered
    Leave ``PR_NUMBER`` unset (or set to empty string).  The script will
    query the GitHub API to find the open PR for ``BRANCH`` and use its
    number.  If no open PR is found the script exits 0 (no comment posted).

Required environment variables
-------------------------------
GH_TOKEN        GitHub token (PAT or github.token)
PR_NUMBER       Pull-request number (integer); optional in push mode
REPO            owner/repo slug
COMMIT_SHA      Full 40-char head commit SHA
RUN_ID          GitHub Actions run ID
RUN_URL         Full URL to the workflow run
WORKFLOW_NAME   Human-readable name shown in the comment
BRANCH          PR head branch name (required in push mode for PR lookup)

Usage — PR-triggered workflow step
------------------------------------
    - name: Post or update rescue comment
      env:
        GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
        PR_NUMBER: ${{ github.event.pull_request.number }}
        REPO: ${{ github.repository }}
        COMMIT_SHA: ${{ github.event.pull_request.head.sha }}
        RUN_ID: ${{ github.run_id }}
        WORKFLOW_NAME: "My Workflow"
        RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        BRANCH: ${{ github.head_ref }}
      run: python scripts/ci/post_rescue_comment.py

Usage — push-triggered workflow step
--------------------------------------
    - name: Post or update rescue comment
      env:
        GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
        REPO: ${{ github.repository }}
        COMMIT_SHA: ${{ github.sha }}
        RUN_ID: ${{ github.run_id }}
        WORKFLOW_NAME: "My Workflow"
        RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        BRANCH: ${{ github.ref_name }}
      run: python scripts/ci/post_rescue_comment.py
"""

from __future__ import annotations

import datetime
import json
import os
import sys
import urllib.error
import urllib.request

MAX_COMMENT_LEN = 65_536  # GitHub comment body limit


def _gh(
    method: str,
    path: str,
    token: str,
    body: dict | None = None,
) -> tuple[int, object]:
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        try:
            err_body = json.loads(exc.read())
        except Exception:
            err_body = {}
        return exc.code, err_body


def _find_rescue_comment(
    token: str,
    repo: str,
    pr_number: int,
    marker: str,
) -> tuple[int | None, str]:
    """Return (comment_id, comment_body) for the first comment containing *marker*."""
    page = 1
    while True:
        status, comments = _gh(
            "GET",
            f"/repos/{repo}/issues/{pr_number}/comments?per_page=100&page={page}",
            token,
        )
        if status != 200 or not isinstance(comments, list) or not comments:
            break
        for c in comments:
            body = c.get("body") or ""
            if marker in body:
                return c["id"], body
        if len(comments) < 100:
            break
        page += 1
    return None, ""


def _lookup_pr_number(token: str, repo: str, branch: str) -> int | None:
    """Return the PR number for *branch* via the GitHub API, or None."""
    owner = repo.split("/")[0]
    status, prs = _gh(
        "GET",
        f"/repos/{repo}/pulls?state=open&head={owner}:{branch}&per_page=10",
        token,
    )
    if status == 200 and isinstance(prs, list) and prs:
        return prs[0]["number"]
    return None


def main() -> None:
    token = os.environ["GH_TOKEN"]
    pr_number_raw = os.environ.get("PR_NUMBER", "").strip()
    repo = os.environ["REPO"]
    commit_sha = os.environ["COMMIT_SHA"]
    run_id = os.environ["RUN_ID"]
    run_url = os.environ["RUN_URL"]
    workflow = os.environ["WORKFLOW_NAME"]
    branch = os.environ["BRANCH"]

    now = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sha_short = commit_sha[:12]

    # Resolve PR number — explicit (PR-triggered) or via API lookup (push-triggered).
    if pr_number_raw:
        pr_number: int = int(pr_number_raw)
    else:
        looked_up = _lookup_pr_number(token, repo, branch)
        if looked_up is None:
            print(f"ℹ️  No open PR found for branch '{branch}' — skipping rescue comment.")
            return
        pr_number = looked_up

    # ONE rescue comment per PR per commit — all workflows share this marker.
    marker = f"<!-- ci-rescue-sha:{pr_number}:{sha_short} -->"

    existing_id, existing_body = _find_rescue_comment(token, repo, pr_number, marker)

    if existing_id:
        # Append this workflow's failure to the existing comment (collapsed).
        append_section = (
            f"\n\n---\n\n"
            f"<details><summary>🔴 <code>{workflow}</code> — {now} · "
            f"<a href=\"{run_url}\">Run #{run_id}</a></summary>\n\n"
            f"@copilot **{workflow}** failed on commit `{sha_short}`. "
            f"Check [run #{run_id}]({run_url}) for details.\n\n"
            f"</details>"
        )
        updated_body = (existing_body.rstrip() + append_section)[:MAX_COMMENT_LEN]
        status, _ = _gh(
            "PATCH",
            f"/repos/{repo}/issues/comments/{existing_id}",
            token,
            {"body": updated_body},
        )
        if status in (200, 201):
            print(
                f"✅ Appended `{workflow}` failure to rescue comment #{existing_id} "
                f"(commit {sha_short})"
            )
            return
        print(
            f"⚠️  PATCH returned HTTP {status} — will attempt to create a new comment."
        )

    # Either no existing comment or PATCH failed — create the initial comment.
    # RC-5 (S299): embed a compact inline context block (§A+§B+§D) so the agent
    # immediately sees the action queue without needing a separate API call.
    inline_ctx = ""
    try:
        import pathlib as _pathlib
        import sys as _sys
        _scripts_ci = str(_pathlib.Path(__file__).parent)
        if _scripts_ci not in _sys.path:
            _sys.path.insert(0, _scripts_ci)
        from discussion_context_store import build_comment_context  # noqa: PLC0415
        inline_ctx = build_comment_context(pr_number, commit_sha, repo, token)
    except Exception:
        # Graceful degradation — inline context is optional; rescue comment still posts.
        pass  # context unavailable (first run, missing deps, etc.)

    ctx_section = (f"{inline_ctx}\n\n---\n\n") if inline_ctx else ""
    first_body = (
        f"{marker}\n"
        f"## 🚨 CI Rescue — @copilot Fix Required\n\n"
        f"**Branch:** `{branch}` | **Commit:** `{commit_sha}`\n\n"
        f"@copilot One or more checks are failing on commit `{sha_short}`. "
        f"This comment is automatically updated as additional failures are "
        f"detected **on the same commit**. A new push creates a new comment.\n\n"
        f"<details><summary>📋 Steps to resolve</summary>\n\n"
        f"1. Load `.codex/CODEBASE_AGENCY_POLICY.md` (§0 — fix ALL issues found)\n"
        f"2. Check each failing workflow run linked below\n"
        f"3. Apply the minimal fix and push\n"
        f"4. Update `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`\n"
        f"5. Verify all CI checks are green before concluding\n\n"
        f"</details>\n\n"
        f"{ctx_section}"
        f"<details><summary>🔴 <code>{workflow}</code> — {now} · "
        f"<a href=\"{run_url}\">Run #{run_id}</a></summary>\n\n"
        f"@copilot The **{workflow}** check is failing on commit `{sha_short}`. "
        f"Check the failure logs: [{run_id}]({run_url})\n\n"
        f"_Auto-posted by rescue-comment system (S294) · "
        f"[🔗 Workflow run]({run_url})_\n\n"
        f"</details>"
    )

    status, resp = _gh(
        "POST",
        f"/repos/{repo}/issues/{pr_number}/comments",
        token,
        {"body": first_body},
    )
    if status in (200, 201):
        url = resp.get("html_url", "(no url)") if isinstance(resp, dict) else "(no url)"
        print(f"✅ Posted rescue comment: {url}")
    else:
        print(f"❌ POST failed: HTTP {status} — {resp}")
        sys.exit(1)


if __name__ == "__main__":
    main()
