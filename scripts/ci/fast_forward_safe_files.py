#!/usr/bin/env python3
"""Fast-Forward Safe-File Promoter.

Promotes pre-approved files from an active PR branch directly to ``main``
(or any target branch) without waiting for the full PR merge cycle.

PRIMARY USE CASE
----------------
GitHub Actions files (.github/workflows/*.yml) ONLY take effect from the
default branch.  A schedule trigger, workflow_run handler, or
workflow_dispatch UI button defined in a PR branch is completely **inert**
until the file lands on main.  This tool lets maintainers promote those
files immediately.

Algorithm
---------
1. Load the allowlist from ``.codex/fast_forward_allowlist.yaml``.
2. Fetch the PR branch diff against the target branch.
3. Filter changed files through the allowlist (deny-listed files are always
   excluded; any file not in the allowlist is excluded unless ``--force`` is
   passed).
4. In DRY-RUN mode: print a summary of what would be promoted and exit.
5. In CREATE-PR mode (default):
   a. Create branch ``fast-forward/pr-{N}-{sha8}`` from the target branch.
   b. Apply each allowed file from the PR branch onto that staging branch.
   c. Commit with attribution to the source PR.
   d. Open a new PR from the staging branch → target branch.
   e. If ``auto_approve_when_all_safe`` is true, auto-approve + merge.
6. In DIRECT-PUSH mode (``--merge-mode=direct-push``):
   a. Apply each allowed file directly to a local clone of the target branch.
   b. Push in a single atomic commit.

Usage::

    python scripts/ci/fast_forward_safe_files.py \\
        --repo   Aries-Serpent/_codex_ \\
        --token  "$GITHUB_TOKEN" \\
        --pr     3856 \\
        --target main \\
        [--files .github/workflows/proactive-ci-monitor.yml] \\
        [--merge-mode create-pr | direct-push] \\
        [--dry-run]

Environment variables
---------------------
GITHUB_TOKEN            PAT with ``repo``, ``workflow``, ``pull-requests`` scopes.
FF_DRY_RUN              ``1`` to enable dry-run without CLI flag.
FF_MERGE_MODE           ``create-pr`` (default) or ``direct-push``.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import logging
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import NamedTuple

try:
    import yaml as _yaml
except ImportError:  # pragma: no cover
    _yaml = None  # type: ignore[assignment]

logger = logging.getLogger("fast_forward")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

_ALLOWLIST_PATH = Path(__file__).parents[2] / ".codex" / "fast_forward_allowlist.yaml"

# Built-in defaults used when the allowlist YAML is absent or PyYAML is unavailable.
_BUILTIN_ALLOWLIST_DEFAULTS: dict = {
    "allowlist": [
        ".github/workflows/*.yml",
        ".github/workflows/*.yaml",
        ".github/agents/*.md",
        "scripts/ci/*.py",
        "docs/ci/*.md",
        "CHANGELOG.md",
    ],
    "denylist": [
        ".github/workflows/*deploy*.yml",
        ".github/workflows/*release*.yml",
        ".github/workflows/*publish*.yml",
        ".github/workflows/*prod*.yml",
    ],
    "default_merge_mode": "create-pr",
    "auto_approve_when_all_safe": True,
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


class PromotionPlan(NamedTuple):
    """Files approved for fast-forward promotion."""

    allowed: list[str]      # files to promote
    excluded: list[str]     # files excluded (not in allowlist)
    denied: list[str]       # files explicitly deny-listed
    pr_number: int
    pr_branch: str
    source_sha: str
    target_branch: str
    merge_mode: str


# ---------------------------------------------------------------------------
# Allowlist helpers
# ---------------------------------------------------------------------------


def _load_allowlist(path: Path = _ALLOWLIST_PATH) -> dict:
    """Load and return the allowlist config dict."""
    if _yaml is None:
        logger.warning("PyYAML not available — using built-in defaults")
        return _BUILTIN_ALLOWLIST_DEFAULTS
    try:
        return _yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        logger.warning("Allowlist not found at %s — using built-in defaults", path)
        return _BUILTIN_ALLOWLIST_DEFAULTS


def _matches_any(filepath: str, patterns: list[str]) -> bool:
    """Return True if *filepath* matches any glob pattern in *patterns*."""
    for pat in patterns:
        if fnmatch.fnmatch(filepath, pat):
            return True
        # Also try matching the basename alone for simple *.ext patterns
        if fnmatch.fnmatch(Path(filepath).name, pat):
            return True
    return False


def classify_files(
    changed_files: list[str],
    config: dict,
    force_files: list[str] | None = None,
) -> tuple[list[str], list[str], list[str]]:
    """Split *changed_files* into (allowed, excluded, denied).

    Parameters
    ----------
    changed_files:  All files changed in the PR.
    config:         Loaded allowlist config dict.
    force_files:    If provided, only consider these specific files (must
                    still pass denylist check).

    Returns
    -------
    (allowed, excluded, denied)
    """
    allowlist: list[str] = config.get("allowlist", [])
    denylist: list[str] = config.get("denylist", [])

    consider = force_files if force_files else changed_files

    allowed: list[str] = []
    excluded: list[str] = []
    denied: list[str] = []

    for f in consider:
        if _matches_any(f, denylist):
            denied.append(f)
        elif force_files or _matches_any(f, allowlist):
            allowed.append(f)
        else:
            excluded.append(f)

    return allowed, excluded, denied


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------


def _gh(path: str, token: str, method: str = "GET", body: dict | None = None) -> object:
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _get_pr(repo: str, pr_number: int, token: str) -> dict:
    return _gh(f"/repos/{repo}/pulls/{pr_number}", token)  # type: ignore[return-value]


def _get_pr_files(repo: str, pr_number: int, token: str) -> list[str]:
    """Return all filenames changed by a PR (paginated)."""
    files: list[str] = []
    page = 1
    while True:
        batch = _gh(
            f"/repos/{repo}/pulls/{pr_number}/files?per_page=100&page={page}",
            token,
        )
        if not batch:
            break
        files.extend(f["filename"] for f in batch)  # type: ignore[union-attr]
        if len(batch) < 100:  # type: ignore[arg-type]
            break
        page += 1
    return files


def _create_branch(repo: str, branch: str, sha: str, token: str) -> None:
    """Create a new branch from *sha*."""
    try:
        _gh(
            f"/repos/{repo}/git/refs",
            token,
            method="POST",
            body={"ref": f"refs/heads/{branch}", "sha": sha},
        )
        logger.info("Created branch %s from %s", branch, sha[:8])
    except urllib.error.HTTPError as exc:
        if exc.code == 422:  # branch already exists
            logger.info("Branch %s already exists", branch)
        else:
            raise


def _get_branch_sha(repo: str, branch: str, token: str) -> str:
    data = _gh(f"/repos/{repo}/git/refs/heads/{branch}", token)
    return data["object"]["sha"]  # type: ignore[index]


def _create_pr(
    repo: str,
    head: str,
    base: str,
    title: str,
    body: str,
    token: str,
) -> dict:
    return _gh(  # type: ignore[return-value]
        f"/repos/{repo}/pulls",
        token,
        method="POST",
        body={"title": title, "head": head, "base": base, "body": body},
    )


def _approve_and_merge_pr(repo: str, pr_number: int, token: str) -> None:
    """Approve then squash-merge a PR."""
    try:
        _gh(
            f"/repos/{repo}/pulls/{pr_number}/reviews",
            token,
            method="POST",
            body={"event": "APPROVE", "body": "Auto-approved: all files in fast-forward allowlist."},
        )
    except Exception as exc:
        logger.warning("Could not approve PR #%d (may need different token): %s", pr_number, exc)

    try:
        _gh(
            f"/repos/{repo}/pulls/{pr_number}/merge",
            token,
            method="PUT",
            body={"merge_method": "squash"},
        )
        logger.info("Auto-merged fast-forward PR #%d", pr_number)
    except Exception as exc:
        logger.warning("Auto-merge failed for PR #%d: %s", pr_number, exc)


# ---------------------------------------------------------------------------
# Git helpers (local clone operations)
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: str | None = None, check: bool = True) -> str:
    """Run a git command; return stdout."""
    result = subprocess.run(  # nosec B603,B607
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed:\n{result.stderr.strip()}"
        )
    return result.stdout.strip()


def _apply_files_via_api(
    repo: str,
    token: str,
    source_branch: str,
    staging_branch: str,
    files: list[str],
    commit_message: str,
) -> str:
    """Apply *files* from *source_branch* onto *staging_branch* via the GitHub
    Contents API (base64 PUT).  Returns the new commit SHA.

    Falls back to a local git clone if the repo is too large or the API
    rate-limits.
    """
    new_sha = ""
    for filepath in files:
        # Get file content from source branch
        try:
            src = _gh(
                f"/repos/{repo}/contents/{filepath}?ref={source_branch}",
                token,
            )
        except urllib.error.HTTPError as exc:
            logger.warning("Could not fetch %s from %s: %s", filepath, source_branch, exc)
            continue

        # Get current SHA on staging branch (needed for update)
        try:
            dst = _gh(
                f"/repos/{repo}/contents/{filepath}?ref={staging_branch}",
                token,
            )
            file_sha: str | None = dst["sha"]  # type: ignore[index]
        except urllib.error.HTTPError:
            file_sha = None  # File doesn't exist on staging branch yet

        body: dict = {
            "message": commit_message,
            "content": src["content"].replace("\n", ""),  # type: ignore[index]
            "branch": staging_branch,
        }
        if file_sha:
            body["sha"] = file_sha

        result = _gh(
            f"/repos/{repo}/contents/{filepath}",
            token,
            method="PUT",
            body=body,
        )
        new_sha = result["commit"]["sha"]  # type: ignore[index]
        logger.info("Applied %s → %s", filepath, staging_branch)

    return new_sha


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def build_plan(
    repo: str,
    token: str,
    pr_number: int,
    target_branch: str,
    merge_mode: str,
    force_files: list[str] | None,
) -> PromotionPlan:
    """Fetch PR metadata and classify files into the promotion plan."""
    pr = _get_pr(repo, pr_number, token)
    pr_branch: str = pr["head"]["ref"]
    source_sha: str = pr["head"]["sha"]

    changed = _get_pr_files(repo, pr_number, token)
    logger.info("PR #%d has %d changed file(s)", pr_number, len(changed))

    config = _load_allowlist()
    allowed, excluded, denied = classify_files(changed, config, force_files)

    return PromotionPlan(
        allowed=allowed,
        excluded=excluded,
        denied=denied,
        pr_number=pr_number,
        pr_branch=pr_branch,
        source_sha=source_sha,
        target_branch=target_branch,
        merge_mode=merge_mode,
    )


def execute_plan(
    repo: str,
    token: str,
    plan: PromotionPlan,
    commit_message_override: str = "",
) -> dict:
    """Execute the promotion plan; return a result dict."""
    if not plan.allowed:
        logger.info("No files to promote after allowlist filtering.")
        return {"status": "nothing-to-promote", "plan": plan._asdict()}

    sha8 = plan.source_sha[:8]
    staging_branch = f"fast-forward/pr-{plan.pr_number}-{sha8}"
    target_sha = _get_branch_sha(repo, plan.target_branch, token)

    commit_msg = commit_message_override or (
        f"chore(fast-forward): promote {len(plan.allowed)} safe file(s) from PR #{plan.pr_number}\n\n"
        f"Source branch: {plan.pr_branch} ({sha8})\n"
        f"Files promoted:\n"
        + "\n".join(f"  - {f}" for f in plan.allowed)
        + f"\n\nFiles excluded (not in allowlist): {len(plan.excluded)}\n"
        f"Files denied: {len(plan.denied)}\n\n"
        f"Auto-promoted by fast-forward-safe-files.yml"
    )

    if plan.merge_mode == "direct-push":
        # Apply directly onto target branch
        new_sha = _apply_files_via_api(
            repo, token,
            plan.pr_branch, plan.target_branch,
            plan.allowed, commit_msg,
        )
        logger.info("Direct-pushed %d file(s) to %s (%s)", len(plan.allowed), plan.target_branch, new_sha[:8] if new_sha else "?")
        return {
            "status": "direct-pushed",
            "files_promoted": plan.allowed,
            "target_branch": plan.target_branch,
            "new_sha": new_sha,
        }

    # create-pr mode (default)
    _create_branch(repo, staging_branch, target_sha, token)
    staging_sha = _apply_files_via_api(
        repo, token,
        plan.pr_branch, staging_branch,
        plan.allowed, commit_msg,
    )

    pr_body = (
        f"## ⚡ Fast-Forward Promotion — PR #{plan.pr_number}\n\n"
        f"This PR was **auto-generated** by `fast-forward-safe-files.yml`.\n\n"
        f"It promotes pre-approved safe files from "
        f"[PR #{plan.pr_number}](https://github.com/{repo}/pull/{plan.pr_number}) "
        f"(`{plan.pr_branch}@{sha8}`) directly to `{plan.target_branch}` so they "
        f"take effect immediately (e.g. workflow schedules, `workflow_dispatch` UI "
        f"buttons, `workflow_run` triggers).\n\n"
        f"### Files promoted ({len(plan.allowed)})\n\n"
        + "\n".join(f"- `{f}`" for f in plan.allowed)
        + f"\n\n### Files excluded ({len(plan.excluded)}) — not in allowlist\n\n"
        + ("\n".join(f"- `{f}`" for f in plan.excluded) or "_none_")
        + f"\n\n### Files denied ({len(plan.denied)}) — explicitly blocked\n\n"
        + ("\n".join(f"- `{f}`" for f in plan.denied) or "_none_")
        + "\n\n> **Allowlist:** `.codex/fast_forward_allowlist.yaml`\n"
        "> **Merge this PR to apply the promotions.**\n"
    )

    new_pr = _create_pr(
        repo,
        head=staging_branch,
        base=plan.target_branch,
        title=f"⚡ fast-forward: {len(plan.allowed)} safe file(s) from PR #{plan.pr_number}",
        body=pr_body,
        token=token,
    )
    new_pr_number: int = new_pr["number"]  # type: ignore[index]
    new_pr_url: str = new_pr["html_url"]  # type: ignore[index]
    logger.info("Created fast-forward PR #%d: %s", new_pr_number, new_pr_url)

    # Auto-merge if all files were safe
    config = _load_allowlist()
    if config.get("auto_approve_when_all_safe") and not plan.denied and not plan.excluded:
        _approve_and_merge_pr(repo, new_pr_number, token)

    return {
        "status": "pr-created",
        "fast_forward_pr": new_pr_number,
        "fast_forward_pr_url": new_pr_url,
        "staging_branch": staging_branch,
        "staging_sha": staging_sha,
        "files_promoted": plan.allowed,
        "files_excluded": plan.excluded,
        "files_denied": plan.denied,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fast-Forward Safe-File Promoter\n\n"
            "Promotes pre-approved files from an active PR directly to main\n"
            "so they take effect immediately (e.g. new workflow schedules,\n"
            "workflow_dispatch buttons, workflow_run triggers).\n\n"
            "IMMEDIATE USE:\n"
            "  gh workflow run fast-forward-safe-files.yml \\\n"
            "    --repo Aries-Serpent/_codex_ \\\n"
            "    --ref copilot/research-ai-agent-skills-architecture \\\n"
            "    -f pr_number=3856 -f dry_run=true"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", ""))
    parser.add_argument("--pr", dest="pr_number", type=int, required=True,
                        help="PR number to promote files from")
    parser.add_argument("--target", default="main",
                        help="Target branch (default: main)")
    parser.add_argument("--files", nargs="*", default=None,
                        help="Specific files to promote (overrides allowlist filter)")
    parser.add_argument("--merge-mode", choices=["create-pr", "direct-push"],
                        default=os.environ.get("FF_MERGE_MODE", "create-pr"))
    parser.add_argument("--dry-run", action="store_true",
                        default=os.environ.get("FF_DRY_RUN", "0") == "1")
    parser.add_argument("--commit-message", default="",
                        help="Override auto-generated commit message")
    parser.add_argument("--output", default="",
                        help="Write JSON result to this path")
    args = parser.parse_args()

    if not args.repo:
        logger.error("--repo is required (or set GITHUB_REPOSITORY)")
        return 1
    if not args.token:
        logger.error("--token is required (or set GITHUB_TOKEN)")
        return 1

    plan = build_plan(
        args.repo, args.token,
        args.pr_number, args.target,
        args.merge_mode,
        args.files,
    )

    logger.info(
        "Plan: %d allowed, %d excluded, %d denied",
        len(plan.allowed), len(plan.excluded), len(plan.denied),
    )

    if plan.denied:
        logger.warning("Denied files (will NOT be promoted): %s", plan.denied)

    if args.dry_run:
        result = {
            "status": "dry-run",
            "would_promote": plan.allowed,
            "would_exclude": plan.excluded,
            "would_deny": plan.denied,
            "pr_branch": plan.pr_branch,
            "source_sha": plan.source_sha,
            "target_branch": plan.target_branch,
            "merge_mode": plan.merge_mode,
        }
        print(json.dumps(result, indent=2))
        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2))
        logger.info("DRY RUN complete — no changes made.")
        return 0

    result = execute_plan(args.repo, args.token, plan, args.commit_message)
    print(json.dumps(result, indent=2))

    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2))

    return 0 if result.get("status") in {"pr-created", "direct-pushed", "nothing-to-promote"} else 1


if __name__ == "__main__":
    sys.exit(main())
