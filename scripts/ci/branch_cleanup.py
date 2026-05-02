#!/usr/bin/env python3
"""branch_cleanup.py — Comprehensive repository branch hygiene.

Strategies
----------
merged     Delete branches whose HEAD commit is already reachable from the
           default branch (fully merged).  Safe: no code is lost.

stale      Delete branches with no commit activity in the last STALE_DAYS days
           (default 30).  Prints a warning per branch; requires --execute.

prefixes   Delete branches whose name matches a configurable prefix list.
           Default prefixes: copilot/, self-heal/run-, fix/, dependabot/
           (only when --delete-by-prefix is passed AND the branch is merged or
           the --force-prefix flag is also set).

Protected branches are NEVER deleted regardless of strategy:
    main  master  develop  0D_base_  release/*  hotfix/*  v[0-9]*

Usage
-----
    # Dry-run report (default)
    python scripts/ci/branch_cleanup.py

    # Execute merged-branch cleanup
    python scripts/ci/branch_cleanup.py --delete-merged --execute

    # Execute stale cleanup (>30 days) + merged
    python scripts/ci/branch_cleanup.py --delete-merged --delete-stale --execute

    # Target only specific prefixes (also merged check applies)
    python scripts/ci/branch_cleanup.py --delete-by-prefix --prefixes "copilot/,self-heal/run-" --execute

    # Full report as JSON
    python scripts/ci/branch_cleanup.py --json-output /tmp/branch_report.json

Environment
-----------
    GITHUB_TOKEN / GH_TOKEN     PAT with contents:write + pull-requests:write
    GITHUB_REPOSITORY           owner/repo  (default: Aries-Serpent/_codex_)

Exit codes
----------
    0   Clean / dry-run completed with no errors
    1   One or more deletions failed (execute mode)
    2   Missing authentication token
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_REPO = "Aries-Serpent/_codex_"
DEFAULT_PREFIXES = [
    "copilot/",
    "self-heal/run-",
    "fix/",
    "dependabot/",
    "chore/",
    "ci/",
]
PROTECTED_PATTERNS = [
    "main",
    "master",
    "develop",
    "0D_base_",
]
PROTECTED_PREFIX_PATTERNS = [
    "release/",
    "hotfix/",
    "v",
]
DEFAULT_STALE_DAYS = 30
DEFAULT_VERY_STALE_DAYS = 90


# ---------------------------------------------------------------------------
# GitHub API helper
# ---------------------------------------------------------------------------


def gh_api(
    method: str,
    path: str,
    token: str,
    data: bytes | None = None,
) -> Any:
    """Minimal GitHub REST API helper — zero external dependencies."""
    url = f"https://api.github.com{path}" if path.startswith("/") else path
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "codex-branch-cleanup/1.0",
        },
        data=data,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        if exc.code == 204:
            return None  # DELETE success
        body_text = exc.read().decode(errors="replace")
        print(
            f"  ⚠️  GitHub API {method} {path} → HTTP {exc.code}: {body_text[:200]}",
            file=sys.stderr,
        )
        return None


def gh_api_paginated(path: str, token: str) -> list[dict]:
    """Fetch all pages from a GitHub list endpoint."""
    results: list[dict] = []
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        data = gh_api("GET", f"{path}{sep}per_page=100&page={page}", token)
        if not data or not isinstance(data, list):
            break
        results.extend(data)
        if len(data) < 100:
            break
        page += 1
    return results


# ---------------------------------------------------------------------------
# Branch introspection helpers
# ---------------------------------------------------------------------------


def get_default_branch(repo: str, token: str) -> str:
    """Return the repository's default branch name."""
    data = gh_api("GET", f"/repos/{repo}", token)
    if data and isinstance(data, dict):
        return data.get("default_branch", "main")
    return "main"


def list_all_branches(repo: str, token: str) -> list[dict]:
    """Return all branches with their SHA and protection status."""
    return gh_api_paginated(f"/repos/{repo}/branches", token)


def get_branch_last_commit_date(repo: str, token: str, branch: str) -> datetime | None:
    """Return the UTC datetime of the last commit on a branch."""
    data = gh_api("GET", f"/repos/{repo}/branches/{urllib.parse.quote(branch, safe='')}", token)
    if data and isinstance(data, dict):
        commit = data.get("commit", {})
        commit_data = commit.get("commit", {})
        author = commit_data.get("author", {})
        date_str = author.get("date", "")
        if date_str:
            try:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                pass
    return None


