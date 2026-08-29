#!/usr/bin/env python3
"""Unified rescue-comment upsert script (S294).

All CI workflows call this script when they fail.  The script maintains
**one rescue comment per head-commit SHA** — every workflow that fails on
the same commit *appends* its failure section to that same comment rather
than creating a new one.

When cascading Copilot errors are detected (10+ comments), the script implements
**append-first batching**: instead of aborting, it appends to the existing
successful rescue comment. Multiple workflow failures destined for the same
commit are automatically batched and posted as a single append, preventing
rate-limiting and sprawling comments.

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

Optional environment variables
--------------------------------
SECTION_TITLE   Title for a custom appended section (e.g., "Root Cause Analysis")
SECTION_CONTENT Markdown content to append as a named ``<details>`` section.
                When set together with SECTION_TITLE, replaces the default
                failure message format with the custom title/content.
APPEND_ONLY     Set to "true" to skip creating a new comment when no existing
                rescue comment is found.  Useful for RCA appends that should
                only update an already-existing rescue thread.
BATCH_WAIT_SECONDS  Time to wait for other workflows before flushing queued
                    comments as a batch append (default: 3 seconds). Used when
                    cascading errors are detected to prevent rate-limiting.

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
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import pathlib
from typing import Any

MAX_COMMENT_LEN = 65_536  # GitHub comment body limit
CONSOLIDATION_DELAY_SECONDS = 3
DUPLICATE_DIGEST_LENGTH = 16
# Note: UTC_TIMESTAMP_FORMAT is also defined in rescue_comment_batch_queue.py.
# We keep both to maintain module independence and avoid circular imports.
UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
# Cascade error marker constant for detecting already-consolidated cascades
# Note: The consolidation script creates markers with CASCADE_ERROR_ID_MARKER_PREFIX
# ('<!-- cascade-error-id:...') to indicate which errors were consolidated.
# We detect consolidation by looking for this 'cascade-error-id' substring.
CASCADE_CONSOLIDATED_CHECK = "cascade-error-id"


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
            raw = resp.read()
            if raw:
                return resp.status, json.loads(raw)
            # Successful GitHub GET requests used by this script return JSON.
            # Empty bodies are expected for 204-style mutation responses.
            return resp.status, {}
    except urllib.error.HTTPError as exc:
        try:
            err_body = json.loads(exc.read())
        except Exception:
            err_body = {}
        return exc.code, err_body


def _get_batch_queue_module() -> Any:
    """Lazily import batch queue module, gracefully degrading if unavailable."""
    try:
        script_dir = str(pathlib.Path(__file__).parent)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        import rescue_comment_batch_queue as batch_queue
        return batch_queue
    except ImportError:
        return None


def _build_append_section(
    workflow_name: str,
    run_id: str,
    run_url: str,
    section_title: str | None,
    section_content: str | None,
    timestamp: str,
    commit_sha: str,
 ) -> str:
    """Build markdown section for appending to rescue comment."""
    if section_title and section_content:
        return (
            f"\n\n---\n\n"
            f"<details><summary>📋 <code>{section_title}</code> — {timestamp} · "
            f"<a href=\"{run_url}\">Run #{run_id}</a></summary>\n\n"
            f"{section_content}\n\n"
            f"</details>"
        )
    else:
        return (
            f"\n\n---\n\n"
            f"<details><summary>🔴 <code>{workflow_name}</code> — {timestamp} · "
            f"<a href=\"{run_url}\">Run #{run_id}</a></summary>\n\n"
            f"@copilot **{workflow_name}** failed on commit `{commit_sha[:12]}`. "
            f"Check [run #{run_id}]({run_url}) for details.\n\n"
            f"</details>"
        )


def _handle_cascade_append(
    token: str,
    repo: str,
    pr_number: int,
    commit_sha: str,
    existing_id: int | None,
    workflow_name: str,
    run_id: str,
    run_url: str,
    section_title: str | None,
    section_content: str | None,
) -> bool:
    """Handle append-first behavior when cascade detected.

    If existing comment found, append to it immediately.
    Otherwise, queue for batch posting.

    Returns True if handled, False otherwise.
    """
    if existing_id:
        # Cascade detected but existing comment found — append to it
        now = datetime.datetime.now(tz=datetime.timezone.utc).strftime(UTC_TIMESTAMP_FORMAT)
        append_section = _build_append_section(
            workflow_name=workflow_name,
            run_id=run_id,
            run_url=run_url,
            section_title=section_title,
            section_content=section_content,
            timestamp=now,
            commit_sha=commit_sha,
        )

        # Fetch existing comment
        status, comments = _gh(
            "GET",
            f"/repos/{repo}/issues/comments/{existing_id}",
            token,
        )
        if status != 200:
            return False

        existing_body = (comments.get("body") or "").rstrip()
        updated_body = (existing_body + append_section)[:MAX_COMMENT_LEN]

        status, _ = _gh(
            "PATCH",
            f"/repos/{repo}/issues/comments/{existing_id}",
            token,
            {"body": updated_body},
        )
        if status in (200, 201):
            print(
                f"✅ CASCADE: Appended `{workflow_name}` failure to rescue comment #{existing_id} "
                f"(cascade handling, commit {commit_sha[:12]})"
            )
            return True
        return False
    else:
        # Cascade detected but no existing comment — queue for batch
        batch_queue = _get_batch_queue_module()
        if batch_queue:
            try:
                batch_queue.queue_item(
                    pr_number=pr_number,
                    commit_sha=commit_sha,
                    workflow_name=workflow_name,
                    run_id=run_id,
                    run_url=run_url,
                    section_title=section_title,
                    section_content=section_content,
                )
                return True
            except Exception as exc:
                # Batch queue operation failed (file I/O, etc.); continue with other approaches
                print(f"⚠️  Batch queue failed (non-blocking): {exc}", file=sys.stderr)
        return False


def _find_rescue_comment(
    token: str,
    repo: str,
    pr_number: int,
    marker: str,
    signature: str | None = None,
) -> tuple[int | None, str]:
    """Return (comment_id, comment_body) for the first matching rescue comment.

    The marker is authoritative.  The visible signature is a defensive fallback
    for comments created by older rescue paths or API surfaces that omit HTML
    comments from their rendered body.
    """
    page = 1
    while True:
        status, comments = _gh(
            "GET",
            f"/repos/{repo}/issues/{pr_number}/comments?per_page=100&page={page}",
            token,
        )
        if status != 200:
            break
        if not isinstance(comments, list):
            break
        if not comments:
            break
        for c in comments:
            body = c.get("body") or ""
            if marker in body or (signature and signature in body):
                return c["id"], body
        if len(comments) < 100:
            break
        page += 1
    return None, ""


def _matching_rescue_comments(
    token: str,
    repo: str,
    pr_number: int,
    marker: str,
    signature: str,
) -> list[dict]:
    """Return all comments matching this SHA-scoped rescue thread."""
    matches: list[dict] = []
    page = 1
    while True:
        status, comments = _gh(
            "GET",
            f"/repos/{repo}/issues/{pr_number}/comments?per_page=100&page={page}",
            token,
        )
        if status != 200:
            break
        if not isinstance(comments, list):
            break
        if not comments:
            break
        for c in comments:
            body = c.get("body") or ""
            if marker in body or signature in body:
                matches.append(c)
        if len(comments) < 100:
            break
        page += 1
    return sorted(matches, key=lambda c: c.get("id", 0))


def _detect_cascading_copilot_errors(
    token: str,
    repo: str,
    pr_number: int,
    threshold: int = 5,
    comments: list[dict] | None = None,
) -> dict:
    """Detect cascading Copilot error comments and already-consolidated cascades.

    When *comments* is provided, the function inspects that already-fetched list
    instead of making a fresh GitHub API request. This keeps duplicate rescue
    consolidation logic from hitting the same PR comments endpoint twice while
    preserving the original network-backed behavior for callers that supply only
    token/repo/pr_number.

    Cascades are identified by:
    - 5+ comments with "comment-generic-error" marker (fresh errors, threshold configurable)
    - 5+ comments with "cascade-error-id" marker (already consolidated)
    - Created by Copilot user within short timespan
    - Repeating UUID patterns

    Note: Consolidated cascades are detected by the presence of cascade-error-id markers,
    which indicate that consolidation has already occurred. Both fresh and consolidated
    error comments are counted, but consolidated cascades skip further processing.

    Args:
        token: GitHub API token
        repo: Repository slug (owner/repo)
        pr_number: Pull request number
        threshold: Minimum error comment count to trigger consolidation (default: 5)

    Returns:
        {
            "is_cascading": bool - True if cascade detected (fresh or already-consolidated)
            "error_count": int - Total error comments found (fresh + consolidated)
            "last_error_id": int or None - Most recent error comment ID
            "action": str - One of "CONSOLIDATE_ERRORS", "ALREADY_CONSOLIDATED", "APPEND_TO_EXISTING", "PROCEED"
        }
    """
    error_comments = []
    has_consolidated_error = False

    if comments is None:
        page = 1
        while True:
            status, comments = _gh(
                "GET",
                f"/repos/{repo}/issues/{pr_number}/comments?per_page=100&page={page}",
                token,
            )
            if status != 200:
                break
            if not isinstance(comments, list) or not comments:
                break

            for c in comments:
                body = c.get("body") or ""
                if ("comment-generic-error" in body or CASCADE_CONSOLIDATED_CHECK in body):
                    if c.get("user", {}).get("login") == "Copilot":
                        error_comments.append(c)
                        if CASCADE_CONSOLIDATED_CHECK in body:
                            has_consolidated_error = True

            if len(comments) < 100:
                break
            page += 1
    else:
        for c in comments:
            body = c.get("body") or ""
            if ("comment-generic-error" in body or CASCADE_CONSOLIDATED_CHECK in body):
                if c.get("user", {}).get("login") == "Copilot":
                    error_comments.append(c)
                    if CASCADE_CONSOLIDATED_CHECK in body:
                        has_consolidated_error = True

    if not error_comments:
        return {
            "is_cascading": False,
            "error_count": 0,
            "last_error_id": None,
            "action": "PROCEED",
        }

    # If already consolidated, skip further action
    if has_consolidated_error:
        return {
            "is_cascading": True,
            "error_count": len(error_comments),
            "last_error_id": None,
            "action": "ALREADY_CONSOLIDATED",
        }

    # If more than threshold error comments, it's an active cascade
    if len(error_comments) >= threshold:
        last_error = max(error_comments, key=lambda c: c.get("created_at", ""))
        return {
            "is_cascading": True,
            "error_count": len(error_comments),
            "last_error_id": last_error.get("id"),
            "action": "CONSOLIDATE_ERRORS",
        }

    return {
        "is_cascading": False,
        "error_count": len(error_comments),
        "last_error_id": error_comments[-1].get("id") if error_comments else None,
        "action": "PROCEED",
    }


def _consolidate_duplicate_rescue_comments(
    token: str,
    repo: str,
    pr_number: int,
    marker: str,
    signature: str,
    created_id: int,
) -> None:
    """Collapse same-SHA rescue-comment races into one appended thread.

    Cascade detection is intentionally handled by main() before this function is
    invoked.  Keeping duplicate consolidation focused on the canonical rescue
    thread avoids redundant PR comment polling and prevents a duplicate GET loop
    when the same-SHA race is already being resolved.
    """
    time.sleep(CONSOLIDATION_DELAY_SECONDS)
    matches = _matching_rescue_comments(token, repo, pr_number, marker, signature)
    if len(matches) <= 1:
        return

    # CIRCUIT BREAKER: Prevent cascading consolidation (Issue: PR #5324)
    # If more than 5 rescue comments exist for this SHA, skip consolidation
    # to avoid exponential growth and circular reference loops
    if len(matches) > 5:
        import sys
        print(f"⚠️  CIRCUIT BREAKER: {len(matches)} rescue comments detected for SHA {signature}.", file=sys.stderr)
        print("    Skipping consolidation to prevent cascading loop.", file=sys.stderr)
        return

    canonical = matches[0]
    canonical_id = canonical.get("id")
    canonical_body = (canonical.get("body") or "").rstrip()

    # If this process created a non-canonical duplicate, append its content to
    # the canonical thread, then delete only its own duplicate comment.  If this
    # process owns the canonical comment, fold in all later duplicates.
    duplicates = (
        [c for c in matches[1:] if c.get("id") == created_id]
        if canonical_id != created_id
        else matches[1:]
    )
    if not duplicates:
        return

    for duplicate in duplicates:
        duplicate_body = (duplicate.get("body") or "").replace(marker, "").strip()
        duplicate_digest = hashlib.sha256(duplicate_body.encode()).hexdigest()[
            :DUPLICATE_DIGEST_LENGTH
        ]
        # Use safe marker format to prevent circular reference in HTML-encoded PR body
        duplicate_marker = f"<!-- rescue-dup-digest:{duplicate_digest} -->"
        if duplicate_body and duplicate_marker not in canonical_body:
            canonical_body = (
                canonical_body
                + "\n\n---\n\n"
                + duplicate_marker
                + "\n"
                + "<details><summary>🔁 Consolidated duplicate rescue update</summary>\n\n"
                + duplicate_body
                + "\n\n</details>"
            )[:MAX_COMMENT_LEN]

    status, _ = _gh(
        "PATCH",
        f"/repos/{repo}/issues/comments/{canonical_id}",
        token,
        {"body": canonical_body},
    )
    if status not in (200, 201):
        print(f"⚠️  Duplicate consolidation PATCH returned HTTP {status}.")
        return

    for duplicate in duplicates:
        duplicate_id = duplicate.get("id")
        if duplicate_id and duplicate_id != canonical_id:
            delete_status, _ = _gh(
                "DELETE",
                f"/repos/{repo}/issues/comments/{duplicate_id}",
                token,
            )
            if delete_status in (200, 204):
                print(f"✅ Deleted duplicate rescue comment #{duplicate_id}.")
            else:
                print(
                    f"⚠️  Duplicate rescue comment #{duplicate_id} "
                    f"delete returned HTTP {delete_status}."
                )


def _get_branch_head_sha(token: str, repo: str, branch: str) -> str | None:
    """Return the current HEAD SHA for *branch*, or None on API error.

    Used by the self-suppress guard: if the branch has advanced past the
    commit that triggered a rescue comment, subsequent workflow re-runs for
    the old commit should not append new (false-positive) notifications.
    """
    import urllib.parse as _urlparse
    safe_branch = _urlparse.quote(branch, safe="")
    status, data = _gh("GET", f"/repos/{repo}/branches/{safe_branch}", token)
    if status == 200 and isinstance(data, dict):
        return (data.get("commit") or {}).get("sha")
    return None


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
    commit_sha = os.environ.get("COMMIT_SHA", "").strip()
    run_id = os.environ["RUN_ID"]
    run_url = os.environ["RUN_URL"]
    workflow = os.environ["WORKFLOW_NAME"]
    branch = os.environ.get("BRANCH", "").strip()

    # Optional: custom section title / content / append-only mode
    section_title = os.environ.get("SECTION_TITLE", "").strip()
    section_content = os.environ.get("SECTION_CONTENT", "").strip()
    append_only = os.environ.get("APPEND_ONLY", "false").strip().lower() == "true"

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

    # CRITICAL CASCADE CHECK: Handle cascading Copilot errors (PR #5324 pattern)
    # NEW BEHAVIOR: Instead of aborting, append to existing comment or queue for batch
    # This ensures no comments are lost and prevents multiple sprawling comments
    cascade_info = None
    try:
        cascade_info = _detect_cascading_copilot_errors(token, repo, pr_number)
    except Exception as exc:
        print(f"⚠️  Cascade check failed (non-blocking): {exc}", file=sys.stderr)
        # Continue execution—cascade check failure shouldn't block rescue posts

    # Defensive: when COMMIT_SHA or BRANCH env vars were not supplied (e.g. when
    # the calling workflow is triggered by an issue_comment or pull_request_review
    # event where github.event.pull_request.head.sha / github.head_ref are empty),
    # resolve them from the PR API so the comment always contains a valid SHA.
    if not commit_sha or not branch:
        _pr_status, _pr_data = _gh("GET", f"/repos/{repo}/pulls/{pr_number}", token)
        if _pr_status == 200 and isinstance(_pr_data, dict):
            _head = _pr_data.get("head") or {}
            if not commit_sha:
                commit_sha = _head.get("sha", "")
                if commit_sha:
                    print(
                        f"ℹ️  COMMIT_SHA resolved from PR #{pr_number} API: {commit_sha[:12]}"
                    )
                else:
                    print(
                        f"⚠️  COMMIT_SHA still empty after PR #{pr_number} API lookup — "
                        "head.sha not present in PR payload"
                    )
            if not branch:
                branch = _head.get("ref", "")
                if branch:
                    print(f"ℹ️  BRANCH resolved from PR #{pr_number} API: {branch!r}")
        else:
            print(
                f"⚠️  PR #{pr_number} API lookup returned HTTP {_pr_status} — "
                "COMMIT_SHA/BRANCH may be empty in rescue comment"
            )

    # Self-suppress: if the branch HEAD has advanced past the commit that
    # triggered this failure, the escalation targets a superseded commit and
    # would generate a false positive.  Fetch the current HEAD and skip if it
    # differs from COMMIT_SHA.  This prevents rescue comments from re-firing
    # on old SHAs when a new push already supersedes the failing run.
    if branch:
        head_sha = _get_branch_head_sha(token, repo, branch)
        if head_sha and head_sha != commit_sha:
            print(
                f"ℹ️  Branch '{branch}' HEAD is now {head_sha[:12]} "
                f"(failure targeted commit {sha_short}) — "
                "rescue comment suppressed (superseded commit)."
            )
            return

    # ONE rescue comment per PR per commit — all workflows share this marker.
    marker = f"<!-- ci-rescue-sha:{pr_number}:{sha_short} -->"
    visible_signature = f"**Branch:** `{branch}` | **Commit:** `{commit_sha}`"

    existing_id, existing_body = _find_rescue_comment(
        token, repo, pr_number, marker, visible_signature
    )

    # APPEND_ONLY mode: skip if no existing rescue comment found.
    if append_only and not existing_id:
        print(
            f"ℹ️  APPEND_ONLY=true but no existing rescue comment found for "
            f"commit {sha_short} — skipping."
        )
        return

    # CASCADE APPEND-FIRST: If cascade detected, prioritize appending to existing comment
    # or consolidating existing errors instead of creating a new comment
    if cascade_info and cascade_info.get("is_cascading"):
        action = cascade_info.get("action")
        count = cascade_info.get("error_count", 0)

        if action == "CONSOLIDATE_ERRORS":
            print(
                f"🔄 CASCADE CONSOLIDATION: {count} Copilot error comments detected. "
                f"Triggering error consolidation script.",
                file=sys.stderr,
            )
            # Try to consolidate the existing error comments
            try:
                consolidate_script = str(pathlib.Path(__file__).parent / "consolidate_cascade_errors.py")
                result = subprocess.run(
                    [
                        sys.executable,
                        consolidate_script,
                    ],
                    env={
                        **os.environ,
                        "GH_TOKEN": token,
                        "REPO": repo,
                        "PR_NUMBER": str(pr_number),
                    },
                    timeout=30,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    print(result.stdout, file=sys.stderr)
                    return  # Consolidation successful
                else:
                    print(f"⚠️  Consolidation script returned {result.returncode}", file=sys.stderr)
                    if result.stderr:
                        print(result.stderr, file=sys.stderr)
            except Exception as exc:
                print(f"⚠️  Failed to run consolidation script: {exc}", file=sys.stderr)
            # Fall through to normal rescue comment creation

        elif action == "ALREADY_CONSOLIDATED":
            print(
                f"✅ CASCADE ALREADY CONSOLIDATED: {count} Copilot error comments detected "
                f"(already consolidated). No new rescue comment needed.",
                file=sys.stderr,
            )
            return  # Cascade already handled, no new comment needed

        elif action == "APPEND_TO_EXISTING":
            print(
                f"🔄 CASCADE APPEND: {count} Copilot error comments detected. "
                f"Action: APPEND_TO_EXISTING. Attempting append-first strategy.",
                file=sys.stderr,
            )
            # Try to append to existing comment or queue for batch
            if _handle_cascade_append(
                token,
                repo,
                pr_number,
                commit_sha,
                existing_id,
                workflow,
                run_id,
                run_url,
                section_title,
                section_content,
            ):
                return  # Successfully appended or queued
            # If append failed and no existing comment, fall through to normal create

    if existing_id:
        # Append this workflow's section to the existing comment (collapsed).
        append_section = _build_append_section(
            workflow_name=workflow,
            run_id=run_id,
            run_url=run_url,
            section_title=section_title,
            section_content=section_content,
            timestamp=now,
            commit_sha=commit_sha,
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
        # pathlib already imported
        import sys as _sys
        _scripts_ci = str(pathlib.Path(__file__).parent)
        if _scripts_ci not in _sys.path:
            _sys.path.insert(0, _scripts_ci)
        from discussion_context_store import build_comment_context  # noqa: PLC0415
        inline_ctx = build_comment_context(pr_number, commit_sha, repo, token)
    except ModuleNotFoundError as exc:
        # Graceful degradation — inline context is optional; rescue comment still posts.
        # Only treat it as "optional module absent" when the top-level module itself is
        # missing; transitive import failures (exc.name != "discussion_context_store")
        # are routed to the generic handler so packaging issues stay visible.
        if exc.name == "discussion_context_store":
            print(
                f"ℹ️  Inline context unavailable: optional module not found "
                f"({exc.name}). Continuing without context."
            )
        else:
            print(
                f"⚠️  Inline context import/build failed: {exc}. "
                f"Continuing without context."
            )
    except Exception as exc:
        # Graceful degradation — inline context is optional; rescue comment still posts.
        print(
            f"⚠️  Inline context import/build failed: {exc}. "
            f"Continuing without context."
        )

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
        f"4. Update `docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md`\n"
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
        if isinstance(resp, dict) and resp.get("id"):
            _consolidate_duplicate_rescue_comments(
                token,
                repo,
                pr_number,
                marker,
                visible_signature,
                int(resp["id"]),
            )
    else:
        msg = resp.get("message", "") if isinstance(resp, dict) else str(resp)
        # 429 is always a rate limit; 403 is a rate limit when the message says so.
        # (GitHub uses 403 for installation-token rate limits, 429 for secondary limits.)
        is_rate_limit = status == 429 or (
            status == 403 and "rate limit" in msg.lower()
        )
        if is_rate_limit:
            # Rate limited: queue for batch posting instead of losing the comment
            batch_queue = _get_batch_queue_module()
            if batch_queue:
                try:
                    batch_queue.queue_item(
                        pr_number=pr_number,
                        commit_sha=commit_sha,
                        workflow_name=workflow,
                        run_id=run_id,
                        run_url=run_url,
                        section_title=section_title,
                        section_content=section_content,
                    )
                    print(
                        f"⚠️  POST skipped: HTTP {status} — rate limit exceeded. "
                        "Queued for batch posting on next workflow run."
                    )
                    sys.exit(0)
                except Exception as exc:
                    print(
                        f"⚠️  POST skipped: HTTP {status} — rate limit exceeded. "
                        f"Batch queue also failed: {exc}. "
                        "Rescue comment will be attempted on next run."
                    )
                    sys.exit(0)
            else:
                # Rescue comment is best-effort; transient rate limits must not fail CI.
                print(
                    f"⚠️  POST skipped: HTTP {status} — rate limit exceeded. "
                    "Rescue comment will be posted on the next run."
                )
                sys.exit(0)
        print(f"❌ POST failed: HTTP {status} — {resp}")
        sys.exit(1)


if __name__ == "__main__":
    main()
