#!/usr/bin/env python3
"""dependabot_consolidator.py — Hardened Dependabot PR consolidation.

Lists open Dependabot PRs, merges all eligible branches into a single
cross-ecosystem consolidation branch, opens/updates a consolidated PR, and
closes the individual Dependabot PRs with a pointer comment.

Usage
-----
    # Normal run
    python scripts/ci/dependabot_consolidator.py --base-branch main

    # Dry-run (no push, no PR create/update, no close)
    python scripts/ci/dependabot_consolidator.py --base-branch main --dry-run

Environment
-----------
    GH_TOKEN / GITHUB_TOKEN     PAT with contents:write + pull-requests:write
    GITHUB_REPOSITORY           owner/repo  (default: Aries-Serpent/_codex_)

Exit codes
----------
    0   Success / nothing to do / dry-run complete
    1   Runtime error (auth, merge conflict handling failure, API error)
    2   Invalid arguments or environment
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

DEFAULT_REPO = "Aries-Serpent/_codex_"
CONSOLIDATED_LABEL = "dependabot-consolidated"
SKIP_LABELS = {"security"}
UNCLEAN_STATES = {"DIRTY", "BLOCKED", "UNKNOWN"}
BOT_AUTHORS = {"dependabot[bot]", "dependabot"}


# ---------------------------------------------------------------------------
# CLI / argument parsing
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Consolidate open Dependabot PRs into a single PR.",
    )
    parser.add_argument(
        "--base-branch",
        default="main",
        help="Base branch to create the consolidation PR against (default: main).",
    )
    parser.add_argument(
        "--dry-run",
        choices=("true", "false"),
        default="false",
        help="Log actions without pushing branches or modifying PRs.",
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPO),
        help="Owner/repo slug (default: GITHUB_REPOSITORY or Aries-Serpent/_codex_).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Console log level.",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Token / auth helpers
# ---------------------------------------------------------------------------


def resolve_token() -> str:
    """Return the first non-empty GitHub token from the standard chain."""
    for envvar in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GH_TOKEN", "GITHUB_TOKEN"):
        tok = os.environ.get(envvar, "").strip()
        if tok:
            log.info("Using token from %s", envvar)
            return tok
    log.error("No GitHub token found. Set GH_TOKEN or GITHUB_TOKEN.")
    raise SystemExit(2)


def verify_gh_auth(token: str) -> None:
    """Verify that the GitHub CLI can authenticate with the provided token."""
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
        env={**os.environ, "GH_TOKEN": token},
    )
    if result.returncode != 0:
        log.error("gh auth status failed:\n%s", result.stderr)
        raise SystemExit(1)
    log.info("gh auth status OK")


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------


def _api_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "codex-dependabot-consolidator/1.0",
    }


def gh_api(
    method: str,
    path: str,
    token: str,
    data: bytes | None = None,
) -> Any:
    """Minimal GitHub REST API helper."""
    url = f"https://api.github.com{path}" if path.startswith("/") else path
    req = urllib.request.Request(
        url,
        method=method,
        headers=_api_headers(token),
        data=data,
    )
    log.debug("GitHub API %s %s", method, path)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        if exc.code == 204:
            return None
        body_text = exc.read().decode(errors="replace")
        log.error("GitHub API %s %s → HTTP %d: %s", method, path, exc.code, body_text[:500])
        raise


def gh_api_paginated(path: str, token: str) -> list[dict[str, Any]]:
    """Fetch all pages from a GitHub list endpoint."""
    results: list[dict[str, Any]] = []
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        data = gh_api("GET", f"{path}{sep}per_page=100&page={page}", token)
        if not isinstance(data, list):
            break
        results.extend(data)
        if len(data) < 100:
            break
        page += 1
    return results


# ---------------------------------------------------------------------------
# PR discovery
# ---------------------------------------------------------------------------


def list_dependabot_prs(repo: str, token: str) -> list[dict[str, Any]]:
    """List open PRs authored by Dependabot or labelled as dependencies/dependabot."""
    owner, name = repo.split("/", 1)
    pulls = gh_api_paginated(f"/repos/{repo}/pulls?state=open&per_page=100", token)
    dependabot_prs: list[dict[str, Any]] = []
    for pr in pulls:
        user = pr.get("user", {}) or {}
        login = user.get("login", "")
        labels = {label.get("name", "") for label in (pr.get("labels", []) or [])}
        is_author = login in BOT_AUTHORS
        is_labelled = "dependencies" in labels or "dependabot" in labels
        if is_author or is_labelled:
            dependabot_prs.append(pr)
    log.info("Found %d open Dependabot PR(s) in %s", len(dependabot_prs), repo)
    return dependabot_prs


def find_existing_consolidation_pr(repo: str, token: str) -> dict[str, Any] | None:
    """Return an existing open consolidation PR labelled dependabot-consolidated."""
    encoded = urllib.parse.quote(f"label:{CONSOLIDATED_LABEL}", safe="")
    pulls = gh_api_paginated(
        f"/repos/{repo}/issues?state=open&labels={encoded}&per_page=10",
        token,
    )
    for issue in pulls:
        if "pull_request" in (issue or {}):
            return issue
    return None


# ---------------------------------------------------------------------------
# Eligibility / merge state
# ---------------------------------------------------------------------------


def pr_eligibility(pr: dict[str, Any]) -> tuple[bool, str]:
    """Return (eligible, reason) for a Dependabot PR."""
    labels = {label.get("name", "") for label in (pr.get("labels", []) or [])}
    if labels & SKIP_LABELS:
        return False, "security label"
    state = pr.get("merge_state_status", "UNKNOWN")
    if state in UNCLEAN_STATES:
        return False, f"merge state {state}"
    return True, ""


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _run_git(
    args: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the CompletedProcess."""
    cmd_env = {**os.environ, **(env or {})}
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
        env=cmd_env,
    )