def is_branch_merged(repo: str, token: str, branch: str, base: str) -> bool:
    """Return True if *branch* has been merged into *base*."""
    # GitHub's compare API returns "behind" when all commits in head are already in base.
    data = gh_api(
        "GET",
        f"/repos/{repo}/compare/{urllib.parse.quote(base, safe='')}...{urllib.parse.quote(branch, safe='')}",
        token,
    )
    if data and isinstance(data, dict):
        status = data.get("status", "")
        ahead_by = data.get("ahead_by", 1)
        return status == "behind" or (status == "identical") or (ahead_by == 0)
    return False


def find_open_pr(repo: str, token: str, branch: str) -> int | None:
    """Return the open PR number for *branch*, if any."""
    owner = repo.split("/")[0]
    data = gh_api(
        "GET",
        f"/repos/{repo}/pulls?state=open&head={owner}:{urllib.parse.quote(branch, safe='')}&per_page=1",
        token,
    )
    if data and isinstance(data, list) and len(data) > 0:
        return data[0]["number"]
    return None


def close_pr(repo: str, token: str, pr_number: int) -> bool:
    """Close an open PR."""
    result = gh_api(
        "PATCH",
        f"/repos/{repo}/pulls/{pr_number}",
        token,
        json.dumps({"state": "closed"}).encode(),
    )
    return result is not None


