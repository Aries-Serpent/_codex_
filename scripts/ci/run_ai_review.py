#!/usr/bin/env python3
"""Run the registered AI reviewer with a short-lived, repository-scoped App token."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import urllib.error
import urllib.request
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


def github_request(
    method: str,
    path: str,
    token: str,
    *,
    accept: str = "application/vnd.github+json",
) -> tuple[int, Any]:
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "codex-ai-review/1.0",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            if ".diff" in accept or accept.endswith("diff"):
                return response.status, raw.decode("utf-8", errors="replace") if raw else ""
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"message": raw.decode("utf-8", "replace")}
        return exc.code, payload


def load_review_context(
    repo: str, pr_number: int, read_token: str
) -> tuple[dict[str, Any], list[str], str]:
    status, pull_request = github_request("GET", f"/repos/{repo}/pulls/{pr_number}", read_token)
    if status != 200 or not isinstance(pull_request, dict):
        raise RuntimeError(f"Pull request lookup failed with HTTP {status}")
    if pull_request.get("state") != "open":
        raise RuntimeError("Pull request is not open")

    status, files = github_request(
        "GET", f"/repos/{repo}/pulls/{pr_number}/files?per_page=100", read_token
    )
    if status != 200 or not isinstance(files, list):
        raise RuntimeError(f"Pull request files lookup failed with HTTP {status}")

    file_names = [str(item.get("filename", "")) for item in files if item.get("filename")]
    status, diff = github_request(
        "GET",
        f"/repos/{repo}/pulls/{pr_number}",
        read_token,
        accept="application/vnd.github.v3.diff",
    )
    if status != 200:
        raise RuntimeError(f"Pull request diff lookup failed with HTTP {status}")
    return pull_request, file_names, diff if isinstance(diff, str) else ""


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

    if not isinstance(token.permissions, dict) or token.permissions.get("pull_requests") != "write":
        revoke_token(token.token)
        raise RuntimeError("GitHub App review token lacks pull_requests=write")
    status, repository = github_request("GET", f"/repos/{repo}", token.token)
    if status != 200 or not isinstance(repository, dict) or repository.get("full_name") != repo:
        revoke_token(token.token)
        raise RuntimeError("GitHub App review token is not bound to the target repository")
    return token.token, int(installation_id)


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
    reviewer = CodexQuantumReviewer(
        {
            "token": review_token,
            "base_url": "https://api.github.com",
            "timeout": 30,
            "max_retries": 3,
        }
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
    finally:
        if review_token:
            revoke_token(review_token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
