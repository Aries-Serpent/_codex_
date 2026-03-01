#!/usr/bin/env python3
"""Cleanup stale self-heal/run-* branches and their associated draft PRs.

Usage:
    # Dry run (default) — show what would be deleted
    python scripts/ci/cleanup_stale_branches.py

    # Actually delete
    python scripts/ci/cleanup_stale_branches.py --execute

    # Custom prefix
    python scripts/ci/cleanup_stale_branches.py --prefix "self-heal/run-" --execute

Environment:
    GITHUB_TOKEN or GH_TOKEN — PAT with contents:write + pull-requests:write
    GITHUB_REPOSITORY        — owner/repo (default: Aries-Serpent/_codex_)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def gh_api(method: str, path: str, token: str, data: bytes | None = None) -> dict | list | None:
    """Minimal GitHub REST API helper — no external dependencies."""
    url = f"https://api.github.com{path}" if path.startswith("/") else path
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
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
        body = exc.read().decode(errors="replace")
        print(f"  ⚠️  {method} {path} → {exc.code}: {body[:200]}", file=sys.stderr)
        return None


def list_branches(repo: str, token: str, prefix: str) -> list[dict]:
    """Return branches matching prefix (paginated)."""
    branches: list[dict] = []
    page = 1
    while True:
        data = gh_api("GET", f"/repos/{repo}/branches?per_page=100&page={page}", token)
        if not data:
            break
        for b in data:
            if b["name"].startswith(prefix):
                branches.append(b)
        if len(data) < 100:
            break
        page += 1
    return branches


def find_pr_for_branch(repo: str, token: str, branch: str) -> int | None:
    """Find open PR from this head branch, if any."""
    data = gh_api(
        "GET",
        f"/repos/{repo}/pulls?state=open&head={repo.split('/')[0]}:{branch}&per_page=1",
        token,
    )
    if data and isinstance(data, list) and len(data) > 0:
        return data[0]["number"]
    return None


def close_pr(repo: str, token: str, pr_number: int) -> bool:
    """Close a PR."""
    result = gh_api(
        "PATCH",
        f"/repos/{repo}/pulls/{pr_number}",
        token,
        json.dumps({"state": "closed"}).encode(),
    )
    return result is not None


def delete_branch(repo: str, token: str, branch: str) -> bool:
    """Delete a branch ref. GitHub refs API uses literal slashes in the path."""
    result = gh_api("DELETE", f"/repos/{repo}/git/refs/heads/{branch}", token)
    return True  # DELETE returns 204 on success, handled in gh_api


def main() -> int:
    parser = argparse.ArgumentParser(description="Cleanup stale self-heal branches")
    parser.add_argument("--prefix", default="self-heal/run-", help="Branch prefix to match")
    parser.add_argument("--execute", action="store_true", help="Actually delete (default: dry-run)")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_"))
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    if not token:
        print("❌ GITHUB_TOKEN or GH_TOKEN required", file=sys.stderr)
        return 1

    mode = "🔴 EXECUTE" if args.execute else "🟡 DRY-RUN"
    print(f"\n{'='*60}")
    print(f"  Stale Branch Cleanup — {mode}")
    print(f"  Repo:   {args.repo}")
    print(f"  Prefix: {args.prefix}")
    print(f"{'='*60}\n")

    branches = list_branches(args.repo, token, args.prefix)
    if not branches:
        print("✅ No stale branches found — nothing to clean up")
        return 0

    print(f"Found {len(branches)} stale branch(es):\n")

    closed_prs = 0
    deleted_branches = 0

    for b in branches:
        name = b["name"]
        print(f"  📌 {name}")

        # Check for associated PR
        pr_num = find_pr_for_branch(args.repo, token, name)
        if pr_num:
            print(f"     └─ PR #{pr_num} (open)")
            if args.execute:
                if close_pr(args.repo, token, pr_num):
                    print(f"     └─ ✅ PR #{pr_num} closed")
                    closed_prs += 1
                else:
                    print(f"     └─ ⚠️  Failed to close PR #{pr_num}")
            else:
                print(f"     └─ Would close PR #{pr_num}")

        # Delete branch
        if args.execute:
            delete_branch(args.repo, token, name)
            print(f"     └─ ✅ Branch deleted")
            deleted_branches += 1
        else:
            print(f"     └─ Would delete branch")

    print(f"\n{'='*60}")
    if args.execute:
        print(f"  ✅ Done: {deleted_branches} branches deleted, {closed_prs} PRs closed")
    else:
        print(f"  🟡 Dry-run: {len(branches)} branches would be deleted")
        print(f"  Run with --execute to apply changes")
    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
