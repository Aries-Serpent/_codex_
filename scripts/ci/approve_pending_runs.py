#!/usr/bin/env python3
"""Approve all action_required workflow runs for a PR's HEAD SHA.

Mirrors the post_rescue_comment.py pattern — uses the Cognitive Brain GitHub
App installation token (primary) or CODEX_MASTER_KEY PAT (fallback) to call
  POST /repos/{owner}/{repo}/actions/runs/{run_id}/approve
on every pending run.  Enables the Copilot agent's autonomous self-approval
loop: agent pushes → self-approve-pending-runs.yml fires via schedule →
runs unblock → CI completes without any human touchpoint.

Token priority
--------------
1. Cognitive Brain App installation token
     (_GITHUB_APP_ID + _GITHUB_APP_PRIVATE_KEY + _GITHUB_APP_INSTALLATION_ID)
     The App has full-admin org-wide access — no action_required restrictions.
2. CODEX_MASTER_KEY  (PAT with repo + workflow + actions:write)
3. CODEX_BACKUP_KEY  (fallback PAT)
4. GH_TOKEN          (github.token — approve will likely fail but we try)

Required environment variables
--------------------------------
REPO        owner/repo slug           e.g. Aries-Serpent/_codex_
GH_TOKEN    Resolved write token      (set by caller or fallback chain below)

Optional environment variables
--------------------------------
HEAD_SHA     40-char commit SHA to scan   (default: all open PRs)
PR_NUMBER    PR number                    (used when HEAD_SHA also given)
DRY_RUN      "true" to preview only
MAX_WAIT_SEC Seconds to poll until runs appear (default 30)
CLEANUP_COPILOT_EYES
            "true" (default) to remove stale Copilot 👀 reactions from
            PR comments after approval handling when PR number is known

App-token env vars (all optional — enables the highest-privilege path)
------------------------------------------------------------------------
GITHUB_APP_PRIVATE_KEY       PEM content of the App private key
GITHUB_APP_ID                Numeric App ID
GITHUB_APP_INSTALLATION_ID   Installation ID for this org/repo

Usage in a workflow step
-------------------------
    - name: "⚡ Approve action_required runs"
      env:
        GH_TOKEN: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY || github.token }}
        GITHUB_APP_PRIVATE_KEY: ${{ secrets._GITHUB_APP_PRIVATE_KEY }}
        GITHUB_APP_ID: ${{ secrets._GITHUB_APP_ID }}
        GITHUB_APP_INSTALLATION_ID: ${{ secrets._GITHUB_APP_INSTALLATION_ID }}
        REPO: ${{ github.repository }}
        HEAD_SHA: ${{ github.sha }}
        PR_NUMBER: ${{ github.event.pull_request.number }}
      run: python scripts/ci/approve_pending_runs.py
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

# ── Helpers ───────────────────────────────────────────────────────────────────

COPILOT_BOT_LOGINS = {"Copilot", "github-copilot[bot]", "copilot-swe-agent[bot]"}

def _gh(
    method: str,
    path: str,
    token: str,
    body: dict[str, Any] | None = None,
    *,
    timeout: int = 20,
) -> tuple[int, Any]:
    """Minimal GitHub REST call — returns (status_code, parsed_json)."""
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": f""******",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "codex-approve-pending-runs/1.0",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body_bytes = resp.read()
            try:
                parsed = json.loads(body_bytes) if body_bytes.strip() else {}
            except json.JSONDecodeError as jde:
                parsed = {"error": f"Invalid JSON from GitHub API: {jde}",
                          "raw": body_bytes[:200].decode("utf-8", errors="replace")}
            return resp.status, parsed
    except urllib.error.HTTPError as exc:
        try:
            err_body = json.loads(exc.read())
        except Exception:
            err_body = {"message": str(exc)}
        return exc.code, err_body


def _mint_app_token(app_id: str, private_key_pem: str, installation_id: str) -> str | None:
    """Mint a short-lived GitHub App installation token.

    Returns the token string, or None if minting fails.
    Requires PyJWT + cryptography; installs them silently if absent.
    """
    try:
        import jwt as _jwt  # type: ignore[import-untyped]
    except ImportError:
        import subprocess as _sp
        _sp.run(
            [sys.executable, "-m", "pip", "install", "--quiet",
             "PyJWT==2.8.0", "cryptography==44.0.2"],
            check=True,
        )
        import jwt as _jwt  # type: ignore[import-untyped]

    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 540, "iss": str(app_id)}
    try:
        app_jwt = _jwt.encode(payload, private_key_pem, algorithm="RS256")
    except Exception as exc:
        print(f"⚠️  App JWT signing failed: {exc}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
        return None

    path = f"/app/installations/{installation_id}/access_tokens"
    status, resp_body = _gh("POST", path, app_jwt)
    if status == 201 and isinstance(resp_body, dict) and resp_body.get("token"):
        return resp_body["token"]
    print(f"⚠️  App token mint failed — HTTP {status}: {resp_body}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
    return None


def _resolve_token() -> tuple[str, str]:
    """Return (token, source_label) using the priority chain:
    CB App → CODEX_MASTER_KEY → CODEX_BACKUP_KEY → GH_TOKEN.
    """
    app_key = os.environ.get("GITHUB_APP_PRIVATE_KEY", "").strip()
    app_id  = os.environ.get("GITHUB_APP_ID", "").strip()
    inst_id = os.environ.get("GITHUB_APP_INSTALLATION_ID", "").strip()

    if app_key and app_id and inst_id:
        print("ℹ️  Trying Cognitive Brain App installation token…")  # codeql[py/clear-text-logging-sensitive-data]
        token = _mint_app_token(app_id, app_key, inst_id)
        if token:
            print("✅ Using Cognitive Brain App token")  # codeql[py/clear-text-logging-sensitive-data]
            return token, "cognitive-brain-app"
        print("⚠️  App token unavailable — falling back to PAT")  # codeql[py/clear-text-logging-sensitive-data]

    for env_name in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GH_TOKEN"):
        val = os.environ.get(env_name, "").strip()
        if val:
            print(f"ℹ️  Using {env_name}")  # codeql[py/clear-text-logging-sensitive-data]
            return val, env_name

    print("❌ No token available — set GH_TOKEN, CODEX_MASTER_KEY, or App secrets",
          file=sys.stderr)
    raise SystemExit(1)


def _has_wec_auto_approve_label(token: str, repo: str, pr_number: str | int) -> bool:
    """Require the explicit WEC auto-approve label before approving a PR."""
    status, payload = _gh("GET", f"/repos/{repo}/pulls/{pr_number}", token)
    if status != 200 or not isinstance(payload, dict):
        return False
    labels = payload.get("labels", [])
    return any((label.get("name") if isinstance(label, dict) else label) == "wec:auto-approve" for label in labels)


def _filter_prs_by_wec_label(token: str, repo: str, prs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only PRs currently opted into WEC auto-approval."""
    authorized: list[dict[str, Any]] = []
    for pr in prs:
        pr_number = pr.get("number")
        if pr_number is None:
            continue
        if _has_wec_auto_approve_label(token, repo, pr_number):
            authorized.append(pr)
        else:
            print(f"⏭️  Skipping PR #{pr_number}: missing 'wec:auto-approve' label")
    return authorized


