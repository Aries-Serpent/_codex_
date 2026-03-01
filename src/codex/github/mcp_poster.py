"""GitHub Actions client — posts PR comments, creates Discussions, manages
variables using CODEX_MASTER_KEY (or CODEX_BACKUP_KEY as fallback).

This module closes the autonomy loop: once CODEX_MASTER_KEY is configured
(see .codex/docs/ADMIN_MANUAL_SETUP_GUIDE.md § 3), the cognitive brain CI
feedback workflow calls ``mcp_poster post-comment`` instead of requiring
a human relay for @copilot follow-up prompts.

Usage
-----
CLI (from CI workflow)::

    python -m codex.github.mcp_poster post-comment \\
        --repo Aries-Serpent/_codex_ \\
        --pr 3401 \\
        --body-file .github/copilot-prompts/active/PR-3401-followup.md

Python API::

    from codex.github.mcp_poster import GitHubMCPPoster
    poster = GitHubMCPPoster()
    poster.post_pr_comment(repo="Aries-Serpent/_codex_", pr_number=3401, body="@copilot ...")

PDA Loop: DO phase — executes the follow-up prompt posting as part of the
AfterMath session-completion cycle.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_GITHUB_API = "https://api.github.com"
_ACCEPT = "application/vnd.github+json"
_API_VERSION = "2022-11-28"


class GitHubMCPPoster:
    """Thin GitHub REST client authenticated with CODEX_MASTER_KEY.

    Designed to be called from CI workflows after each Copilot session to:
    - Post @copilot follow-up prompts on PRs
    - Create GitHub Discussions for new pattern entries
    - Post session summaries as Discussion announcements

    Authentication
    --------------
    Reads token from environment in priority order:
    1. ``CODEX_MASTER_KEY``
    2. ``CODEX_BACKUP_KEY``
    3. ``GITHUB_TOKEN`` (fallback — likely read-only)

    If none of these are set, all write operations raise ``RuntimeError``.
    """

    def __init__(self, token: str | None = None) -> None:
        self._token = (
            token
            or os.environ.get("CODEX_MASTER_KEY")
            or os.environ.get("CODEX_BACKUP_KEY")
            or os.environ.get("GITHUB_TOKEN")
        )
        if not self._token:
            logger.warning(
                "No GitHub token found. Set CODEX_MASTER_KEY or CODEX_BACKUP_KEY. "
                "See .codex/docs/ADMIN_MANUAL_SETUP_GUIDE.md § 3."
            )

    # ------------------------------------------------------------------
    # PR comments
    # ------------------------------------------------------------------

    def post_pr_comment(
        self,
        repo: str,
        pr_number: int,
        body: str,
    ) -> dict[str, Any]:
        """Post *body* as a comment on PR *pr_number* in *repo*.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format, e.g. ``"Aries-Serpent/_codex_"``.
        pr_number:
            PR number (int).
        body:
            Comment markdown body. Must start with ``@copilot`` for
            autonomous session triggering.

        Returns
        -------
        dict
            GitHub API response payload (includes ``html_url`` of comment).

        Raises
        ------
        RuntimeError
            If no token is available.
        urllib.error.HTTPError
            If GitHub returns a non-2xx status.
        """
        self._require_token()
        url = f"{_GITHUB_API}/repos/{repo}/issues/{pr_number}/comments"
        return self._post(url, {"body": body})

    def post_pr_comment_from_file(
        self,
        repo: str,
        pr_number: int,
        body_file: str | Path,
    ) -> dict[str, Any]:
        """Read *body_file* and post its contents as a PR comment."""
        body = Path(body_file).read_text()
        return self.post_pr_comment(repo, pr_number, body)

    # ------------------------------------------------------------------
    # GitHub Discussions
    # ------------------------------------------------------------------

    def create_discussion(
        self,
        repo: str,
        title: str,
        body: str,
        category_slug: str = "cognitive-brain-patterns",
    ) -> dict[str, Any]:
        """Create a GitHub Discussion via GraphQL.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        title:
            Discussion title.
        body:
            Discussion body (markdown).
        category_slug:
            Slug of an existing Discussion category.
            See ADMIN_MANUAL_SETUP_GUIDE.md § 4 for required categories.

        Returns
        -------
        dict
            GraphQL response payload.
        """
        self._require_token()
        owner, repo_name = repo.split("/", 1)

        # Step 1: resolve repository + category node IDs
        repo_id, category_id = self._resolve_discussion_ids(owner, repo_name, category_slug)

        # Step 2: create discussion
        mutation = """
        mutation CreateDiscussion($repoId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
          createDiscussion(input: {
            repositoryId: $repoId
            categoryId: $categoryId
            title: $title
            body: $body
          }) {
            discussion { number url title }
          }
        }
        """
        variables = {
            "repoId": repo_id,
            "categoryId": category_id,
            "title": title,
            "body": body,
        }
        result = self._graphql(mutation, variables)
        return result.get("data", {}).get("createDiscussion", {}).get("discussion", result)

    def post_session_summary_discussion(
        self,
        repo: str,
        session_num: int,
        summary_md: str,
    ) -> dict[str, Any]:
        """Post a session summary as a GitHub Discussion announcement."""
        title = f"Session S{session_num} — Completion Summary"
        return self.create_discussion(
            repo=repo,
            title=title,
            body=summary_md,
            category_slug="session-summaries",
        )

    # ------------------------------------------------------------------
    # Repository variables
    # ------------------------------------------------------------------

    def set_repo_variable(self, repo: str, name: str, value: str) -> dict[str, Any]:
        """Create or update a repository Actions variable.

        Requires the token to have ``actions: write`` scope.
        """
        self._require_token()
        owner, repo_name = repo.split("/", 1)
        url = f"{_GITHUB_API}/repos/{repo}/actions/variables/{name}"
        # Try PATCH first (update existing); fall back to POST (create new)
        try:
            return self._request("PATCH", url, {"name": name, "value": value})
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                url_create = f"{_GITHUB_API}/repos/{repo}/actions/variables"
                return self._post(url_create, {"name": name, "value": value})
            raise

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_token(self) -> None:
        if not self._token:
            raise RuntimeError(
                "No GitHub token available. Set CODEX_MASTER_KEY. "
                "See .codex/docs/ADMIN_MANUAL_SETUP_GUIDE.md § 3."
            )

    def _post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", url, payload)

    def _request(self, method: str, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": _ACCEPT,
                "X-GitHub-Api-Version": _API_VERSION,
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode(errors="replace")
            logger.error("GitHub API %s %s → %d: %s", method, url, exc.code, error_body)
            raise

    def _graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        url = f"{_GITHUB_API}/graphql"
        return self._post(url, {"query": query, "variables": variables})

    def _resolve_discussion_ids(self, owner: str, repo: str, category_slug: str) -> tuple[str, str]:
        """Return (repository_node_id, category_node_id) for GraphQL mutations."""
        query = """
        query GetRepoAndCategory($owner: String!, $repo: String!) {
          repository(owner: $owner, name: $repo) {
            id
            discussionCategories(first: 20) {
              nodes { id slug name }
            }
          }
        }
        """
        result = self._graphql(query, {"owner": owner, "repo": repo})
        repo_data = result.get("data", {}).get("repository", {})
        repo_id: str = repo_data.get("id", "")
        categories = repo_data.get("discussionCategories", {}).get("nodes", [])
        category_id = ""
        for cat in categories:
            if (
                cat.get("slug") == category_slug
                or cat.get("name", "").lower().replace(" ", "-") == category_slug
            ):
                category_id = cat["id"]
                break
        if not category_id and categories:
            # Fallback to first category
            category_id = categories[0]["id"]
        return repo_id, category_id


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m codex.github.mcp_poster",
        description="Post GitHub PR comments and Discussions using CODEX_MASTER_KEY.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # post-comment
    pc = sub.add_parser("post-comment", help="Post a comment on a PR")
    pc.add_argument("--repo", required=True, help="owner/repo")
    pc.add_argument("--pr", required=True, type=int, help="PR number")
    group = pc.add_mutually_exclusive_group(required=True)
    group.add_argument("--body", help="Comment body string")
    group.add_argument("--body-file", help="Path to markdown file")

    # set-variable
    sv = sub.add_parser("set-variable", help="Create or update a repository variable")
    sv.add_argument("--repo", required=True)
    sv.add_argument("--name", required=True)
    sv.add_argument("--value", required=True)

    # create-discussion
    cd = sub.add_parser("create-discussion", help="Create a GitHub Discussion")
    cd.add_argument("--repo", required=True)
    cd.add_argument("--title", required=True)
    cd.add_argument("--body-file", required=True)
    cd.add_argument("--category", default="cognitive-brain-patterns")

    return p


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = _build_parser()
    args = parser.parse_args(argv)
    poster = GitHubMCPPoster()

    try:
        if args.command == "post-comment":
            body = args.body or Path(args.body_file).read_text()
            result = poster.post_pr_comment(args.repo, args.pr, body)
            print(f"✅ Comment posted: {result.get('html_url', result)}")

        elif args.command == "set-variable":
            result = poster.set_repo_variable(args.repo, args.name, args.value)
            print(f"✅ Variable set: {args.name}={args.value}")

        elif args.command == "create-discussion":
            body = Path(args.body_file).read_text()
            result = poster.create_discussion(args.repo, args.title, body, args.category)
            print(f"✅ Discussion created: {result.get('url', result)}")

    except RuntimeError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    except urllib.error.HTTPError as exc:
        print(f"❌ GitHub API error {exc.code}: {exc.reason}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
