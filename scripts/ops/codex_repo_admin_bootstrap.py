#!/usr/bin/env python3
"""
codex_repo_admin_bootstrap.py

Purpose:
  Bootstrap a repository to sane defaults:
    - Create/update standard labels from JSON
    - Ensure CODEOWNERS exists/updated (via Contents API)
    - Harden default branch protection (reviews, code-owner reviews, status checks, conversation resolution)
    - Enable repo security features via PATCH /repos (secret scanning, push protection, dependabot updates)

Defaults to DRY-RUN to avoid accidental network calls. Explicit --apply required.

Environment (strongly recommended):
  CODEX_NET_MODE=online_allowlist
  CODEX_ALLOWLIST_HOSTS=api.github.com
  GITHUB_APP_INSTALLATION_TOKEN=<short-lived token>  # or GITHUB_TOKEN (PAT fine-grained)
  GITHUB_API_BASE=https://api.github.com

Docs:
  - Update a repository (security_and_analysis toggles)
  - Create/Update file contents (CODEOWNERS)
  - Branch protection update (require code owner reviews, conversation resolution)
  - Labels API (create/update)
"""

from __future__ import annotations
import argparse
import base64
import json
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

API = os.getenv("GITHUB_API_BASE", "https://api.github.com").rstrip("/")


@lru_cache(maxsize=1)
def _requests():
    import requests  # type: ignore

    return requests


def _auth_headers() -> Dict[str, str]:
    token = os.getenv("GITHUB_APP_INSTALLATION_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Provide GITHUB_APP_INSTALLATION_TOKEN or GITHUB_TOKEN")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _allowlisted() -> None:
    mode = os.getenv("CODEX_NET_MODE", "offline")
    allow = {h.strip() for h in os.getenv("CODEX_ALLOWLIST_HOSTS", "").split(",") if h.strip()}
    if mode != "online_allowlist" or "api.github.com" not in allow:
        raise SystemExit(
            "Online mode not permitted (set CODEX_NET_MODE=online_allowlist and add api.github.com to CODEX_ALLOWLIST_HOSTS)."
        )


def _req(method: str, url: str, *, json_body: Any | None = None):
    requests = _requests()
    r = requests.request(method, url, headers=_auth_headers(), json=json_body, timeout=20)
    if r.status_code >= 400:
        raise SystemExit(f"{method} {url} failed: {r.status_code} {r.text}")
    return r


# -------------------------
# Labels
# -------------------------


def plan_labels(
    owner: str, repo: str, labels: List[Dict[str, Any]]
) -> List[Tuple[str, Dict[str, Any]]]:
    """Return a list of ('create'|'update', payload) operations. When applied, POST/PATCH label endpoints are used."""
    ops: List[Tuple[str, Dict[str, Any]]] = []
    for lb in labels:
        name = lb["name"]
        payload = {
            "name": name,
            "color": lb.get("color", "ededed").lstrip("#"),
            "description": lb.get("description", ""),
        }
        # In 'apply' we will check existence and swap endpoint to PATCH as needed.
        ops.append(("upsert", payload))
    return ops


def apply_labels(owner: str, repo: str, labels: List[Dict[str, Any]]) -> None:
    # list existing labels (best-effort); fallback to creating all
    existing = {}
    try:
        r = _req("GET", f"{API}/repos/{owner}/{repo}/labels")
        for item in r.json():
            existing[item["name"].lower()] = item
    except SystemExit:
        existing = {}
    for lb in labels:
        name = lb["name"]
        payload = {
            "name": name,
            "color": lb.get("color", "ededed").lstrip("#"),
            "description": lb.get("description", ""),
        }
        if name.lower() in existing:
            requests = _requests()
            _req(
                "PATCH",
                f"{API}/repos/{owner}/{repo}/labels/{requests.utils.quote(name, safe='')}",
                json_body={"new_name": name, **payload},
            )
        else:
            _req("POST", f"{API}/repos/{owner}/{repo}/labels", json_body=payload)


# -------------------------
# CODEOWNERS
# -------------------------


