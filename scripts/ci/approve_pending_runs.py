#!/usr/bin/env python3
"""Approve only independently requested, labelled, current PR workflow runs.

Mirrors the post_rescue_comment.py pattern — uses the Cognitive Brain GitHub
App installation token (primary) or CODEX_MASTER_KEY PAT (fallback) to call
  POST /repos/{owner}/{repo}/actions/runs/{run_id}/approve
on eligible pending runs. A token or label is not independent approval:
unknown identity, self-approval and ambiguous PR associations are denied.
GitHub rejection is final; it never triggers a rerun fallback.

Token priority
--------------
1. Cognitive Brain App installation token
     (_GITHUB_APP_ID + _GITHUB_APP_PRIVATE_KEY + _GITHUB_APP_INSTALLATION_ID)
     Actual installation scope must be verified by the maintainer.
2. CODEX_MASTER_KEY  (PAT with repo + workflow + actions:write)
3. CODEX_BACKUP_KEY  (fallback PAT)
4. GH_TOKEN          (verified account token; GitHub still enforces its scopes)

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

App-token env vars (all optional — enables repository-scoped App approval)
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
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ or __name__ != "__main__":
    from scripts.ci import require_wec_auto_approve as package_gate

    label_gate = package_gate
    label_valid = package_gate.label_valid
else:
    import require_wec_auto_approve as script_gate

    label_gate = script_gate
    label_valid = script_gate.label_valid

# ── Helpers ───────────────────────────────────────────────────────────────────

COPILOT_BOT_LOGINS = {"Copilot", "github-copilot[bot]", "copilot-swe-agent[bot]"}


@dataclass(frozen=True)
class _AppIdentity:
    token: str = field(repr=False)
    login: str
    expires_at: float


_app_identity: _AppIdentity | None = None


def _verified_identity(token: str) -> dict[str, Any] | None:
    if _app_identity and token == _app_identity.token:
        if time.time() >= _app_identity.expires_at:
            return None
        return {"login": _app_identity.login, "type": "Bot"}
    status, identity = _gh("GET", "/user", token)
    if status == 200 and isinstance(identity, dict) and identity.get("type") == "User":
        return identity
    return None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _gh(
    method: str,
    path: str,
    token: str,
    body: dict[str, Any] | None = None,
    *,
    timeout: int = 20,
) -> tuple[int, Any]:
    """Minimal GitHub REST call — returns (status_code, parsed_json)."""
    if (
        not path.startswith("/")
        or path.startswith("//")
        or any(char in path for char in ("\r", "\n", "\0", "\\"))
    ):
        raise ValueError("invalid GitHub API path")
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "codex-approve-pending-runs/1.0",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())
        with opener.open(req, timeout=timeout) as resp:
            body_bytes = resp.read(1024 * 1024 + 1)
            if len(body_bytes) > 1024 * 1024:
                return 502, {"error": "GitHub API response exceeds size limit"}
            try:
                parsed = json.loads(body_bytes) if body_bytes.strip() else {}
            except json.JSONDecodeError as jde:
                parsed = {
                    "error": f"Invalid JSON from GitHub API: {jde}",
                    "raw": body_bytes[:200].decode("utf-8", errors="replace"),
                }
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
    Requires existing PyJWT + cryptography; missing dependencies fail closed.
    """
    global _app_identity
    _app_identity = None
    if not app_id.isdecimal() or not installation_id.isdecimal():
        print("App and installation IDs must be numeric", file=sys.stderr)
        return None
    try:
        import jwt as _jwt
    except ImportError:
        print(
            "App signing dependencies unavailable; falling back to verified PATs", file=sys.stderr
        )
        return None

    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 540, "iss": str(app_id)}
    try:
        app_jwt = _jwt.encode(payload, private_key_pem, algorithm="RS256")
    except Exception:
        print("App JWT signing failed", file=sys.stderr)
        return None

    repo = os.environ.get("REPO") or os.environ.get("GITHUB_REPOSITORY", "")
    parts = repo.split("/")
    if len(parts) != 2 or not all(parts):
        print("App token requires an explicit repository scope", file=sys.stderr)
        return None
    status, app = _gh("GET", "/app", app_jwt)
    if (
        status != 200
        or not isinstance(app, dict)
        or str(app.get("id")) != app_id
        or not isinstance(app.get("slug"), str)
        or not app["slug"]
    ):
        print("App identity could not be verified", file=sys.stderr)
        return None
    status, installation = _gh("GET", f"/app/installations/{installation_id}", app_jwt)
    if (
        status != 200
        or not isinstance(installation, dict)
        or str(installation.get("id")) != installation_id
        or str(installation.get("app_id")) != app_id
        or (installation.get("account") or {}).get("login", "").casefold() != parts[0].casefold()
        or installation.get("suspended_at") is not None
    ):
        print("App installation is not active for the repository owner", file=sys.stderr)
        return None
    path = f"/app/installations/{installation_id}/access_tokens"
    status, resp_body = _gh(
        "POST",
        path,
        app_jwt,
        {
            "repositories": [parts[1]],
            "permissions": {
                "actions": "write",
                "contents": "read",
                "pull_requests": "read",
                "issues": "write",
            },
        },
    )
    if status == 201 and isinstance(resp_body, dict):
        token = resp_body.get("token")
        try:
            expires_at = datetime.fromisoformat(resp_body["expires_at"].replace("Z", "+00:00"))
        except (KeyError, TypeError, ValueError, AttributeError):
            print("App token expiry is unavailable", file=sys.stderr)
            return None
        permissions = resp_body.get("permissions")
        if (
            isinstance(token, str)
            and token
            and expires_at.tzinfo is not None
            and expires_at.timestamp() > time.time()
            and isinstance(permissions, dict)
            and permissions.get("actions") == "write"
            and permissions.get("pull_requests") in {"read", "write"}
        ):
            _app_identity = _AppIdentity(token, app["slug"] + "[bot]", expires_at.timestamp())
            return token
        print("App token lacks verified approval permissions or a valid expiry", file=sys.stderr)
        return None
    print(f"App token mint failed (HTTP {status})", file=sys.stderr)
    return None