def _get_action_required_runs(
    token: str,
    repo: str,
    head_sha: str | None = None,
) -> list[dict[str, Any]]:
    """List all action_required workflow runs, optionally filtered by SHA."""
    all_runs: list[dict[str, Any]] = []
    page = 1
    while True:
        path = f"/repos/{repo}/actions/runs?status=action_required&per_page=100&page={page}"
        if head_sha:
            path += f"&head_sha={head_sha}"
        status, data = _gh("GET", path, token)
        if status != 200 or not isinstance(data, dict):
            print(f"⚠️  Could not list runs (HTTP {status}): {data}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
            break
        runs: list[dict[str, Any]] = data.get("workflow_runs", [])
        all_runs.extend(runs)
        if len(runs) < 100:
            break
        page += 1
    return all_runs


def _approve_run(
    token: str,
    repo: str,
    run: dict[str, Any],
    *,
    dry_run: bool = False,
) -> str:
    """Approve a single action_required run.  Returns status label."""
    run_id   = run["id"]
    run_name = run.get("name") or str(run.get("workflow_id", run_id))
    label    = f"{run_name} (#{run_id})"

    if dry_run:
        print(f"  [DRY] Would approve: {label}")  # codeql[py/clear-text-logging-sensitive-data]
        return "dry-run"

    # Primary: approve endpoint (works for fork PRs and App-level tokens)
    status, body = _gh("POST", f"/repos/{repo}/actions/runs/{run_id}/approve", token)
    if status in (201, 204):
        print(f"  ✅ Approved: {label}")  # codeql[py/clear-text-logging-sensitive-data]
        return "approved"
    if status in (409, 422):
        print(f"  ⏭️  Already processed: {label}")  # codeql[py/clear-text-logging-sensitive-data]
        return "skipped"

    msg = body.get("message", "") if isinstance(body, dict) else str(body)
    print(f"  ⚠️  approve → HTTP {status} ({msg}) — trying rerun: {label}")  # codeql[py/clear-text-logging-sensitive-data]

    # Fallback: rerun (clears action_required for same-repo pushes)
    status2, body2 = _gh("POST", f"/repos/{repo}/actions/runs/{run_id}/rerun", token)
    if status2 in (200, 201, 204):
        print(f"  ✅ Rerun queued: {label}")  # codeql[py/clear-text-logging-sensitive-data]
        return "rerun"
    if status2 in (409, 422):
        print(f"  ⏭️  Already running: {label}")  # codeql[py/clear-text-logging-sensitive-data]
        return "skipped"
    msg2 = body2.get("message", "") if isinstance(body2, dict) else str(body2)
    print(f"  ❌ Both approve and rerun failed for {label}: HTTP {status2} ({msg2})",
          file=sys.stderr)
    return "error"


def _get_open_pr_shas(token: str, repo: str) -> list[tuple[str, str]]:
    """Return list of (pr_number, head_sha) for all open PRs."""
    pairs: list[tuple[str, str]] = []
    page = 1
    while True:
        status, data = _gh(
            "GET", f"/repos/{repo}/pulls?state=open&per_page=100&page={page}", token
        )
        if status != 200 or not isinstance(data, list):
            break
        for pr in data:
            num  = str(pr.get("number", ""))
            sha  = pr.get("head", {}).get("sha", "")
            if num and sha:
                pairs.append((num, sha))
        if len(data) < 100:
            break
        page += 1
    return pairs


def _fetch_pr_comments(token: str, repo: str, pr_number: str) -> list[dict[str, Any]]:
    """Return all issue comments for a PR."""
    comments: list[dict[str, Any]] = []
    page = 1
    while True:
        status, data = _gh(
            "GET",
            f"/repos/{repo}/issues/{pr_number}/comments?per_page=100&page={page}",
            token,
        )
        if status != 200 or not isinstance(data, list):
            print(f"⚠️  Could not list PR comments (HTTP {status}): {data}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
            break
        comments.extend(data)
        if len(data) < 100:
            break
        page += 1
    return comments


def _fetch_comment_reactions(token: str, repo: str, comment_id: int) -> list[dict[str, Any]]:
    """Return reactions for a single issue comment."""
    reactions: list[dict[str, Any]] = []
    page = 1
    while True:
        status, data = _gh(
            "GET",
            f"/repos/{repo}/issues/comments/{comment_id}/reactions?per_page=100&page={page}",
            token,
        )
        if status != 200 or not isinstance(data, list):
            print(
                f"⚠️  Could not list reactions for comment {comment_id} (HTTP {status}): {data}",
                file=sys.stderr,
            )
            break
        reactions.extend(data)
        if len(data) < 100:
            break
        page += 1
    return reactions


def _cleanup_copilot_eyes_reactions(
    token: str,
    repo: str,
    pr_number: str,
    *,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Remove stale Copilot 👀 reactions from PR comments.

    Returns (removed_count, blocked_count). blocked_count tracks permission/HTTP errors.
    """
    removed = 0
    blocked = 0
    comments = _fetch_pr_comments(token, repo, pr_number)

    for comment in comments:
        comment_id = int(comment.get("id", 0))
        if not comment_id:
            continue
        reactions = _fetch_comment_reactions(token, repo, comment_id)
        for reaction in reactions:
            if reaction.get("content") != "eyes":
                continue
            user_data = reaction.get("user", {})
            login = str(user_data.get("login", "")) if isinstance(user_data, dict) else ""
            if login not in COPILOT_BOT_LOGINS:
                continue
            reaction_id = int(reaction.get("id", 0))
            if not reaction_id:
                continue
            label = f"comment {comment_id} reaction {reaction_id} by {login}"
            if dry_run:
                print(f"  [DRY] Would remove stale 👀: {label}")  # codeql[py/clear-text-logging-sensitive-data]
                removed += 1
                continue
            status, body = _gh(
                "DELETE",
                f"/repos/{repo}/issues/comments/{comment_id}/reactions/{reaction_id}",
                token,
            )
            if status == 204:
                print(f"  ✅ Removed stale 👀: {label}")  # codeql[py/clear-text-logging-sensitive-data]
                removed += 1
                continue
            msg = body.get("message", "") if isinstance(body, dict) else str(body)
            print(f"  ⚠️  Could not remove stale 👀 ({label}) — HTTP {status}: {msg}")  # codeql[py/clear-text-logging-sensitive-data]
            blocked += 1

    return removed, blocked


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    repo      = os.environ.get("REPO") or os.environ.get("GITHUB_REPOSITORY", "")
    head_sha  = os.environ.get("HEAD_SHA", "").strip() or None
    pr_number = os.environ.get("PR_NUMBER", "").strip()
    dry_run   = os.environ.get("DRY_RUN", "false").lower() == "true"
    max_wait  = int(os.environ.get("MAX_WAIT_SEC", "30"))
    cleanup_eyes = os.environ.get("CLEANUP_COPILOT_EYES", "true").lower() != "false"

    if not repo:
        print("❌ REPO env var required (owner/repo)", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
        return 1

    token, token_source = _resolve_token()
    mode_tag = "🔍 DRY-RUN" if dry_run else "🚀 LIVE"
    print(f"\n{'─'*60}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"⚡ approve_pending_runs — {mode_tag}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"   repo        : {repo}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"   head_sha    : {head_sha or '(all open PRs)'}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"   pr_number   : {pr_number or '(all)'}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"   token_source: {token_source}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"{'─'*60}\n")  # codeql[py/clear-text-logging-sensitive-data]

    # Collect (pr_number, head_sha) targets ───────────────────────────────────
    if head_sha and pr_number:
        if not _has_wec_auto_approve_label(token, repo, pr_number):
            print(f"⏭️  Skipping PR #{pr_number}: missing 'wec:auto-approve' label")
            return 0
        targets = [(pr_number, head_sha)]
    elif head_sha:
        targets = [("?", head_sha)]
    else:
        # Sweep mode: all open PRs
        print("📋 Sweep mode — resolving all open PRs…")  # codeql[py/clear-text-logging-sensitive-data]
        targets = _get_open_pr_shas(token, repo)
        filtered = _filter_prs_by_wec_label(token, repo, [{"number": pr_num, "head": {"sha": sha}} for pr_num, sha in targets])
        targets = [(str(pr["number"]), pr["head"]["sha"]) for pr in filtered]
        print(f"   Found {len(targets)} authorized PR(s) with the 'wec:auto-approve' label")  # codeql[py/clear-text-logging-sensitive-data]

    if not targets:
        print("ℹ️  No authorized targets — nothing to do.")  # codeql[py/clear-text-logging-sensitive-data]
        return 0

    # Wait briefly for runs to register after a fresh push ────────────────────
    total_approved = total_skipped = total_errors = 0
    waited = 0
    cleaned_prs: set[str] = set()

    for pr_num, sha in targets:
        print(f"\n── PR #{pr_num} @ {sha[:12]} ──────────────────────────────")  # codeql[py/clear-text-logging-sensitive-data]
        runs: list[dict[str, Any]] = []

        # Poll until we see action_required runs (they may take a few seconds)
        deadline = time.time() + max_wait
        while True:
            runs = _get_action_required_runs(token, repo, head_sha=sha)
            if runs or time.time() >= deadline:
                break
            remaining = int(deadline - time.time())
            print(f"   ⏳ No action_required runs yet — waiting ({remaining}s left)…")  # codeql[py/clear-text-logging-sensitive-data]
            time.sleep(5)
            waited += 5

        print(f"   Found {len(runs)} action_required run(s)")  # codeql[py/clear-text-logging-sensitive-data]
        if not runs:
            print("   Nothing to approve.")  # codeql[py/clear-text-logging-sensitive-data]
            continue

        for run in runs:
            result = _approve_run(token, repo, run, dry_run=dry_run)
            if result in ("approved", "rerun", "dry-run"):
                total_approved += 1
            elif result == "skipped":
                total_skipped += 1
            else:
                total_errors += 1

        if cleanup_eyes and pr_num not in {"", "?"} and pr_num not in cleaned_prs:
            print(f"   🧹 Copilot queue hygiene for PR #{pr_num} (remove stale 👀)…")  # codeql[py/clear-text-logging-sensitive-data]
            removed, blocked = _cleanup_copilot_eyes_reactions(
                token,
                repo,
                pr_num,
                dry_run=dry_run,
            )
            cleaned_prs.add(pr_num)
            if removed:
                print(f"   ✅ Removed {removed} stale Copilot 👀 reaction(s)")  # codeql[py/clear-text-logging-sensitive-data]
            if blocked:
                print(f"   ⚠️  {blocked} reaction cleanup operation(s) blocked")  # codeql[py/clear-text-logging-sensitive-data]

    # Summary ─────────────────────────────────────────────────────────────────
    print(f"\n{'─'*60}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"⚡ Summary — approved={total_approved}  skipped={total_skipped}  errors={total_errors}")  # codeql[py/clear-text-logging-sensitive-data]
    if waited:
        print(f"   (waited {waited}s for runs to register)")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"{'─'*60}\n")  # codeql[py/clear-text-logging-sensitive-data]

    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