def create_consolidation_branch(
    workdir: Path,
    base_branch: str,
    run_id: str,
    dry_run: bool,
) -> str:
    """Create and check out a new consolidation branch from the base branch."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    short_run = re.sub(r"[^a-zA-Z0-9]", "", run_id)[:7]
    branch = f"dependabot/consolidated-{today}-{short_run}"

    _run_git(["fetch", "origin", base_branch], workdir)
    _run_git(["checkout", "-B", branch, f"origin/{base_branch}"], workdir)
    log.info("Created consolidation branch %s from %s", branch, base_branch)
    return branch


def merge_dependabot_branch(
    workdir: Path,
    branch: str,
    pr_number: int,
    title: str,
    dry_run: bool,
) -> tuple[bool, str]:
    """Merge a Dependabot branch into the consolidation branch."""
    _run_git(["fetch", "origin", branch], workdir, check=False)
    if dry_run:
        log.info("[dry-run] Would merge PR #%d (%s) from %s", pr_number, title, branch)
        return True, ""

    result = _run_git(
        ["merge", "--no-ff", "--no-commit", f"origin/{branch}"],
        workdir,
        check=False,
    )
    if result.returncode == 0:
        _run_git(["commit", "-m", f"chore(deps): consolidate PR #{pr_number} - {title}"], workdir)
        log.info("Merged PR #%d (%s)", pr_number, title)
        return True, ""

    log.warning("Merge conflict for PR #%d (%s): %s", pr_number, title, result.stderr)
    _run_git(["merge", "--abort"], workdir, check=False)
    return False, "merge conflict"


def push_branch(workdir: Path, branch: str, dry_run: bool) -> None:
    """Push the consolidation branch to origin."""
    if dry_run:
        log.info("[dry-run] Would push branch %s", branch)
        return
    _run_git(["push", "origin", branch], workdir)
    log.info("Pushed branch %s", branch)


# ---------------------------------------------------------------------------
# PR create / update / close helpers
# ---------------------------------------------------------------------------


def build_pr_body(
    included: list[tuple[int, str, str]],
    excluded: list[tuple[int, str, str]],
) -> str:
    """Build the consolidated PR body with included/excluded tables."""
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = f"""chore(deps): consolidated dependency updates for {date}

This PR combines all eligible open Dependabot PRs into a single
cross-ecosystem update to reduce review sprawl and CI contention.

Configuration reference: [.github/dependabot.yml](/.github/dependabot.yml)

### Included PRs

| PR | Title | Reason |
|---|---|---|
"""
    for pr_number, title, reason in included:
        body += f"| #{pr_number} | {title} | {reason} |\n"
    if not included:
        body += "| — | — | No eligible PRs |\n"

    body += "\n### Excluded PRs\n\n| PR | Title | Reason |\n|---|---|---|\n"
    for pr_number, title, reason in excluded:
        body += f"| #{pr_number} | {title} | {reason} |\n"
    if not excluded:
        body += "| — | — | None |\n"

    body += """
### Notes
- The consolidator workflow will close the individual Dependabot PRs once
  CI passes on this consolidated PR.
- Security-labelled or conflicting PRs are intentionally excluded and must
  be handled manually.