def upsert_codeowners(owner: str, repo: str, branch: str, content: str, message: str) -> None:
    """PUT contents API to .github/CODEOWNERS on default branch."""
    path = ".github/CODEOWNERS"
    # fetch current sha (if exists)
    sha = None
    url = f"{API}/repos/{owner}/{repo}/contents/{path}"
    requests = _requests()
    r = requests.get(url, headers=_auth_headers(), timeout=20, params={"ref": branch})
    if r.status_code == 200:
        sha = r.json().get("sha")
    elif r.status_code != 404:
        raise SystemExit(f"GET {url} failed: {r.status_code} {r.text}")
    body = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": branch,
    }
    if sha:
        body["sha"] = sha
    _req("PUT", url, json_body=body)


# -------------------------
# Repo settings + security
# -------------------------


def patch_repo_settings(owner: str, repo: str) -> None:
    payload = {
        "allow_squash_merge": True,
        "allow_merge_commit": False,
        "allow_rebase_merge": False,
        "allow_auto_merge": True,
        "delete_branch_on_merge": True,
        # security_and_analysis toggles (Advanced Security features / push protection)
        "security_and_analysis": {
            "secret_scanning": {"status": "enabled"},
            "secret_scanning_push_protection": {"status": "enabled"},
            "dependabot_security_updates": {"status": "enabled"},
        },
    }
    _req("PATCH", f"{API}/repos/{owner}/{repo}", json_body=payload)


# -------------------------
# Branch protection
# -------------------------


def put_branch_protection(owner: str, repo: str, branch: str, checks: List[str]) -> None:
    payload = {
        "required_status_checks": {"strict": True, "contexts": checks},
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
            "required_approving_review_count": 2,
            "require_last_push_approval": True,
        },
        "restrictions": None,
        "required_linear_history": True,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "block_creations": True,
        "required_conversation_resolution": True,
        "lock_branch": False,
        "allow_fork_syncing": False,
    }
    _req("PUT", f"{API}/repos/{owner}/{repo}/branches/{branch}/protection", json_body=payload)


# -------------------------
# CLI
# -------------------------


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description="Bootstrap a repository to sane defaults (dry-run by default)."
    )
    p.add_argument("--owner", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--default-branch", default="main")
    p.add_argument("--labels-json", type=Path, help="Path to labels.json (optional)")
    p.add_argument("--codeowners", type=Path, help="Path to CODEOWNERS template (optional)")
    p.add_argument(
        "--status-check",
        action="append",
        default=[],
        help="Required status check context (repeatable)",
    )
    p.add_argument(
        "--apply", action="store_true", help="Execute calls (network). Default is dry-run."
    )
    args = p.parse_args(argv)

    # Always require allowlist when applying
    if args.apply:
        _allowlisted()

    plan = {
        "owner": args.owner,
        "repo": args.repo,
        "default_branch": args.default_branch,
        "ops": [],
    }

    if args.labels_json and args.labels_json.exists():
        labels = json.loads(args.labels_json.read_text(encoding="utf-8"))
        plan["ops"].append({"labels": labels})
        if args.apply:
            apply_labels(args.owner, args.repo, labels)

    if args.codeowners and args.codeowners.exists():
        content = args.codeowners.read_text(encoding="utf-8")
        plan["ops"].append({"codeowners": ".github/CODEOWNERS"})
        if args.apply:
            upsert_codeowners(
                args.owner,
                args.repo,
                args.default_branch,
                content,
                "chore: ensure CODEOWNERS present",
            )

    # Repo settings + security
    plan["ops"].append({"repo_settings": True, "security_and_analysis": True})
    if args.apply:
        patch_repo_settings(args.owner, args.repo)

    # Branch protection
    plan["ops"].append(
        {"branch_protection": {"branch": args.default_branch, "checks": args.status_check}}
    )
    if args.apply:
        put_branch_protection(args.owner, args.repo, args.default_branch, args.status_check)

    print(json.dumps({"ok": True, "dry_run": not args.apply, "plan": plan}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAborted by user.", file=sys.stderr)
        sys.exit(130)