def _resolve_token() -> tuple[str, str]:
    """Return (token, source_label) using the priority chain:
    CB App → CODEX_MASTER_KEY → CODEX_BACKUP_KEY → GH_TOKEN.
    """
    app_key = (
        os.environ.get("GITHUB_APP_PRIVATE_KEY") or os.environ.get("_GITHUB_APP_PRIVATE_KEY", "")
    ).strip()
    app_id = (os.environ.get("GITHUB_APP_ID") or os.environ.get("_GITHUB_APP_ID", "")).strip()
    inst_id = (
        os.environ.get("GITHUB_APP_INSTALLATION_ID")
        or os.environ.get("_GITHUB_APP_INSTALLATION_ID", "")
    ).strip()

    if app_key and app_id and inst_id:
        print(
            "ℹ️  Trying Cognitive Brain App installation token…"
        )  # codeql[py/clear-text-logging-sensitive-data]
        token = _mint_app_token(app_id, app_key, inst_id)
        if token and _verified_identity(token):
            return token, "cognitive-brain-app"
        print(
            "⚠️  App token unavailable — falling back to PAT"
        )  # codeql[py/clear-text-logging-sensitive-data]

    for env_name in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GH_TOKEN"):
        val = os.environ.get(env_name, "").strip()
        if val:
            status, identity = _gh("GET", "/user", val)
            if status == 200 and isinstance(identity, dict) and identity.get("type") == "User":
                print(f"Using verified {env_name}")
                return val, env_name
            print(f"{env_name} identity unavailable (HTTP {status})", file=sys.stderr)

    print("❌ No token available — set GH_TOKEN, CODEX_MASTER_KEY, or App secrets", file=sys.stderr)
    raise SystemExit(1)


def _has_wec_auto_approve_label(
    token: str, repo: str, pr_number: str | int, *, ttl_hours: int = 1
) -> bool:
    """Require a valid label-based WEC auto-approve gate before approving a PR.

    The permanent label (wec:auto-approve) is always allowed. The one-session label
    (wec:auto-approve-once) is also allowed only while it remains within the TTL window.
    """
    status, payload = _gh("GET", f"/repos/{repo}/pulls/{pr_number}", token)
    if status != 200 or not isinstance(payload, dict):
        return False

    return label_valid(token, repo, pr_number, payload, _gh, ttl_hours=ttl_hours)


