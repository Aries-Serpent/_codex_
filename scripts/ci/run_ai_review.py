#!/usr/bin/env python3
"""Run the registered AI reviewer with a short-lived, repository-scoped App token."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_ROOT = REPO_ROOT / ".github" / "agents"
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(AGENTS_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENTS_ROOT))

from codex_reviewer.main import CodexQuantumReviewer

from aries_serpent_core.auth.github_app import GitHubApp, GitHubAppConfig
from scripts.ci._token_resolver import (
    get_token,
    resolve_app_id,
    resolve_app_installation_id,
    resolve_app_private_key,
)
from scripts.ci.github_rate_limit import GitHubRateLimitError, credentials_for_token, request


def github_request(
    method: str,
    path: str,
    token: str,
    *,
    accept: str = "application/vnd.github+json",
) -> tuple[int, Any]:
    try:
        response = request(
            method,
            f"https://api.github.com{path}",
            credentials=credentials_for_token(token),
            accept=accept,
            user_agent="codex-ai-review/1.1",
        )
        return response.status, response.payload
    except GitHubRateLimitError:
        return 429, {"message": "GitHub review credential is rate-limited"}


def load_review_context(
    repo: str, pr_number: int, read_token: str
) -> tuple[dict[str, Any], list[str], str]:
    status, pull_request = github_request("GET", f"/repos/{repo}/pulls/{pr_number}", read_token)
    if status != 200 or not isinstance(pull_request, dict):
        raise RuntimeError(f"Pull request lookup failed with HTTP {status}")
    if pull_request.get("state") != "open":
        raise RuntimeError("Pull request is not open")

    files: list[Any] = []
    for page in range(1, 101):
        status, batch = github_request(
            "GET",
            f"/repos/{repo}/pulls/{pr_number}/files?per_page=100&page={page}",
            read_token,
        )
        if status != 200 or not isinstance(batch, list):
            raise RuntimeError(f"Pull request files lookup failed with HTTP {status}")
        files.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise RuntimeError("Pull request changed-file pagination did not terminate")

    expected_files = pull_request.get("changed_files")
    if not isinstance(expected_files, int) or expected_files != len(files):
        raise RuntimeError("Pull request changed-file listing is incomplete")

    file_names: list[str] = []
    diff_sections: list[str] = []
    patchless_files: list[str] = []
    for item in files:
        if not isinstance(item, dict):
            continue
        filename = str(item.get("filename", "")).strip()
        if not filename:
            continue
        file_names.append(filename)
        patch = item.get("patch")
        if isinstance(patch, str) and patch:
            diff_sections.append(
                f"diff --git a/{filename} b/{filename}\n"
                f"--- a/{filename}\n"
                f"+++ b/{filename}\n"
                f"{patch.rstrip()}"
            )
        else:
            patchless_files.append(filename)

    if patchless_files:
        status, full_diff = github_request(
            "GET",
            f"/repos/{repo}/pulls/{pr_number}",
            read_token,
            accept="application/vnd.github.v3.diff",
        )
        if status != 200 or not isinstance(full_diff, str) or not full_diff.strip():
            raise RuntimeError(f"Full diff unavailable with HTTP {status}")
        missing = [
            filename
            for filename in file_names
            if (
                f"diff --git a/{filename} b/{filename}" not in full_diff
                and f'diff --git "a/{filename}" "b/{filename}"' not in full_diff
            )
        ]
        if missing:
            raise RuntimeError(
                "Pull request full diff is incomplete; missing: " + ", ".join(missing)
            )
        return pull_request, file_names, full_diff

    diff = "\n".join(diff_sections)
    return pull_request, file_names, diff


def mint_review_token(repo: str) -> tuple[str, int]:
    app_id, _ = resolve_app_id()
    installation_id, _ = resolve_app_installation_id()
    private_key, _ = resolve_app_private_key()
    if not app_id or not installation_id or not private_key:
        raise RuntimeError("GitHub App credentials are incomplete")

    owner, name = repo.split("/", 1)
    app = GitHubApp(
        GitHubAppConfig(
            app_id=int(app_id),
            private_key_pem=private_key,
        )
    )
    token = app.get_installation_token(
        installation_id=int(installation_id),
        permissions={
            "contents": "read",
            "issues": "read",
            "pull_requests": "write",
            "metadata": "read",
        },
        repositories=[name],
        force_refresh=True,
    )
    if not hasattr(token, "token") or not token.token:
        raise RuntimeError("GitHub App did not return a repository token")

    review_token = str(token.token)
    try:
        if (
            not isinstance(token.permissions, dict)
            or token.permissions.get("pull_requests") != "write"
        ):
            raise RuntimeError("GitHub App review token lacks pull_requests=write")
        status, repository = github_request("GET", f"/repos/{repo}", review_token)
        if status != 200 or not isinstance(repository, dict) or repository.get("full_name") != repo:
            raise RuntimeError("GitHub App review token is not bound to the target repository")
        return review_token, int(installation_id)
    except Exception:
        try:
            revoke_token(review_token)
        except Exception as cleanup_error:
            raise RuntimeError(
                "GitHub App review token validation and cleanup failed"
            ) from cleanup_error
        raise


def revoke_token(token: str) -> bool:
    status, _ = github_request("DELETE", "/installation/token", token)
    if status != 204:
        raise RuntimeError(f"GitHub App token revocation failed with HTTP {status}")
    return True


async def execute_review(
    repo: str,
    pr_number: int,
    pull_request: dict[str, Any],
    file_names: list[str],
    diff: str,
    review_token: str,
) -> dict[str, Any]:
    head_sha = str((pull_request.get("head") or {}).get("sha", ""))

    def head_is_current(context: Any) -> bool:
        status, current = github_request("GET", f"/repos/{repo}/pulls/{pr_number}", review_token)
        return (
            status == 200
            and isinstance(current, dict)
            and str((current.get("head") or {}).get("sha", "")) == head_sha
            and context.head_sha == head_sha
        )

    reviewer = CodexQuantumReviewer(
        {
            "token": review_token,
            "base_url": "https://api.github.com",
            "timeout": 30,
            "max_retries": 3,
        },
        head_verifier=head_is_current,
    )
    event = {
        "action": "initial_review",
        "repository": {"full_name": repo},
        "pull_request": pull_request,
        "files_changed": file_names,
        "diff": diff,
    }
    return await reviewer.handle_event(event)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="Aries-Serpent/_codex_")
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--sha", help="Require this exact 40-character pull-request head SHA")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.sha and not re.fullmatch(r"[0-9a-fA-F]{40}", args.sha):
        parser.error("--sha must be a 40-character commit SHA")

    read_token, token_source = get_token(required_elevated=True)
    pull_request, file_names, diff = load_review_context(args.repo, args.pr, str(read_token))
    head_sha = str((pull_request.get("head") or {}).get("sha", ""))
    if args.sha and head_sha.casefold() != args.sha.casefold():
        raise RuntimeError("Pull request head SHA changed from the requested SHA")

    summary = {
        "pr": args.pr,
        "repo": args.repo,
        "head_sha": head_sha,
        "read_token_source": token_source,
        "changed_files": len(file_names),
        "diff_bytes": len(diff.encode("utf-8")),
        "dry_run": args.dry_run,
    }
    if args.dry_run:
        print(json.dumps(summary, sort_keys=True))
        return 0

    review_token = ""
    try:
        review_token, _ = mint_review_token(args.repo)
        result = asyncio.run(
            execute_review(
                args.repo,
                args.pr,
                pull_request,
                file_names,
                diff,
                review_token,
            )
        )
        print(json.dumps({**summary, "review_result": result}, sort_keys=True))
        if result.get("status") != "review_complete":
            return 1
    finally:
        if review_token:
            revoke_token(review_token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