def delete_branch(repo: str, token: str, branch: str) -> bool:
    """Delete a branch. Returns True on success (HTTP 204 No Content)."""
    encoded = urllib.parse.quote(branch, safe='')
    url = f"https://api.github.com/repos/{repo}/git/refs/heads/{encoded}"
    req = urllib.request.Request(
        url,
        method="DELETE",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "codex-branch-cleanup/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req):
            return True  # any 2xx response (including 204 No Content) is success
    except urllib.error.HTTPError as exc:
        print(
            f"  ⚠️  Failed to delete branch {branch!r}: HTTP {exc.code}",
            file=sys.stderr,
        )
        return False


# ---------------------------------------------------------------------------
# Protection check
# ---------------------------------------------------------------------------


def is_protected(branch_name: str) -> bool:
    """Return True if *branch_name* must never be deleted."""
    if branch_name in PROTECTED_PATTERNS:
        return True
    return any(branch_name.startswith(prefix) for prefix in PROTECTED_PREFIX_PATTERNS)


# ---------------------------------------------------------------------------
# Core cleanup logic
# ---------------------------------------------------------------------------


def classify_branches(
    repo: str,
    token: str,
    default_branch: str,
    branches: list[dict],
    stale_days: int,
    very_stale_days: int,
    target_prefixes: list[str],
    delete_merged: bool,
    delete_stale: bool,
    delete_by_prefix: bool,
    force_prefix: bool,
) -> dict[str, list[dict]]:
    """Classify branches into: protected, to_delete, stale_warn, clean."""
    now = datetime.now(tz=timezone.utc)
    result: dict[str, list[dict]] = {
        "protected": [],
        "to_delete": [],
        "stale_warn": [],
        "clean": [],
    }

    for b in branches:
        name: str = b["name"]
        # Skip the default branch unconditionally
        if name == default_branch:
            result["protected"].append({"name": name, "reason": "default branch"})
            continue
        if is_protected(name):
            result["protected"].append({"name": name, "reason": "protected pattern"})
            continue

        # Gather metadata
        last_commit_dt = get_branch_last_commit_date(repo, token, name)
        days_since = (
            (now - last_commit_dt).days if last_commit_dt else None
        )
        merged = is_branch_merged(repo, token, name, default_branch)
        has_prefix = any(name.startswith(p) for p in target_prefixes)

        branch_info = {
            "name": name,
            "merged": merged,
            "days_since_commit": days_since,
            "has_target_prefix": has_prefix,
            "pr_number": None,
        }

        should_delete = False
        reason = ""

        if delete_merged and merged:
            should_delete = True
            reason = "fully merged into default branch"
        elif delete_stale and days_since is not None and days_since >= stale_days and merged:
            should_delete = True
            reason = f"stale ({days_since}d since last commit) and merged"
        elif delete_stale and days_since is not None and days_since >= very_stale_days and not merged:
            # Very stale unmerged branches are force-deleted regardless of merge status
            should_delete = True
            reason = f"very stale ({days_since}d >= {very_stale_days}d threshold) — force-deleting unmerged branch"
        elif delete_by_prefix and has_prefix and (merged or force_prefix):
            should_delete = True
            reason = f"matches target prefix; {'merged' if merged else 'force-prefix set'}"

        if should_delete:
            branch_info["reason"] = reason
            # Find associated PR
            pr = find_open_pr(repo, token, name)
            branch_info["pr_number"] = pr
            result["to_delete"].append(branch_info)
        elif delete_stale and days_since is not None and days_since >= stale_days and not merged:
            branch_info["reason"] = f"stale ({days_since}d) but NOT merged — warning only"
            result["stale_warn"].append(branch_info)
        else:
            result["clean"].append(branch_info)

    return result


def execute_cleanup(
    repo: str,
    token: str,
    to_delete: list[dict],
    dry_run: bool,
) -> tuple[int, int]:
    """Delete branches (and close PRs). Returns (deleted, errors)."""
    deleted = 0
    errors = 0
    for b in to_delete:
        name = b["name"]
        pr_num = b.get("pr_number")
        prefix = "  [DRY-RUN]" if dry_run else " "

        if pr_num:
            if dry_run:
                print(f"{prefix} Would close PR #{pr_num} for branch '{name}'")
            else:
                if close_pr(repo, token, pr_num):
                    print(f"  ✅ Closed PR #{pr_num} for '{name}'")
                else:
                    print(f"  ⚠️  Failed to close PR #{pr_num} for '{name}'", file=sys.stderr)
                    errors += 1

        if dry_run:
            print(f"{prefix} Would delete '{name}'  ← {b.get('reason', '')}")
        else:
            if delete_branch(repo, token, name):
                print(f"  ✅ Deleted '{name}'  ← {b.get('reason', '')}")
                deleted += 1
            else:
                print(f"  ❌ Failed to delete '{name}'", file=sys.stderr)
                errors += 1

    return deleted, errors


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def print_report(classification: dict[str, list[dict]], default_branch: str) -> None:
    """Print a human-readable summary to stdout."""
    to_delete = classification["to_delete"]
    stale_warn = classification["stale_warn"]
    protected = classification["protected"]
    clean = classification["clean"]

    total = sum(len(v) for v in classification.values())

    print(f"\n{'═'*70}")
    print(f"  Branch Cleanup Report   (default: {default_branch})")
    print(f"  Total branches surveyed: {total}")
    print(f"{'═'*70}\n")

    if to_delete:
        print(f"🗑️  TO DELETE ({len(to_delete)}):")
        for b in to_delete:
            pr_tag = f" [PR #{b['pr_number']}]" if b.get("pr_number") else ""
            print(f"    {b['name']}{pr_tag}  ← {b.get('reason', '')}")
        print()

    if stale_warn:
        print(f"⚠️  STALE BUT NOT MERGED — warning only ({len(stale_warn)}):")
        for b in stale_warn:
            print(f"    {b['name']}  ← {b.get('reason', '')} (manual review needed)")
        print()

    if protected:
        print(f"🔒  PROTECTED — never deleted ({len(protected)}):")
        for b in protected:
            print(f"    {b['name']}  ← {b.get('reason', '')}")
        print()

    print(f"✅  CLEAN ({len(clean)} branch(es) — no action needed)\n")


def write_json_report(
    classification: dict[str, list[dict]],
    default_branch: str,
    path: str,
    deleted: int,
    errors: int,
    dry_run: bool,
) -> None:
    output = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "default_branch": default_branch,
        "dry_run": dry_run,
        "summary": {
            "total_branches": sum(len(v) for v in classification.values()),
            "to_delete": len(classification["to_delete"]),
            "stale_warn": len(classification["stale_warn"]),
            "protected": len(classification["protected"]),
            "clean": len(classification["clean"]),
            "deleted": deleted,
            "errors": errors,
        },
        "branches": classification,
    }
    with open(path, "w") as fh:
        json.dump(output, fh, indent=2)
    print(f"\n📄 JSON report written to: {path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

# Lazy import — only needed for URL-encoding branch names with slashes
import urllib.parse  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Comprehensive repository branch cleanup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPO))
    parser.add_argument("--delete-merged", action="store_true", help="Delete fully-merged branches")
    parser.add_argument("--delete-stale", action="store_true", help="Delete stale merged branches")
    parser.add_argument(
        "--stale-days",
        type=int,
        default=int(os.environ.get("CODEX_STALE_BRANCH_DAYS", DEFAULT_STALE_DAYS)),
        help="Days of inactivity before a branch is considered stale "
        "(default: %(default)s; override with CODEX_STALE_BRANCH_DAYS env var)",
    )
    parser.add_argument(
        "--very-stale-days",
        type=int,
        default=int(os.environ.get("CODEX_VERY_STALE_BRANCH_DAYS", DEFAULT_VERY_STALE_DAYS)),
        help="Days of inactivity before an unmerged branch is force-deleted "
        "(default: %(default)s; override with CODEX_VERY_STALE_BRANCH_DAYS env var)",
    )
    parser.add_argument("--delete-by-prefix", action="store_true", help="Delete merged branches matching prefixes")
    parser.add_argument("--force-prefix", action="store_true", help="Delete prefix branches even if not merged (DANGER)")
    parser.add_argument(
        "--prefixes",
        default=",".join(DEFAULT_PREFIXES),
        help="Comma-separated list of branch name prefixes",
    )
    parser.add_argument("--execute", action="store_true", help="Actually delete (default: dry-run)")
    parser.add_argument("--json-output", metavar="PATH", help="Write JSON report to file")
    parser.add_argument("--github-summary", action="store_true", help="Write Markdown to GITHUB_STEP_SUMMARY")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    if not token:
        print("❌  GITHUB_TOKEN or GH_TOKEN required", file=sys.stderr)
        return 2

    target_prefixes = [p.strip() for p in args.prefixes.split(",") if p.strip()]
    dry_run = not args.execute

    print(f"\n🔍 Fetching branches for {args.repo}…")
    default_branch = get_default_branch(args.repo, token)
    branches = list_all_branches(args.repo, token)
    print(f"   Found {len(branches)} branches. Default: '{default_branch}'")

    print("🧮 Classifying branches…")
    classification = classify_branches(
        repo=args.repo,
        token=token,
        default_branch=default_branch,
        branches=branches,
        stale_days=args.stale_days,
        very_stale_days=args.very_stale_days,
        target_prefixes=target_prefixes,
        delete_merged=args.delete_merged,
        delete_stale=args.delete_stale,
        delete_by_prefix=args.delete_by_prefix,
        force_prefix=args.force_prefix,
    )

    print_report(classification, default_branch)

    deleted = 0
    errors = 0
    if classification["to_delete"]:
        mode_label = "🔴 EXECUTE" if args.execute else "🟡 DRY-RUN"
        print(f"{'─'*70}")
        print(f"  Running cleanup — {mode_label}")
        print(f"{'─'*70}")
        deleted, errors = execute_cleanup(args.repo, token, classification["to_delete"], dry_run)

    if args.json_output:
        write_json_report(classification, default_branch, args.json_output, deleted, errors, dry_run)

    if args.github_summary:
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "")
        if summary_path:
            to_del = classification["to_delete"]
            stale = classification["stale_warn"]
            with open(summary_path, "a") as fh:
                fh.write("\n### 🌿 Branch Cleanup Report\n\n")
                fh.write("| Metric | Count |\n|---|---|\n")
                fh.write(f"| Total branches | {sum(len(v) for v in classification.values())} |\n")
                fh.write(f"| To delete | {len(to_del)} |\n")
                fh.write(f"| Stale (not merged) | {len(stale)} |\n")
                fh.write(f"| Protected | {len(classification['protected'])} |\n")
                fh.write(f"| Clean | {len(classification['clean'])} |\n")
                if dry_run:
                    fh.write("\n> 🟡 **Dry-run mode** — no branches were deleted.\n")
                else:
                    fh.write(f"\n> ✅ Deleted: **{deleted}** | ❌ Errors: **{errors}**\n")

    print(f"\n{'═'*70}")
    if dry_run:
        print(f"  🟡 DRY-RUN complete — {len(classification['to_delete'])} branch(es) would be deleted")
        print("  Run with --execute to apply.")
    else:
        print(f"  ✅ Done — {deleted} deleted, {errors} errors")
    print(f"{'═'*70}\n")

    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