def _filter_prs_by_wec_label(
    token: str, repo: str, prs: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Return only PRs currently opted into WEC auto-approval."""
    authorized: list[dict[str, Any]] = []
    for pr in prs:
        pr_number = pr.get("number")
        if pr_number is None:
            continue
        if _has_wec_auto_approve_label(token, repo, pr_number):
            authorized.append(pr)
        else:
            print(f"⏭️  Skipping PR #{pr_number}: missing or expired required auto-approve label")
    return authorized


def _search_wec_labelled_prs(token: str, repo: str) -> list[tuple[str, str]]:
    """Inventory labelled PRs completely; failed or truncated searches are unknown."""
    results: dict[int, str] = {}
    for label in ("wec:auto-approve", "wec:auto-approve-once"):
        seen: set[int] = set()
        expected_total: int | None = None
        for page in range(1, 11):
            q = urllib.parse.quote(f"repo:{repo} is:pr is:open label:{label}")
            status, payload = _gh("GET", f"/search/issues?q={q}&per_page=100&page={page}", token)
            if status != 200 or not isinstance(payload, dict):
                raise RuntimeError(f"Could not search PRs (HTTP {status})")
            items, total = _inventory_page(payload, "items")
            if payload.get("incomplete_results") is not False or total > 1000:
                raise RuntimeError("Incomplete PR search inventory")
            if expected_total is not None and total != expected_total:
                raise RuntimeError("PR search inventory changed during pagination")
            expected_total = total
            for item in items:
                pr_num = item.get("number")
                if type(pr_num) is not int or pr_num <= 0 or pr_num in seen:
                    raise RuntimeError("Invalid or repeated PR search identity")
                seen.add(pr_num)
                results[pr_num] = ""
            if _inventory_complete(len(items), len(seen), total):
                break
        else:
            raise RuntimeError("PR search inspection budget exhausted")

    if not results:
        return []

    targets: list[tuple[str, str]] = []
    for pr_num in results:
        status, payload = _gh("GET", f"/repos/{repo}/pulls/{pr_num}", token)
        if status != 200 or not isinstance(payload, dict):
            raise RuntimeError(f"Could not inspect discovered PR (HTTP {status})")
        sha = _inventory_pr_sha(payload)
        labels = payload.get("labels")
        if not isinstance(labels, list) or not all(
            isinstance(label, dict) and isinstance(label.get("name"), str) for label in labels
        ):
            raise RuntimeError("Malformed discovered PR labels")
        if payload.get("state") not in {"open", "closed"}:
            raise RuntimeError("Malformed discovered PR state")
        if payload["state"] == "open" and label_valid(token, repo, pr_num, payload, _gh):
            targets.append((str(pr_num), sha))
    return targets


def _inventory_page(payload: dict[str, Any], key: str) -> tuple[list[dict[str, Any]], int]:
    items = payload.get(key)
    total = payload.get("total_count")
    if (
        not isinstance(items, list)
        or len(items) > 100
        or not all(isinstance(item, dict) for item in items)
        or type(total) is not int
        or total < 0
    ):
        raise RuntimeError("Malformed inventory response")
    return items, total


def _inventory_complete(page_size: int, seen: int, total: int) -> bool:
    if seen > total or (page_size < 100 and seen != total):
        raise RuntimeError("Incomplete or inconsistent inventory pagination")
    return seen == total


def _inventory_pr_sha(pr: dict[str, Any]) -> str:
    head = pr.get("head")
    sha = head.get("sha") if isinstance(head, dict) else None
    if not isinstance(sha, str) or not sha.strip():
        raise RuntimeError("Malformed PR head in inventory")
    return sha


def _get_action_required_runs(
    token: str,
    repo: str,
    head_sha: str | None = None,
) -> list[dict[str, Any]]:
    """List all action_required workflow runs, optionally filtered by SHA."""
    all_runs: list[dict[str, Any]] = []
    seen: set[int] = set()
    expected_total: int | None = None
    for page in range(1, 101):
        path = f"/repos/{repo}/actions/runs?status=action_required&per_page=100&page={page}"
        if head_sha:
            path += f"&head_sha={head_sha}"
        status, data = _gh("GET", path, token)
        if status != 200 or not isinstance(data, dict):
            raise RuntimeError(f"Could not list runs (HTTP {status})")
        runs, total = _inventory_page(data, "workflow_runs")
        if expected_total is not None and total != expected_total:
            raise RuntimeError("Run inventory changed during pagination")
        expected_total = total
        for run in runs:
            run_id = run.get("id")
            if (
                type(run_id) is not int
                or run_id <= 0
                or run_id in seen
                or not isinstance(run.get("head_sha"), str)
                or not run["head_sha"].strip()
            ):
                raise RuntimeError("Invalid or repeated run inventory identity")
            seen.add(run_id)
        all_runs.extend(runs)
        if _inventory_complete(len(runs), len(seen), total):
            break
    else:
        raise RuntimeError("Run inventory inspection budget exhausted")
    return all_runs


def _approve_run(
    token: str,
    repo: str,
    run: dict[str, Any],
    *,
    dry_run: bool = False,
) -> str:
    """Approve a single action_required run.  Returns status label."""
    run_id = run["id"]
    run_name = run.get("name") or str(run.get("workflow_id", run_id))
    label = f"{run_name} (#{run_id})"

    if dry_run:
        print(f"  [DRY] Would approve: {label}")  # codeql[py/clear-text-logging-sensitive-data]
        return "dry-run"

    # Primary: approve endpoint (works for fork PRs and App-level tokens)
    status, body = _gh("POST", f"/repos/{repo}/actions/runs/{run_id}/approve", token)
    if status in (201, 204):
        print(f"  ✅ Approved: {label}")  # codeql[py/clear-text-logging-sensitive-data]
        return "approved"
    print(f"  ❌ Approval denied by GitHub (HTTP {status}): {label}", file=sys.stderr)
    return "error"


def _get_open_pr_shas(token: str, repo: str) -> list[tuple[str, str]]:
    """Return list of (pr_number, head_sha) for all open PRs."""
    pairs: list[tuple[str, str]] = []
    seen: set[int] = set()
    for page in range(1, 101):
        status, data = _gh("GET", f"/repos/{repo}/pulls?state=open&per_page=100&page={page}", token)
        if status != 200 or not isinstance(data, list):
            raise RuntimeError(f"Could not list open PRs (HTTP {status})")
        if len(data) > 100:
            raise RuntimeError("Oversized PR inventory page")
        for pr in data:
            if not isinstance(pr, dict):
                raise RuntimeError("Malformed PR inventory entry")
            num = pr.get("number")
            if type(num) is not int or num <= 0 or num in seen:
                raise RuntimeError("Invalid or repeated PR inventory identity")
            seen.add(num)
            pairs.append((str(num), _inventory_pr_sha(pr)))
        if len(data) < 100:
            break
    else:
        raise RuntimeError("PR inventory inspection budget exhausted")
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
            print(
                f"⚠️  Could not list PR comments (HTTP {status}): {data}", file=sys.stderr
            )  # codeql[py/clear-text-logging-sensitive-data]
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
                print(
                    f"  [DRY] Would remove stale 👀: {label}"
                )  # codeql[py/clear-text-logging-sensitive-data]
                removed += 1
                continue
            status, body = _gh(
                "DELETE",
                f"/repos/{repo}/issues/comments/{comment_id}/reactions/{reaction_id}",
                token,
            )
            if status == 204:
                print(
                    f"  ✅ Removed stale 👀: {label}"
                )  # codeql[py/clear-text-logging-sensitive-data]
                removed += 1
                continue
            msg = body.get("message", "") if isinstance(body, dict) else str(body)
            print(
                f"  ⚠️  Could not remove stale 👀 ({label}) — HTTP {status}: {msg}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            blocked += 1

    return removed, blocked


# ── Main ─────────────────────────────────────────────────────────────────────


def _authorize_run(
    token: str, repo: str, pr_number: str, head_sha: str, run: dict[str, Any]
) -> str:
    """Revalidate independently attributed maintainer approval at the current SHA."""
    identity = _verified_identity(token)
    if identity is None:
        return "unknown-approver-identity"
    approver = str(identity.get("login", "")).casefold()
    requester = os.environ.get("GITHUB_ACTOR", "").casefold()
    triggering_requester = os.environ.get("GITHUB_TRIGGERING_ACTOR", "").casefold()
    if not approver or not requester or not triggering_requester:
        return "unknown-requester-identity"
    status, current_run = _gh("GET", f"/repos/{repo}/actions/runs/{run['id']}", token)
    if status != 200 or not isinstance(current_run, dict):
        return "unknown-run"
    if current_run.get("head_sha") != head_sha or run.get("head_sha") != head_sha:
        return "stale-head-sha"
    if current_run.get("conclusion") != "action_required":
        return "run-not-action-required"
    associations = current_run.get("pull_requests")
    if (
        not isinstance(associations, list)
        or len(associations) != 1
        or not isinstance(associations[0], dict)
        or str(associations[0].get("number")) != pr_number
    ):
        return "unknown-or-mismatched-pr-association"
    status, pr = _gh("GET", f"/repos/{repo}/pulls/{pr_number}", token)
    if status != 200 or not isinstance(pr, dict):
        return "unknown-pr"
    if pr.get("state") != "open" or (pr.get("head") or {}).get("sha") != head_sha:
        return "stale-head-sha"
    author = str((pr.get("user") or {}).get("login", "")).casefold()
    run_actors = {
        str((current_run.get(key) or {}).get("login", "")).casefold()
        for key in ("actor", "triggering_actor")
    }
    if not author or "" in run_actors:
        return "unknown-author-identity"
    approval_actors = {approver}
    # Automatic events request inspection; they are not the platform approver.
    if identity["type"] != "Bot" and os.environ.get("GITHUB_EVENT_NAME") not in {
        "pull_request_target",
        "workflow_run",
        "issue_comment",
        "schedule",
    }:
        approval_actors.update({requester, triggering_requester})
    if approval_actors & (run_actors | {author}):
        return "self-approval"
    if not _has_wec_auto_approve_label(token, repo, pr_number):
        return "missing-or-expired-label"
    # A label expresses opt-in, not independent review of the current commit.
    reviews: dict[str, dict[str, Any]] = {}
    for page in range(1, 11):
        status, batch = _gh(
            "GET", f"/repos/{repo}/pulls/{pr_number}/reviews?per_page=100&page={page}", token
        )
        if status != 200 or not isinstance(batch, list):
            return "unknown-review-evidence"
        for review in batch:
            if not isinstance(review, dict):
                return "unknown-review-evidence"
            reviewer = str((review.get("user") or {}).get("login", "")).casefold()
            if reviewer and review.get("state") != "COMMENTED":
                reviews[reviewer] = review
        if len(batch) < 100:
            break
    else:
        return "review-inspection-budget-exhausted"
    if not any(
        reviewer not in run_actors | {author}
        and (
            (
                (review.get("user") or {}).get("type") == "User"
                and review.get("author_association") in {"OWNER", "MEMBER", "COLLABORATOR"}
            )
            or (
                identity["type"] == "Bot"
                and reviewer == approver
                and (review.get("user") or {}).get("type") == "Bot"
            )
        )
        and review.get("state") == "APPROVED"
        and review.get("commit_id") == head_sha
        for reviewer, review in reviews.items()
    ):
        return "missing-independent-current-review"
    # Separate lookups must remain bound to the same final PR context.
    status, latest = _gh("GET", f"/repos/{repo}/pulls/{pr_number}", token)
    if (
        status != 200
        or not isinstance(latest, dict)
        or latest.get("state") != "open"
        or (latest.get("head") or {}).get("sha") != head_sha
        or latest.get("labels") != pr.get("labels")
    ):
        return "changed-pr-context"
    return "authorized"


def _event_target(token: str, repo: str) -> tuple[str, str] | None:
    """Resolve trusted event metadata; final authorization rechecks the live run/PR."""
    event_name = os.environ.get("GITHUB_EVENT_NAME")
    if event_name not in {"pull_request_target", "issue_comment", "workflow_run"}:
        return None
    with Path(os.environ["GITHUB_EVENT_PATH"]).open(encoding="utf-8") as stream:
        event = json.load(stream)
    if event_name == "pull_request_target":
        pr = event.get("pull_request")
    elif event_name == "issue_comment":
        issue = event.get("issue", {})
        if not issue.get("pull_request"):
            return None
        number = issue.get("number")
        if type(number) is not int or number <= 0:
            raise RuntimeError("Invalid event PR identity")
        status, pr = _gh("GET", f"/repos/{repo}/pulls/{number}", token)
        if status != 200:
            raise RuntimeError("Event PR inspection unavailable")
    else:
        run_id = (event.get("workflow_run") or {}).get("id")
        if type(run_id) is not int or run_id <= 0:
            raise RuntimeError("Invalid event run identity")
        status, run = _gh("GET", f"/repos/{repo}/actions/runs/{run_id}", token)
        if status != 200 or not isinstance(run, dict):
            raise RuntimeError("Event run inspection unavailable")
        associations = run.get("pull_requests")
        if not isinstance(associations, list) or len(associations) != 1:
            raise RuntimeError("Event run has ambiguous PR association")
        pr = associations[0]
        if not isinstance(pr, dict) or type(pr.get("number")) is not int:
            raise RuntimeError("Invalid event PR association")
        return str(pr["number"]), str(run["head_sha"])
    if not isinstance(pr, dict) or type(pr.get("number")) is not int or pr["number"] <= 0:
        raise RuntimeError("Invalid event PR context")
    return str(pr["number"]), _inventory_pr_sha(pr)


def _completed_once_grant(token: str, repo: str, pr_number: str, sha: str) -> int | None:
    """Bind cleanup to a real completed Copilot session following activation."""
    if os.environ.get("GITHUB_EVENT_NAME") != "workflow_run":
        return None
    with Path(os.environ["GITHUB_EVENT_PATH"]).open(encoding="utf-8") as stream:
        run_id = (json.load(stream).get("workflow_run") or {}).get("id")
    status, session = _gh("GET", f"/repos/{repo}/actions/runs/{run_id}", token)
    if status != 200 or not isinstance(session, dict):
        raise RuntimeError("Completed session inspection unavailable")
    if (
        session.get("name") != "Copilot coding agent"
        or session.get("status") != "completed"
        or session.get("head_sha") != sha
        or session.get("pull_requests") is None
        or len(session["pull_requests"]) != 1
        or str(session["pull_requests"][0].get("number")) != pr_number
    ):
        return None
    status, pr = _gh("GET", f"/repos/{repo}/pulls/{pr_number}", token)
    if status != 200 or not isinstance(pr, dict):
        raise RuntimeError("Session PR inspection unavailable")
    names = {label["name"] for label in pr.get("labels", [])}
    if label_gate.LABEL_NAME in names or label_gate.ONE_SESSION_LABEL_NAME not in names:
        return None
    activation = label_gate.once_activation(token, repo, pr_number, _gh)
    if activation is None:
        return None
    started = label_gate._parse_activation_time(session.get("run_started_at"))
    activated = label_gate._parse_activation_time(activation["created_at"])
    if started is None or activated is None or started < activated:
        return None
    return int(activation["id"])


def _consume_once_grant(
    token: str, repo: str, pr_number: str, sha: str, activation_id: int
) -> None:
    status, pr = _gh("GET", f"/repos/{repo}/pulls/{pr_number}", token)
    if status != 200 or not isinstance(pr, dict):
        raise RuntimeError("Once-grant cleanup PR inspection unavailable")
    if pr.get("state") != "open" or _inventory_pr_sha(pr) != sha:
        return
    names = {label["name"] for label in pr.get("labels", [])}
    if label_gate.LABEL_NAME in names or label_gate.ONE_SESSION_LABEL_NAME not in names:
        return
    if not label_valid(token, repo, pr_number, pr, _gh):
        return
    activation = label_gate.once_activation(token, repo, pr_number, _gh)
    if activation is None or activation["id"] != activation_id:
        return
    status, _ = _gh(
        "DELETE", f"/repos/{repo}/issues/{pr_number}/labels/wec%3Aauto-approve-once", token
    )
    if status != 200:
        raise RuntimeError(f"Once-grant cleanup denied (HTTP {status})")


def _run_decisions(decisions: list[dict[str, Any]]) -> int:
    repo = os.environ.get("REPO") or os.environ.get("GITHUB_REPOSITORY", "")
    head_sha = os.environ.get("HEAD_SHA", "").strip() or None
    pr_number = os.environ.get("PR_NUMBER", "").strip()
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    max_wait = int(os.environ.get("MAX_WAIT_SEC", "30"))
    if os.environ.get("APPROVAL_INTENT") in {"deny", "force_deny"}:
        decisions.append(
            {"rule": "explicit-denial", "pr": pr_number, "head_sha": head_sha, "outcome": "denied"}
        )
        return 1
    if not repo:
        decisions.append(
            {
                "rule": "missing-repository",
                "pr": pr_number,
                "head_sha": head_sha,
                "outcome": "denied",
            }
        )
        return 1
    if head_sha and not pr_number:
        decisions.append(
            {"rule": "missing-pr", "pr": None, "head_sha": head_sha, "outcome": "denied"}
        )
        return 1

    token, token_source = _resolve_token()
    if not head_sha and not pr_number:
        target = _event_target(token, repo)
        if target is not None:
            pr_number, head_sha = target
    mode_tag = "🔍 DRY-RUN" if dry_run else "🚀 LIVE"
    print(f"\n{'─'*60}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"⚡ approve_pending_runs — {mode_tag}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"   repo        : {repo}")  # codeql[py/clear-text-logging-sensitive-data]
    print(
        f"   head_sha    : {head_sha or '(all open PRs)'}"
    )  # codeql[py/clear-text-logging-sensitive-data]
    print(
        f"   pr_number   : {pr_number or '(all)'}"
    )  # codeql[py/clear-text-logging-sensitive-data]
    print(f"   token_source: {token_source}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"{'─'*60}\n")  # codeql[py/clear-text-logging-sensitive-data]

    # Collect (pr_number, head_sha) targets ───────────────────────────────────
    if head_sha and pr_number:
        if not _has_wec_auto_approve_label(token, repo, pr_number):
            print(
                f"⏭️  Skipping PR #{pr_number}: missing or expired required WEC approval label "
                "('wec:auto-approve' or active 'wec:auto-approve-once')"
            )
            decisions.append(
                {
                    "rule": "missing-or-expired-label",
                    "pr": pr_number,
                    "head_sha": head_sha,
                    "outcome": "denied",
                }
            )
            return 1
        targets = [(pr_number, head_sha)]
    elif pr_number:
        status, pr = _gh("GET", f"/repos/{repo}/pulls/{pr_number}", token)
        sha = (
            (pr.get("head") or {}).get("sha", "") if status == 200 and isinstance(pr, dict) else ""
        )
        if not sha:
            decisions.append(
                {"rule": "unknown-pr", "pr": pr_number, "head_sha": None, "outcome": "denied"}
            )
            return 1
        targets = [(pr_number, sha)]
    else:
        # Sweep mode: use Search API to find only WEC-labelled PRs in one query
        if os.environ.get("GITHUB_EVENT_NAME") != "schedule":
            decisions.append(
                {"rule": "missing-pr-context", "pr": None, "head_sha": None, "outcome": "denied"}
            )
            return 1
        print(
            "📋 Sweep mode — searching for WEC-labelled open PRs…"
        )  # codeql[py/clear-text-logging-sensitive-data]
        targets = _search_wec_labelled_prs(token, repo)
        print(
            f"   Found {len(targets)} authorized PR(s) with a valid WEC auto-approve label "
            "('wec:auto-approve' or active 'wec:auto-approve-once')"
        )  # codeql[py/clear-text-logging-sensitive-data]

    if not targets:
        decisions.append(
            {"rule": "no-authorized-targets", "pr": None, "head_sha": None, "outcome": "skipped"}
        )
        print(
            "ℹ️  No authorized targets — nothing to do."
        )  # codeql[py/clear-text-logging-sensitive-data]
        return 0

    # Wait briefly for runs to register after a fresh push ────────────────────
    total_approved = total_skipped = total_errors = 0
    waited = 0
    target_run_id = os.environ.get("TARGET_RUN_ID", "").strip()
    matched_target = False

    for pr_num, sha in targets:
        activation_id = _completed_once_grant(token, repo, pr_num, sha)
        print(
            f"\n── PR #{pr_num} @ {sha[:12]} ──────────────────────────────"
        )  # codeql[py/clear-text-logging-sensitive-data]
        runs: list[dict[str, Any]] = []

        # Poll until we see action_required runs (they may take a few seconds)
        deadline = time.time() + max_wait
        while True:
            runs = _get_action_required_runs(token, repo, head_sha=sha)
            if runs or time.time() >= deadline:
                break
            remaining = int(deadline - time.time())
            print(
                f"   ⏳ No action_required runs yet — waiting ({remaining}s left)…"
            )  # codeql[py/clear-text-logging-sensitive-data]
            time.sleep(5)
            waited += 5

        print(
            f"   Found {len(runs)} action_required run(s)"
        )  # codeql[py/clear-text-logging-sensitive-data]
        if not runs:
            decisions.append(
                {"rule": "no-pending-runs", "pr": pr_num, "head_sha": sha, "outcome": "skipped"}
            )
            print("   Nothing to approve.")  # codeql[py/clear-text-logging-sensitive-data]
            continue

        batch_start = len(decisions)
        for run in runs:
            if target_run_id and str(run.get("id")) != target_run_id:
                continue
            matched_target = True
            rule = _authorize_run(token, repo, pr_num, sha, run)
            result = (
                _approve_run(token, repo, run, dry_run=dry_run)
                if rule == "authorized"
                else "denied"
            )
            decision: dict[str, Any] = {
                "rule": rule,
                "pr": pr_num,
                "head_sha": sha,
                "run_id": run["id"],
                "outcome": result,
                "token_source": token_source,
            }
            if _app_identity and token == _app_identity.token:
                decision["approver"] = {"login": _app_identity.login, "type": "Bot"}
                decision["credential_expires_at"] = _app_identity.expires_at
            decisions.append(decision)
            if result in ("approved", "dry-run"):
                total_approved += 1
            elif result == "skipped":
                total_skipped += 1
            else:
                total_errors += 1
        batch = decisions[batch_start:]
        if (
            activation_id is not None
            and not dry_run
            and len(batch) == len(runs)
            and all(decision["outcome"] == "approved" for decision in batch)
        ):
            _consume_once_grant(token, repo, pr_num, sha, activation_id)

    # Summary ─────────────────────────────────────────────────────────────────
    print(f"\n{'─'*60}")  # codeql[py/clear-text-logging-sensitive-data]
    print(
        f"⚡ Summary — approved={total_approved}  skipped={total_skipped}  errors={total_errors}"
    )  # codeql[py/clear-text-logging-sensitive-data]
    if waited:
        print(
            f"   (waited {waited}s for runs to register)"
        )  # codeql[py/clear-text-logging-sensitive-data]
    print(f"{'─'*60}\n")  # codeql[py/clear-text-logging-sensitive-data]

    if target_run_id and not matched_target:
        decisions.append(
            {
                "rule": "target-run-not-in-pr-scope",
                "pr": pr_number,
                "head_sha": head_sha,
                "outcome": "denied",
            }
        )
        return 1
    return 1 if total_errors > 0 else 0


def main() -> int:
    decisions: list[dict[str, Any]] = []
    try:
        return _run_decisions(decisions)
    except (Exception, SystemExit):
        print("Approval inspection failed; no unverified approval is permitted", file=sys.stderr)
        decisions.append(
            {
                "rule": "inspection-error",
                "pr": os.environ.get("PR_NUMBER") or None,
                "head_sha": os.environ.get("HEAD_SHA") or None,
                "outcome": "denied",
            }
        )
        return 1
    finally:
        Path("approval-decision.json").write_text(
            json.dumps({"schema_version": 1, "decisions": decisions}, indent=2) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    sys.exit(main())