"""
    return body


def create_or_update_consolidation_pr(
    repo: str,
    token: str,
    branch: str,
    base_branch: str,
    included: list[tuple[int, str, str]],
    excluded: list[tuple[int, str, str]],
    existing: dict[str, Any] | None,
    dry_run: bool,
) -> int | None:
    """Create a new consolidation PR or update the body of an existing one."""
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    title = f"chore(deps): consolidated dependency updates for {date}"
    body = build_pr_body(included, excluded)

    if dry_run:
        log.info("[dry-run] Would create/update PR '%s' on branch %s", title, branch)
        return None

    if existing:
        pr_number = existing["number"]
        gh_api(
            "PATCH",
            f"/repos/{repo}/pulls/{pr_number}",
            token,
            json.dumps({"body": body, "state": "open"}).encode(),
        )
        log.info("Updated existing consolidation PR #%d", pr_number)
        return pr_number

    payload = {
        "title": title,
        "head": branch,
        "base": base_branch,
        "body": body,
        "labels": [CONSOLIDATED_LABEL, "dependencies"],
    }
    result = gh_api("POST", f"/repos/{repo}/pulls", token, json.dumps(payload).encode())
    pr_number = result.get("number")
    log.info("Created consolidation PR #%d", pr_number)
    return pr_number


def close_original_pr(
    repo: str,
    token: str,
    pr_number: int,
    consolidated_number: int,
    dry_run: bool,
) -> None:
    """Close a Dependabot PR with a comment pointing to the consolidated PR."""
    comment = f"Consolidated into #{consolidated_number}."
    if dry_run:
        log.info("[dry-run] Would close PR #%d with comment: %s", pr_number, comment)
        return
    gh_api(
        "POST",
        f"/repos/{repo}/issues/{pr_number}/comments",
        token,
        json.dumps({"body": comment}).encode(),
    )
    gh_api(
        "PATCH",
        f"/repos/{repo}/pulls/{pr_number}",
        token,
        json.dumps({"state": "closed"}).encode(),
    )
    log.info("Closed original PR #%d", pr_number)


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    args = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    dry_run = args.dry_run == "true"
    if dry_run:
        log.info("Running in DRY-RUN mode")

    token = resolve_token()
    verify_gh_auth(token)

    repo = args.repo
    base_branch = args.base_branch
    run_id = os.environ.get("GITHUB_RUN_ID", datetime.now(timezone.utc).strftime("%H%M%S"))

    dependabot_prs = list_dependabot_prs(repo, token)
    if len(dependabot_prs) <= 1:
        log.info("Zero or one Dependabot PR — nothing to consolidate.")
        return 0

    existing = find_existing_consolidation_pr(repo, token)
    if existing:
        log.info("Existing consolidation PR found: #%d", existing.get("number"))

    included: list[tuple[int, str, str]] = []
    excluded: list[tuple[int, str, str]] = []

    with tempfile.TemporaryDirectory(prefix="dependabot-consolidator-") as tmp:
        workdir = Path(tmp)
        clone_url = f"https://x-access-token:{token}@github.com/{repo}.git"
        _run_git(["clone", "--depth", "1", clone_url, "."], workdir)
        _run_git(["fetch", "origin", base_branch, "--depth=1"], workdir)

        branch = create_consolidation_branch(workdir, base_branch, run_id, dry_run)

        for pr in dependabot_prs:
            pr_number = pr.get("number", 0)
            title = pr.get("title", "")
            head_ref = pr.get("head", {}).get("ref", "")
            if not head_ref:
                excluded.append((pr_number, title, "missing head ref"))
                continue

            eligible, reason = pr_eligibility(pr)
            if not eligible:
                excluded.append((pr_number, title, reason))
                log.info("Excluding PR #%d (%s): %s", pr_number, title, reason)
                continue

            success, merge_reason = merge_dependabot_branch(
                workdir, head_ref, pr_number, title, dry_run
            )
            if success:
                included.append((pr_number, title, "merged cleanly"))
            else:
                excluded.append((pr_number, title, merge_reason))

        if not included:
            log.warning("No Dependabot PRs could be merged cleanly; nothing to push.")
            return 0

        push_branch(workdir, branch, dry_run)

    consolidated_number = create_or_update_consolidation_pr(
        repo,
        token,
        branch,
        base_branch,
        included,
        excluded,
        existing,
        dry_run,
    )

    if consolidated_number is not None:
        for pr_number, _, _ in included:
            close_original_pr(repo, token, pr_number, consolidated_number, dry_run)

    log.info("Consolidation complete. Included=%d, Excluded=%d", len(included), len(excluded))
    return 0


if __name__ == "__main__":
    sys.exit(main())
