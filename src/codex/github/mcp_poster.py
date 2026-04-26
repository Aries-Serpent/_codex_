"""GitHub Actions client — posts PR comments, creates Discussions, manages
variables, creates branches, and opens PRs using CODEX_MASTER_KEY (or
CODEX_BACKUP_KEY as fallback).

This module closes the autonomy loop: once CODEX_MASTER_KEY is configured
(see .codex/docs/ADMIN_MANUAL_SETUP_GUIDE.md § 3), the cognitive brain CI
feedback workflow calls ``mcp_poster post-comment`` instead of requiring
a human relay for @copilot follow-up prompts.

Write operations (IMP-001 / S174 — docs/ops/MCP_PLAYWRIGHT_IMPROVEMENTS.md):
- ``create_ref()``           — create a branch ref (e.g. ``refs/heads/0D_base_``)
- ``create_pull_request()``  — open a PR without a local git clone
- ``list_pull_requests()``   — query PRs by state / head / base filters
- ``merge_branch()``         — server-side branch merge via GitHub merge API
- ``commit_files()``         — push file changes via Git Data API (IMP-002 / S178)

Usage
-----
CLI (from CI workflow)::

    python -m codex.github.mcp_poster post-comment \\
        --repo Aries-Serpent/_codex_ \\
        --pr 3401 \\
        --body-file .github/copilot-prompts/active/PR-3401-followup.md

    python -m codex.github.mcp_poster create-branch \\
        --repo Aries-Serpent/_codex_ \\
        --ref refs/heads/0D_base_ \\
        --sha 9fea48d4b01d24571b5b7b70c16dd0fedc49c9a3

    python -m codex.github.mcp_poster create-pr \\
        --repo Aries-Serpent/_codex_ \\
        --title "S174 promotion: 0D_base_ → main" \\
        --head 0D_base_ --base main

    python -m codex.github.mcp_poster commit-files \\
        --repo Aries-Serpent/_codex_ \\
        --branch 0D_base_ \\
        --message "chore: autonomous commit via Git Data API" \\
        --file README.md:README.md

Python API::

    from codex.github.mcp_poster import GitHubMCPPoster
    poster = GitHubMCPPoster()
    poster.post_pr_comment(repo="Aries-Serpent/_codex_", pr_number=3401, body="@copilot ...")
    poster.create_ref("Aries-Serpent/_codex_", "refs/heads/0D_base_", sha="abc123")
    poster.create_pull_request("Aries-Serpent/_codex_", "title", "body", "0D_base_", "main")
    poster.commit_files(
        "Aries-Serpent/_codex_", "0D_base_",
        {"README.md": "# Hello\\n"}, "docs: update README"
    )

PDA Loop: DO phase — executes the follow-up prompt posting as part of the
AfterMath session-completion cycle.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
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
    - Create branch refs (e.g. 0D_base_) without a local git clone
    - Open pull requests autonomously
    - Merge branches server-side

    Authentication
    --------------
    Reads token from environment in priority order:
    1. ``CODEX_MASTER_KEY``
    2. ``CODEX_BACKUP_KEY``
    3. ``GITHUB_TOKEN`` (fallback — likely read-only for branch/PR write ops)

    If none of these are set, all write operations raise ``RuntimeError``.
    """

    def __init__(self, token: str | None = None) -> None:
        self._token = (
            token
            or os.environ.get("CODEX_MASTER_KEY")
            or os.environ.get("CODEX_BACKUP_KEY")
            or os.environ.get("GITHUB_TOKEN")
        )
        # Track which key is active for health-check reporting (GAP-033).
        if token:
            self._token_source = "explicit"
        elif os.environ.get("CODEX_MASTER_KEY"):
            self._token_source = "CODEX_MASTER_KEY"
        elif os.environ.get("CODEX_BACKUP_KEY"):
            self._token_source = "CODEX_BACKUP_KEY"
        elif os.environ.get("GITHUB_TOKEN"):
            self._token_source = "GITHUB_TOKEN"
        else:
            self._token_source = "none"

        if not self._token:
            logger.warning(
                "No GitHub token found. Set CODEX_MASTER_KEY or CODEX_BACKUP_KEY. "
                "See .codex/docs/ADMIN_MANUAL_SETUP_GUIDE.md § 3."
            )

    # ------------------------------------------------------------------
    # GAP-033 — Token health check
    # ------------------------------------------------------------------

    def check_token_health(self) -> dict[str, object]:
        """GAP-033: Verify the active GitHub token and report its scopes / expiry.

        This resolves the systemic risk identified in the Cognitive Brain deep
        reflection (S323): when ``CODEX_MASTER_KEY`` expires or is rotated, the
        self-healing loop silently degrades because ``@copilot`` only responds to
        comments that appear to come from ``@mbaetiong`` (which requires the key).
        The fallback chain (``CODEX_BACKUP_KEY → GITHUB_TOKEN``) keeps basic API
        calls alive but lacks the ``repo + workflow`` scopes needed for rescue
        comments and workflow dispatches.

        Returns a dict with keys::

            {
                "source": "CODEX_MASTER_KEY" | "CODEX_BACKUP_KEY" | "GITHUB_TOKEN" | "none",
                "login": "<github-username>",
                "scopes": ["repo", "workflow", ...],
                "has_master_key_scopes": True | False,
                "expiry_warning": "<message>" | None,
                "healthy": True | False,
            }

        **Integration point:** call this at session start and log the result to the
        PDA loop.  CI can dispatch a ``CODEX_MASTER_KEY``-rotation alert if
        ``healthy=False``.
        """
        health: dict[str, object] = {
            "source": self._token_source,
            "login": None,
            "scopes": [],
            "has_master_key_scopes": False,
            "expiry_warning": None,
            "healthy": False,
        }
        if not self._token:
            health["expiry_warning"] = "No token configured — loop is broken."
            return health

        try:
            req = urllib.request.Request(
                f"{_GITHUB_API}/user",
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": _API_VERSION,
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:  # nosec B310
                body = json.loads(resp.read().decode())
                raw_scopes = resp.headers.get("x-oauth-scopes", "")
                status = resp.status
        except urllib.error.HTTPError as exc:
            status = exc.code
            body = {}
            raw_scopes = ""
        except Exception as exc:
            health["expiry_warning"] = f"Request failed: {exc}"
            return health

        if status == 401:
            health["expiry_warning"] = (
                f"Token ({self._token_source}) is invalid or expired. "
                "Rotate CODEX_MASTER_KEY immediately to preserve the self-healing loop."
            )
            logger.error(health["expiry_warning"])
            return health

        if status != 200:
            health["expiry_warning"] = f"Unexpected /user status {status}"
            return health

        health["login"] = body.get("login")

        # Parse OAuth scopes from response header
        scopes = [s.strip() for s in raw_scopes.split(",") if s.strip()]
        health["scopes"] = scopes

        required = {"repo", "workflow"}
        health["has_master_key_scopes"] = required.issubset(set(scopes))

        if not health["has_master_key_scopes"] and self._token_source in (
            "CODEX_MASTER_KEY", "CODEX_BACKUP_KEY"
        ):
            missing = required - set(scopes)
            health["expiry_warning"] = (
                f"Token ({self._token_source}) is missing required scopes: "
                f"{missing}.  Self-healing loop will silently degrade."
            )
            logger.warning(health["expiry_warning"])

        health["healthy"] = bool(health["has_master_key_scopes"])
        return health

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
        return self._request("POST", url, {"body": body})

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
        result = self._graphql_with_retry(mutation, variables, operation_name="CreateDiscussion")
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

    def add_discussion_comment(
        self,
        repo: str,
        discussion_number: int,
        body: str,
    ) -> dict[str, Any]:
        """Add a comment to an existing GitHub Discussion via GraphQL.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        discussion_number:
            The integer number of the target discussion (visible in the URL).
        body:
            Comment body in Markdown.

        Returns
        -------
        dict
            GraphQL response payload with ``id``, ``url``, ``body``.
        """
        self._require_token()
        owner, repo_name = repo.split("/", 1)

        # Step 1: resolve the discussion node ID
        discussion_id = self._resolve_discussion_node_id(owner, repo_name, discussion_number)

        # Step 2: add comment
        mutation = """
        mutation AddDiscussionComment($discussionId: ID!, $body: String!) {
          addDiscussionComment(input: { discussionId: $discussionId, body: $body }) {
            comment { id url body }
          }
        }
        """
        result = self._graphql(mutation, {"discussionId": discussion_id, "body": body})
        # Surface GraphQL-level errors (HTTP 200 but errors in body, e.g. FORBIDDEN)
        gql_errors = result.get("errors") if result else None
        if gql_errors:
            first_err = gql_errors[0]
            err_type = first_err.get("type", "UNKNOWN")
            err_msg = first_err.get("message", str(gql_errors))
            raise PermissionError(
                f"GitHub Discussion comment FORBIDDEN ({err_type}): {err_msg}. "
                "Ensure the token has 'write:discussion' scope (PAT) or the workflow "
                "declares 'discussions: write' permission."
            )
        comment_data = (result or {}).get("data", {}).get("addDiscussionComment")
        if comment_data is None:
            raise RuntimeError(
                f"addDiscussionComment returned null for discussion #{discussion_number}. "
                "Full response: " + str(result)
            )
        return comment_data.get("comment", comment_data)

    def upsert_discussion_comment(
        self,
        repo: str,
        discussion_number: int,
        body: str,
        marker: str = "",
    ) -> dict[str, Any]:
        """Idempotent add-or-update of a Discussion comment.

        Searches existing comments in *discussion_number* for one whose body
        contains *marker*.  If found, updates it; otherwise posts a new comment.
        This prevents duplicate status summaries when a workflow runs multiple
        times on the same discussion.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        discussion_number:
            Integer number of the target Discussion.
        body:
            Full Markdown comment body (should include *marker* so future calls
            can identify it).
        marker:
            A unique string used to detect whether a previous comment from this
            caller already exists.  If empty, always creates a new comment.

        Returns
        -------
        dict
            GraphQL response payload.
        """
        self._require_token()
        owner, repo_name = repo.split("/", 1)

        if marker:
            existing_id = self._find_discussion_comment(owner, repo_name, discussion_number, marker)
            if existing_id:
                return self._update_discussion_comment(existing_id, body)

        return self.add_discussion_comment(repo, discussion_number, body)

    def post_ci_pattern_summary(
        self,
        repo: str,
        discussion_number: int,
        summary_md: str,
        session_id: str = "",
    ) -> dict[str, Any]:
        """Post (or update) a CI pattern knowledge-graph summary as a Discussion comment.

        Uses ``upsert_discussion_comment`` so each session's summary replaces
        the previous one rather than growing the thread indefinitely.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        discussion_number:
            Target Discussion number (e.g. 3673 for the accountability thread).
        summary_md:
            Markdown content — typically output from ``pattern_recorder summary``.
        session_id:
            Optional session ID embedded in the marker for deduplication.
        """
        marker = (
            f"<!-- ci-pattern-summary:{session_id} -->"
            if session_id
            else "<!-- ci-pattern-summary -->"
        )
        full_body = f"{marker}\n{summary_md}"
        return self.upsert_discussion_comment(repo, discussion_number, full_body, marker)

    def post_continuation_chain(
        self,
        repo: str,
        discussion_number: int,
        chain_md: str,
    ) -> dict[str, Any]:
        """Post a tokenized continuation chain prompt as a new Discussion comment.

        Continuation chains are always posted as new comments (not upserted)
        so the discussion thread preserves the full history of chain prompts.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        discussion_number:
            Target Discussion number.
        chain_md:
            Full Markdown content of the continuation chain prompt, including
            tokenized context sections and ``@copilot continue`` call-to-action.
        """
        return self.add_discussion_comment(repo, discussion_number, chain_md)

    # ------------------------------------------------------------------
    # Discussion internals
    # ------------------------------------------------------------------

    def _resolve_discussion_node_id(self, owner: str, repo: str, discussion_number: int) -> str:
        """Return the GraphQL node ID for a Discussion identified by its number."""
        query = """
        query GetDiscussionId($owner: String!, $repo: String!, $number: Int!) {
          repository(owner: $owner, name: $repo) {
            discussion(number: $number) { id }
          }
        }
        """
        result = self._graphql(query, {"owner": owner, "repo": repo, "number": discussion_number})
        discussion = result.get("data", {}).get("repository", {}).get("discussion") or {}
        node_id: str = discussion.get("id", "")
        if not node_id:
            raise RuntimeError(
                f"Discussion #{discussion_number} not found in {owner}/{repo}. "
                "Ensure the discussion exists and the token has 'discussions:write' scope."
            )
        return node_id

    def _find_discussion_comment(
        self, owner: str, repo: str, discussion_number: int, marker: str
    ) -> str:
        """Return the node ID of the most-recent comment containing *marker*, or ``""``.

        Searches newest-first using ``last: 100`` with backward cursor pagination
        so that recent upsert markers are found quickly even in high-volume threads
        (e.g. Discussion #3756 with 700+ comments).  Continues paginating backward
        through older pages until the marker is found or all comments are exhausted.
        """
        query = """
        query FindDiscussionComment(
          $owner: String!, $repo: String!, $number: Int!, $cursor: String
        ) {
          repository(owner: $owner, name: $repo) {
            discussion(number: $number) {
              comments(last: 100, before: $cursor) {
                nodes { id body }
                pageInfo { hasPreviousPage startCursor }
              }
            }
          }
        }
        """
        cursor: str | None = None
        while True:
            result = self._graphql(
                query,
                {"owner": owner, "repo": repo, "number": discussion_number, "cursor": cursor},
            )
            disc = (
                result.get("data", {})
                .get("repository", {})
                .get("discussion", {})
                .get("comments", {})
            )
            nodes = disc.get("nodes", [])
            page_info = disc.get("pageInfo", {})
            # Iterate newest→oldest within this page
            for c in reversed(nodes):
                if marker in (c.get("body") or ""):
                    return c["id"]
            if not page_info.get("hasPreviousPage"):
                break
            cursor = page_info.get("startCursor")
        return ""

    # ------------------------------------------------------------------
    # Per-PR discussion auto-create / find-or-create
    # ------------------------------------------------------------------

    def find_or_create_pr_discussion(
        self,
        repo: str,
        pr_number: int,
        purpose: str,
        category_slug: str = "show-and-tell",
    ) -> tuple[int, str]:
        """Find an existing discussion for a PR + purpose, or create one.

        This is the canonical entry-point for all per-PR discussion posting.
        It removes the need to hard-code discussion numbers (e.g. #3673, #3756)
        in workflows and scripts — every PR gets its own isolated thread.

        Title format
        ~~~~~~~~~~~~
        ``"🤖 {purpose_title} — PR #{pr_number}"``

        Supported *purpose* values and their titles
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ``"accountability"``   → ``"📋 Agent Accountability — PR #{pr_number}"``
        ``"pre-session"``      → ``"🧠 Pre-Session Context — PR #{pr_number}"``
        ``"qa"``               → ``"❓ Q&A — PR #{pr_number}"``

        Any other string is used as-is for the title prefix.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        pr_number:
            The PR number to scope this discussion to.
        purpose:
            Short identifier for the discussion's purpose (see above).
        category_slug:
            Slug of the Discussion category to create in if needed.
            Defaults to ``"show-and-tell"`` (always available).

        Returns
        -------
        tuple[int, str]
            ``(discussion_number, discussion_node_id)``

        Raises
        ------
        RuntimeError
            If neither an existing discussion is found nor a new one can be created.
        """
        self._require_token()
        owner, repo_name = repo.split("/", 1)

        _PURPOSE_TITLES = {
            "accountability": f"📋 Agent Accountability — PR #{pr_number}",
            "pre-session": f"🧠 Pre-Session Context — PR #{pr_number}",
            "qa": f"❓ Q&A — PR #{pr_number}",
        }
        title = _PURPOSE_TITLES.get(purpose, f"🤖 {purpose} — PR #{pr_number}")
        # Dedup marker embedded in the discussion *body* (not a comment)
        registry_marker = f"<!-- pr-discussion-registry:{pr_number}:{purpose} -->"

        # Search existing discussions for matching title OR body marker
        # (search newest-first; discussions are ordered by UPDATED_AT DESC)
        page_cursor: str | None = None
        while True:
            _, category_id = self._resolve_discussion_ids(owner, repo_name, category_slug)
            list_query = """
            query ListDiscussions(
              $owner: String!, $repo: String!, $first: Int!, $after: String
            ) {
              repository(owner: $owner, name: $repo) {
                discussions(
                  first: $first, after: $after,
                  orderBy: {field: UPDATED_AT, direction: DESC}
                ) {
                  pageInfo { hasNextPage endCursor }
                  nodes { number id title body }
                }
              }
            }
            """
            result = self._graphql(
                list_query,
                {"owner": owner, "repo": repo_name, "first": 50, "after": page_cursor},
            )
            page = result.get("data", {}).get("repository", {}).get("discussions", {})
            for d in page.get("nodes", []):
                if d.get("title") == title or registry_marker in (d.get("body") or ""):
                    return d["number"], d["id"]
            page_info = page.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            page_cursor = page_info.get("endCursor")

        # Not found — create a new discussion
        _PURPOSE_DESCRIPTIONS = {
            "accountability": (
                "Automatically maintained by `post-accountability-to-discussion.yml`.\n\n"
                "Each comment in this discussion is one session's accountability entry for "
                f"PR #{pr_number}. Copilot Coding Agent posts here at the end of every session "
                "and checks this thread for maintainer feedback at the start of the next session."
            ),
            "pre-session": (
                "Automatically maintained by `scripts/ci/discussion_context_store.py` (P6-C).\n\n"
                "Each comment contains a structured pre-session briefing (§A workflow status, "
                f"§B blocking comments, §D action queue) for PR #{pr_number}. "
                "Copilot reads the latest comment here at session start."
            ),
            "qa": (
                "Automatically maintained by `copilot-agent-checkin.yml`.\n\n"
                f"Q&A thread for PR #{pr_number}. Copilot posts questions derived from the "
                "current PDA pattern library and CI failure state. "
                "Maintainer responses are detected at session close and acted on."
            ),
        }
        description = _PURPOSE_DESCRIPTIONS.get(
            purpose,
            f"Automatically maintained discussion for PR #{pr_number} — purpose: {purpose}.",
        )
        body = (
            f"{registry_marker}\n\n"
            f"**PR:** #{pr_number} · **Repo:** [{repo}](https://github.com/{repo})\n\n"
            f"{description}\n\n"
            f"**⚠️ Do not delete this discussion** — it is the canonical record for its purpose."
        )
        discussion = self.create_discussion(
            repo=repo, title=title, body=body, category_slug=category_slug
        )
        number = discussion.get("number")
        node_id = discussion.get("id") or discussion.get("url", "")
        if not number:
            raise RuntimeError(
                f"find_or_create_pr_discussion: createDiscussion returned no number. "
                f"Response: {discussion}"
            )
        logger.info(
            "Created new %r discussion #%s for PR #%s in %s",
            purpose,
            number,
            pr_number,
            repo,
        )
        return int(number), str(node_id)

    # ------------------------------------------------------------------
    # Response-checking: detect unread maintainer replies
    # ------------------------------------------------------------------

    _BOT_LOGINS: frozenset[str] = frozenset(
        {
            "github-actions[bot]",
            "copilot-swe-agent[bot]",
            "github-copilot[bot]",
            "copilot[bot]",
            "dependabot[bot]",
        }
    )

    def check_discussion_replies(
        self,
        repo: str,
        discussion_number: int,
        since_marker: str = "",
        max_comments: int = 200,
    ) -> list[dict[str, Any]]:
        """Return a list of unread human replies in a discussion thread.

        "Unread" means: posted by a non-bot author AND appearing *after* the
        most recent Copilot-agent comment in the same thread (or after the
        comment identified by *since_marker*).

        This lets Copilot Coding Agent check at session start whether the
        maintainer has responded to any accountability entry or Q&A post
        without needing to be explicitly prompted.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        discussion_number:
            The discussion to check (e.g. the per-PR accountability discussion).
        since_marker:
            Optional HTML-comment marker string.  If supplied, only replies
            posted *after* the comment containing this marker are returned.
            If empty, replies after the latest Copilot comment are returned.
        max_comments:
            Maximum number of recent comments to fetch (newest first).

        Returns
        -------
        list[dict]
            Each entry has keys: ``author``, ``body`` (first 300 chars),
            ``url``, ``created_at``, ``in_reply_to_marker``.
        """
        self._require_token()
        owner, repo_name = repo.split("/", 1)

        # Fetch newest max_comments comments (last: N paginated)
        query = """
        query CheckReplies(
          $owner: String!, $repo: String!, $number: Int!, $cursor: String
        ) {
          repository(owner: $owner, name: $repo) {
            discussion(number: $number) {
              comments(last: 100, before: $cursor) {
                nodes {
                  id body createdAt url
                  author { login }
                  replies(first: 20) {
                    nodes { id body createdAt url author { login } }
                  }
                }
                pageInfo { hasPreviousPage startCursor }
              }
            }
          }
        }
        """
        all_comments: list[dict] = []
        cursor: str | None = None
        fetched = 0
        while fetched < max_comments:
            result = self._graphql(
                query,
                {"owner": owner, "repo": repo_name, "number": discussion_number, "cursor": cursor},
            )
            disc = (
                result.get("data", {})
                .get("repository", {})
                .get("discussion", {})
                .get("comments", {})
            )
            nodes = disc.get("nodes", [])
            all_comments = nodes + all_comments  # prepend so list is oldest→newest
            fetched += len(nodes)
            page_info = disc.get("pageInfo", {})
            if not page_info.get("hasPreviousPage") or not nodes:
                break
            cursor = page_info.get("startCursor")

        if not all_comments:
            return []

        # Find the anchor point: the latest Copilot comment OR the since_marker comment
        anchor_idx = -1
        for i, c in enumerate(all_comments):
            login = (c.get("author") or {}).get("login", "")
            body = c.get("body") or ""
            if since_marker and since_marker in body:
                anchor_idx = i
                break
            if not since_marker and login in (
                "copilot-swe-agent[bot]",
                "github-copilot[bot]",
                "copilot[bot]",
            ):
                anchor_idx = i  # keep updating — want the LAST one

        unread: list[dict[str, Any]] = []

        # Collect top-level non-bot comments posted after anchor
        for i, c in enumerate(all_comments):
            if i <= anchor_idx:
                continue
            login = (c.get("author") or {}).get("login", "")
            if login in self._BOT_LOGINS:
                continue
            unread.append(
                {
                    "author": login,
                    "body": (c.get("body") or "")[:300],
                    "url": c.get("url", ""),
                    "created_at": c.get("createdAt", ""),
                    "in_reply_to_marker": "",
                    "type": "comment",
                }
            )

        # Collect reply-thread entries anywhere in the discussion
        for c in all_comments:
            for r in (c.get("replies") or {}).get("nodes", []):
                login = (r.get("author") or {}).get("login", "")
                if login in self._BOT_LOGINS:
                    continue
                # Only count replies posted after the anchor comment's timestamp
                anchor_ts = all_comments[anchor_idx].get("createdAt", "") if anchor_idx >= 0 else ""
                if anchor_ts and r.get("createdAt", "") <= anchor_ts:
                    continue
                unread.append(
                    {
                        "author": login,
                        "body": (r.get("body") or "")[:300],
                        "url": r.get("url", ""),
                        "created_at": r.get("createdAt", ""),
                        "in_reply_to_marker": since_marker,
                        "type": "reply",
                    }
                )

        return unread

    def _update_discussion_comment(self, comment_id: str, body: str) -> dict[str, Any]:
        """Update an existing Discussion comment by its GraphQL node ID."""
        mutation = """
        mutation UpdateDiscussionComment($commentId: ID!, $body: String!) {
          updateDiscussionComment(input: { commentId: $commentId, body: $body }) {
            comment { id url body }
          }
        }
        """
        result = self._graphql(mutation, {"commentId": comment_id, "body": body})
        return result.get("data", {}).get("updateDiscussionComment", {}).get("comment", result)

    def update_discussion(
        self,
        repo: str,
        discussion_number: int,
        *,
        title: str | None = None,
        body: str | None = None,
        category_slug: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing Discussion's title, body, and/or category.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        discussion_number:
            The integer discussion number (visible in the URL).
        title, body:
            New values; ``None`` means leave unchanged.
        category_slug:
            Slug of a new category to move the discussion into; ``None`` leaves it.

        Returns
        -------
        dict
            GraphQL ``updateDiscussion.discussion`` payload.
        """
        self._require_token()
        owner, repo_name = repo.split("/", 1)
        discussion_id = self._resolve_discussion_node_id(owner, repo_name, discussion_number)

        variables: dict[str, Any] = {"discussionId": discussion_id}
        if title is not None:
            variables["title"] = title
        if body is not None:
            variables["body"] = body
        if category_slug is not None:
            _, category_id = self._resolve_discussion_ids(owner, repo_name, category_slug)
            variables["categoryId"] = category_id

        mutation = """
        mutation UpdateDiscussion(
          $discussionId: ID!
          $title: String
          $body: String
          $categoryId: ID
        ) {
          updateDiscussion(input: {
            discussionId: $discussionId
            title: $title
            body: $body
            categoryId: $categoryId
          }) {
            discussion { number url title }
          }
        }
        """
        result = self._graphql(mutation, variables)
        return result.get("data", {}).get("updateDiscussion", {}).get("discussion", result)

    def lock_discussion(
        self,
        repo: str,
        discussion_number: int,
        reason: str = "RESOLVED",
    ) -> dict[str, Any]:
        """Lock a Discussion to prevent further comments.

        Parameters
        ----------
        reason:
            One of ``"OFF_TOPIC"``, ``"RESOLVED"``, ``"SPAM"``, ``"TOO_HEATED"``.
        """
        self._require_token()
        owner, repo_name = repo.split("/", 1)
        discussion_id = self._resolve_discussion_node_id(owner, repo_name, discussion_number)
        mutation = """
        mutation LockDiscussion($id: ID!, $reason: LockReason) {
          lockLockable(input: { lockableId: $id, lockReason: $reason }) {
            lockedRecord { ... on Discussion { number url } }
          }
        }
        """
        result = self._graphql(mutation, {"id": discussion_id, "reason": reason})
        return result.get("data", {}).get("lockLockable", result)

    def unlock_discussion(self, repo: str, discussion_number: int) -> dict[str, Any]:
        """Unlock a previously locked Discussion."""
        self._require_token()
        owner, repo_name = repo.split("/", 1)
        discussion_id = self._resolve_discussion_node_id(owner, repo_name, discussion_number)
        mutation = """
        mutation UnlockDiscussion($id: ID!) {
          unlockLockable(input: { lockableId: $id }) {
            unlockedRecord { ... on Discussion { number url } }
          }
        }
        """
        result = self._graphql(mutation, {"id": discussion_id})
        return result.get("data", {}).get("unlockLockable", result)

    def delete_discussion(self, repo: str, discussion_number: int) -> bool:
        """Permanently delete a Discussion.

        Returns ``True`` if deletion succeeded, ``False`` otherwise.
        Requires admin-level token with ``discussions:write`` scope.
        """
        self._require_token()
        owner, repo_name = repo.split("/", 1)
        discussion_id = self._resolve_discussion_node_id(owner, repo_name, discussion_number)
        mutation = """
        mutation DeleteDiscussion($id: ID!) {
          deleteDiscussion(input: { id: $id }) {
            clientMutationId
          }
        }
        """
        result = self._graphql(mutation, {"id": discussion_id})
        return "errors" not in result

    def delete_discussion_comment(self, comment_id: str) -> bool:
        """Delete a Discussion comment by its GraphQL node ID.

        Returns ``True`` if deletion succeeded, ``False`` otherwise.
        """
        self._require_token()
        mutation = """
        mutation DeleteDiscussionComment($id: ID!) {
          deleteDiscussionComment(input: { id: $id }) {
            clientMutationId
          }
        }
        """
        result = self._graphql(mutation, {"id": comment_id})
        return "errors" not in result

    def mark_answer(self, comment_id: str) -> dict[str, Any]:
        """Mark a Discussion comment as the accepted answer.

        Parameters
        ----------
        comment_id:
            GraphQL node ID of the comment (obtain from ``add_discussion_comment``
            or ``_find_discussion_comment``).
        """
        self._require_token()
        mutation = """
        mutation MarkAnswer($commentId: ID!) {
          markDiscussionCommentAsAnswer(input: { id: $commentId }) {
            discussion { number url }
          }
        }
        """
        result = self._graphql(mutation, {"commentId": comment_id})
        return (
            result.get("data", {})
            .get("markDiscussionCommentAsAnswer", {})
            .get("discussion", result)
        )

    def unmark_answer(self, comment_id: str) -> dict[str, Any]:
        """Unmark a previously accepted answer on a Discussion."""
        self._require_token()
        mutation = """
        mutation UnmarkAnswer($commentId: ID!) {
          unmarkDiscussionCommentAsAnswer(input: { id: $commentId }) {
            discussion { number url }
          }
        }
        """
        result = self._graphql(mutation, {"commentId": comment_id})
        return (
            result.get("data", {})
            .get("unmarkDiscussionCommentAsAnswer", {})
            .get("discussion", result)
        )

    def list_discussions(
        self,
        repo: str,
        category_slug: str | None = None,
        first: int = 20,
        after: str | None = None,
    ) -> dict[str, Any]:
        """List Discussions in a repository, optionally filtered by category.

        Parameters
        ----------
        category_slug:
            Filter to this category; ``None`` returns all categories.
        first:
            Number of discussions to return (max 100 per GitHub's GraphQL limits).
        after:
            Cursor for pagination.  Pass ``pageInfo.endCursor`` from a previous
            response to retrieve the next page.

        Returns
        -------
        dict
            ``nodes`` — list of discussion dicts with ``number``, ``title``,
            ``url``, ``category`` (name), ``createdAt``, ``isAnswered``,
            ``comments`` (count).
            ``pageInfo`` — ``{"endCursor": str | None, "hasNextPage": bool}``.
        """
        self._require_token()
        owner, repo_name = repo.split("/", 1)

        category_id: str | None = None
        if category_slug:
            _, category_id = self._resolve_discussion_ids(owner, repo_name, category_slug)

        query = """
        query ListDiscussions(
          $owner: String!, $repo: String!, $first: Int!,
          $categoryId: ID, $after: String
        ) {
          repository(owner: $owner, name: $repo) {
            discussions(
              first: $first, categoryId: $categoryId, after: $after,
              orderBy: {field: UPDATED_AT, direction: DESC}
            ) {
              pageInfo { endCursor hasNextPage }
              nodes {
                number
                title
                url
                createdAt
                updatedAt
                isAnswered
                category { name slug }
                comments { totalCount }
                author { login }
              }
            }
          }
        }
        """
        variables: dict[str, Any] = {
            "owner": owner,
            "repo": repo_name,
            "first": min(first, 100),
            "categoryId": category_id,
            "after": after,
        }
        result = self._graphql(query, variables)
        disc_data = result.get("data", {}).get("repository", {}).get("discussions", {})
        return {
            "nodes": disc_data.get("nodes", []),
            "pageInfo": disc_data.get("pageInfo", {"endCursor": None, "hasNextPage": False}),
        }

    def get_discussion(
        self,
        repo: str,
        discussion_number: int,
        comments_first: int = 50,
        comments_after: str | None = None,
    ) -> dict[str, Any]:
        """Fetch a single Discussion by number including its comments.

        Parameters
        ----------
        repo:
            Full repository name (``owner/repo``).
        discussion_number:
            The discussion number (visible in the URL).
        comments_first:
            Number of comments to return per page (max 100).
        comments_after:
            Cursor for comment pagination.  Pass ``comments.pageInfo.endCursor``
            from a previous response to retrieve the next comment page.

        Returns
        -------
        dict
            Discussion fields: ``id`` (node ID), ``number``, ``title``,
            ``body``, ``url``, ``category``, ``isAnswered``, ``comments`` with
            ``totalCount``, ``pageInfo``, and ``nodes`` (up to *comments_first*).
            The ``id`` field is the GraphQL node ID required by mutations such
            as :meth:`pin_discussion`.
        """
        self._require_token()
        owner, repo_name = repo.split("/", 1)
        query = """
        query GetDiscussion(
          $owner: String!, $repo: String!, $number: Int!,
          $commentsFirst: Int!, $commentsAfter: String
        ) {
          repository(owner: $owner, name: $repo) {
            discussion(number: $number) {
              id number title url body createdAt updatedAt isAnswered isLocked
              category { name slug }
              author { login }
              comments(first: $commentsFirst, after: $commentsAfter) {
                totalCount
                pageInfo { endCursor hasNextPage }
                nodes { id body createdAt author { login } isAnswer }
              }
            }
          }
        }
        """
        result = self._graphql(
            query,
            {
                "owner": owner,
                "repo": repo_name,
                "number": discussion_number,
                "commentsFirst": min(comments_first, 100),
                "commentsAfter": comments_after,
            },
        )
        disc = result.get("data", {}).get("repository", {}).get("discussion")
        if disc is None:
            raise RuntimeError(f"Discussion #{discussion_number} not found in {owner}/{repo_name}")
        return disc

    def pin_discussion(self, repo: str, discussion_number: int) -> dict[str, Any]:
        """Pin a Discussion to the repository.

        Requires the token to have ``discussions: write`` scope.

        Parameters
        ----------
        repo:
            Full repository name (``owner/repo``).
        discussion_number:
            The discussion number (visible in the URL).

        Returns
        -------
        dict
            The pinned discussion fields returned by the GraphQL mutation.
        """
        self._require_token()
        disc = self.get_discussion(repo, discussion_number)
        discussion_id: str = disc["id"]
        mutation = """
        mutation PinDiscussion($discussionId: ID!) {
          pinDiscussion(input: { discussionId: $discussionId }) {
            discussion { id number title url }
          }
        }
        """
        result = self._graphql(mutation, {"discussionId": discussion_id})
        return result.get("data", {}).get("pinDiscussion", {}).get("discussion", result)

    def unpin_discussion(self, repo: str, discussion_number: int) -> dict[str, Any]:
        """Unpin a previously pinned Discussion from the repository.

        Requires the token to have ``discussions: write`` scope.

        Parameters
        ----------
        repo:
            Full repository name (``owner/repo``).
        discussion_number:
            The discussion number (visible in the URL).

        Returns
        -------
        dict
            The discussion fields returned by the GraphQL mutation.
        """
        self._require_token()
        disc = self.get_discussion(repo, discussion_number)
        discussion_id: str = disc["id"]
        mutation = """
        mutation UnpinDiscussion($discussionId: ID!) {
          unpinDiscussion(input: { discussionId: $discussionId }) {
            discussion { id number title url }
          }
        }
        """
        result = self._graphql(mutation, {"discussionId": discussion_id})
        return result.get("data", {}).get("unpinDiscussion", {}).get("discussion", result)

    def list_discussion_categories(self, repo: str) -> list[dict[str, Any]]:
        """List all Discussion categories in a repository.

        **Note:** Categories can only be *created* or *deleted* via the GitHub web UI
        (Settings → Discussions).  This method is read-only.

        Returns
        -------
        list[dict]
            Each entry has ``id``, ``name``, ``slug``, ``description``,
            ``emojiHTML``, ``isAnswerable``.
        """
        self._require_token()
        owner, repo_name = repo.split("/", 1)
        query = """
        query ListCategories($owner: String!, $repo: String!) {
          repository(owner: $owner, name: $repo) {
            discussionCategories(first: 25) {
              nodes { id name slug description emojiHTML isAnswerable }
            }
          }
        }
        """
        result = self._graphql(query, {"owner": owner, "repo": repo_name})
        return (
            result.get("data", {})
            .get("repository", {})
            .get("discussionCategories", {})
            .get("nodes", [])
        )

    # ------------------------------------------------------------------
    # Repository variables
    # ------------------------------------------------------------------

    def set_repo_variable(self, repo: str, name: str, value: str) -> dict[str, Any]:
        """Create or update a repository Actions variable.

        Requires the token to have ``actions: write`` scope.
        """
        self._require_token()
        url = f"{_GITHUB_API}/repos/{repo}/actions/variables/{name}"
        # Try PATCH first (update existing); fall back to POST (create new)
        try:
            return self._request("PATCH", url, {"name": name, "value": value})
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                url_create = f"{_GITHUB_API}/repos/{repo}/actions/variables"
                return self._request("POST", url_create, {"name": name, "value": value})
            raise

    # ------------------------------------------------------------------
    # Branch & PR management (IMP-001 — S174)
    # ------------------------------------------------------------------

    def create_ref(self, repo: str, ref: str, sha: str) -> dict[str, Any]:
        """Create a git reference (branch or tag) on GitHub.

        Requires the token to have ``contents: write`` scope.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format, e.g. ``"Aries-Serpent/_codex_"``.
        ref:
            Full ref name, e.g. ``"refs/heads/0D_base_"``.
        sha:
            40-character commit SHA the new ref should point to.
            The commit must already exist in the repository (pushed
            via another mechanism such as a PR merge).

        Returns
        -------
        dict
            GitHub API response payload with ``ref`` and ``object.sha``.

        Raises
        ------
        RuntimeError
            If no token is available.
        urllib.error.HTTPError
            If GitHub returns non-2xx (e.g. 422 ref already exists,
            403 insufficient token scope).
        """
        self._require_token()
        # Normalise the ref: only add refs/heads/ when the caller passes a bare
        # branch name (no slash at all).  Explicit refs/heads/…, refs/tags/…, or
        # heads/… / tags/… prefixes are left intact to avoid double-prefixing.
        if not ref.startswith("refs/"):
            if ref.startswith("heads/") or ref.startswith("tags/"):
                ref = f"refs/{ref}"
            else:
                ref = f"refs/heads/{ref}"
        url = f"{_GITHUB_API}/repos/{repo}/git/refs"
        result = self._request("POST", url, {"ref": ref, "sha": sha})
        self._record_cb_pattern(
            "CB-branch-create",
            f"create_ref: {ref} @ {sha[:8] if sha else sha}",
            {"repo": repo, "ref": ref, "sha": sha},
        )
        return result

    def create_pull_request(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str,
        draft: bool = False,
    ) -> dict[str, Any]:
        """Open a pull request on GitHub.

        Requires the token to have ``pull-requests: write`` scope.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        title:
            PR title string.
        body:
            PR description (markdown).
        head:
            Branch name for the source (head) of the PR,
            e.g. ``"0D_base_"``.
        base:
            Branch name for the target (base) of the PR,
            e.g. ``"main"``.
        draft:
            When ``True``, open as a draft PR.

        Returns
        -------
        dict
            GitHub API response payload including ``number`` and
            ``html_url``.
        """
        self._require_token()
        url = f"{_GITHUB_API}/repos/{repo}/pulls"
        result = self._request(
            "POST",
            url,
            {
                "title": title,
                "body": body,
                "head": head,
                "base": base,
                "draft": draft,
            },
        )
        self._record_cb_pattern(
            "CB-pr-open",
            f"create_pull_request: {head!r} → {base!r} (#{result.get('number', '?')})",
            {
                "repo": repo,
                "head": head,
                "base": base,
                "pr_number": result.get("number"),
                "draft": draft,
            },
        )
        return result

    def list_pull_requests(
        self,
        repo: str,
        state: str = "open",
        head: str = "",
        base: str = "",
        per_page: int = 30,
    ) -> list[dict[str, Any]]:
        """List pull requests, optionally filtered by head/base branch.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        state:
            One of ``"open"``, ``"closed"``, or ``"all"``.
        head:
            Filter by head branch name.  The GitHub REST API requires the
            ``owner:branch`` format; pass a bare branch name and the owner
            will be derived from *repo* automatically.
        base:
            Filter by base branch name.
        per_page:
            Number of results per page (max 100).

        Returns
        -------
        list[dict]
            List of PR objects from the GitHub API.
        """
        self._require_token()
        params = [f"state={state}", f"per_page={min(per_page, 100)}"]
        if head:
            # GitHub requires "owner:branch" format for the head filter.
            # Derive the owner from repo when the caller passes a bare branch name.
            if ":" not in head:
                owner = repo.split("/")[0]
                head = f"{owner}:{head}"
            params.append(f"head={head}")
        if base:
            params.append(f"base={base}")
        url = f"{_GITHUB_API}/repos/{repo}/pulls?{'&'.join(params)}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": _ACCEPT,
                "X-GitHub-Api-Version": _API_VERSION,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode(errors="replace")
            logger.error("GitHub API GET %s → %d: %s", url, exc.code, error_body)
            raise

    def merge_branch(
        self,
        repo: str,
        base: str,
        head: str,
        commit_message: str = "",
    ) -> dict[str, Any]:
        """Merge *head* into *base* via GitHub's server-side merge API.

        Creates a merge commit on GitHub without requiring a local git
        clone or ``git push`` — ideal for autonomous branch management.
        The resulting commit SHA can be used with :meth:`create_ref` to
        create or update a branch pointing to the merge result.

        Requires the token to have ``contents: write`` scope.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        base:
            Target branch name (e.g. ``"0D_base_"``).
        head:
            Source branch name or commit SHA to merge in.
        commit_message:
            Optional custom merge commit message.

        Returns
        -------
        dict
            GitHub API response with ``sha``, ``commit``, and
            ``parents`` keys — or an empty dict when no merge was
            necessary (already up-to-date).

        Raises
        ------
        urllib.error.HTTPError
            HTTP 409 when there is a merge conflict.
        """
        self._require_token()
        url = f"{_GITHUB_API}/repos/{repo}/merges"
        payload: dict[str, Any] = {"base": base, "head": head}
        if commit_message:
            payload["commit_message"] = commit_message
        result = self._request("POST", url, payload)
        outcome = "success" if result else "already_exists"
        self._record_cb_pattern(
            "CB-merge",
            f"merge_branch: {head!r} → {base!r} outcome={outcome}",
            {
                "repo": repo,
                "base": base,
                "head": head,
                "sha": result.get("sha", "") if result else "",
            },
            outcome=outcome,
        )
        return result

    # ------------------------------------------------------------------
    # Git Data API — autonomous commits (IMP-002 — S178)
    # ------------------------------------------------------------------

    def _create_blob(self, repo: str, content: str, encoding: str = "utf-8") -> str:
        """Create a git blob object and return its SHA.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        content:
            File content as a string (UTF-8 or base64 encoded).
        encoding:
            ``"utf-8"`` (default) or ``"base64"``.
        """
        url = f"{_GITHUB_API}/repos/{repo}/git/blobs"
        result = self._request("POST", url, {"content": content, "encoding": encoding})
        return result["sha"]

    def _create_tree(
        self,
        repo: str,
        tree_items: list[dict[str, Any]],
        base_tree_sha: str = "",
    ) -> str:
        """Create a git tree object and return its SHA.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        tree_items:
            List of tree entries, each with ``path``, ``mode``, ``type``,
            and either ``sha`` (blob SHA) or ``content`` (inline content).
        base_tree_sha:
            SHA of the tree to build on top of.  Pass an empty string to
            create a standalone root tree (rarely needed — usually the
            current commit tree SHA should be passed here).
        """
        url = f"{_GITHUB_API}/repos/{repo}/git/trees"
        payload: dict[str, Any] = {"tree": tree_items}
        if base_tree_sha:
            payload["base_tree"] = base_tree_sha
        result = self._request("POST", url, payload)
        return result["sha"]

    def _create_commit(
        self,
        repo: str,
        message: str,
        tree_sha: str,
        parent_shas: list[str],
    ) -> str:
        """Create a git commit object and return its SHA.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        message:
            Commit message string.
        tree_sha:
            SHA of the root tree for this commit (from :meth:`_create_tree`).
        parent_shas:
            List of parent commit SHAs (typically one — the current HEAD).
        """
        url = f"{_GITHUB_API}/repos/{repo}/git/commits"
        result = self._request(
            "POST",
            url,
            {
                "message": message,
                "tree": tree_sha,
                "parents": parent_shas,
            },
        )
        return result["sha"]

    def _update_ref(self, repo: str, ref: str, sha: str, force: bool = False) -> dict[str, Any]:
        """Update (fast-forward) a git reference to a new commit SHA.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        ref:
            Full ref name, e.g. ``"refs/heads/0D_base_"``.  A bare branch
            name is accepted and will be normalised to ``refs/heads/<name>``.
        sha:
            New target commit SHA.
        force:
            When ``True``, perform a force-update (non-fast-forward).
        """
        if not ref.startswith("refs/"):
            ref = f"refs/heads/{ref}"
        url = f"{_GITHUB_API}/repos/{repo}/git/refs/{ref.removeprefix('refs/')}"
        return self._request("PATCH", url, {"sha": sha, "force": force})

    def _get_ref_sha(self, repo: str, ref: str) -> str:
        """Resolve a branch ref to the current tip commit SHA.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        ref:
            Branch name or full ref (e.g. ``"main"`` or
            ``"refs/heads/main"``).
        """
        branch = ref.removeprefix("refs/heads/")
        url = f"{_GITHUB_API}/repos/{repo}/git/refs/heads/{branch}"
        result_get = self._get(url)
        return result_get["object"]["sha"]

    def _get_commit_tree_sha(self, repo: str, commit_sha: str) -> str:
        """Return the tree SHA for a given commit SHA."""
        url = f"{_GITHUB_API}/repos/{repo}/git/commits/{commit_sha}"
        result = self._get(url)
        return result["tree"]["sha"]

    def commit_files(
        self,
        repo: str,
        branch: str,
        files: dict[str, str],
        message: str,
        force: bool = False,
    ) -> str:
        """Push one or more file changes as a single commit via the Git Data API.

        IMP-002: Closes the "agent can only push via ``report_progress``"
        constraint.  Uses the low-level Git Data API
        (blobs → trees → commits → PATCH refs) to create a commit
        entirely through HTTPS REST calls, without requiring a local
        ``git clone`` or ``git push``.

        Requires the token to have ``contents: write`` scope.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format, e.g. ``"Aries-Serpent/_codex_"``.
        branch:
            Target branch name (e.g. ``"0D_base_"``).  The branch must
            already exist.
        files:
            Mapping of file paths (repo-relative, e.g.
            ``"src/codex/foo.py"``) to their new UTF-8 string content.
        message:
            Commit message.
        force:
            When ``True``, force-update the branch ref even for
            non-fast-forward situations.  Use with caution.

        Returns
        -------
        str
            The SHA of the new commit.

        Raises
        ------
        RuntimeError
            If no token is available.
        urllib.error.HTTPError
            On GitHub API errors (e.g. 422 branch not found, 409 conflict).

        Examples
        --------
        >>> poster = GitHubMCPPoster()
        >>> sha = poster.commit_files(
        ...     repo="Aries-Serpent/_codex_",
        ...     branch="0D_base_",
        ...     files={"README.md": "# Updated\\n"},
        ...     message="docs: update README",
        ... )
        """
        self._require_token()

        # 1. Resolve the current tip of the target branch.
        head_sha = self._get_ref_sha(repo, branch)
        base_tree_sha = self._get_commit_tree_sha(repo, head_sha)

        # 2. Create a blob for each changed file.
        tree_items: list[dict[str, Any]] = []
        for path, content in files.items():
            blob_sha = self._create_blob(repo, content, encoding="utf-8")
            tree_items.append(
                {
                    "path": path,
                    "mode": "100644",  # regular file
                    "type": "blob",
                    "sha": blob_sha,
                }
            )

        # 3. Create a new tree that layers the changed files on top of the
        #    existing tree.
        new_tree_sha = self._create_tree(repo, tree_items, base_tree_sha=base_tree_sha)

        # 4. Create the commit object.
        commit_sha = self._create_commit(repo, message, new_tree_sha, [head_sha])

        # 5. Fast-forward the branch ref to the new commit.
        self._update_ref(repo, branch, commit_sha, force=force)

        self._record_cb_pattern(
            "CB-commit-files",
            f"commit_files: {len(files)} file(s) to {branch!r} as {commit_sha[:8]}",
            {
                "repo": repo,
                "branch": branch,
                "file_count": len(files),
                "sha": commit_sha,
            },
        )
        logger.info(
            "commit_files: pushed %d file(s) to %s/%s as %s",
            len(files),
            repo,
            branch,
            commit_sha[:8],
        )
        return commit_sha

    # ------------------------------------------------------------------
    # Cognitive brain lifecycle hooks (IMP-012 — S175)
    # ------------------------------------------------------------------

    def _record_cb_pattern(
        self,
        pattern_id: str,
        decision: str,
        context: dict[str, Any],
        outcome: str = "success",
    ) -> None:
        """Record a lifecycle event as a cognitive-brain memory pattern.

        Emits a structured log entry (always) and optionally stores the
        pattern in the SQLite cognitive-brain memory when the
        ``cognitive_brain`` package is available (fail-open — any import
        or write error is logged at DEBUG and silently ignored).

        Parameters
        ----------
        pattern_id:
            Short identifier, e.g. ``"CB-branch-create"``.
        decision:
            Human-readable description of the action taken.
        context:
            Arbitrary key/value pairs describing the operation context.
        outcome:
            Outcome string, one of ``"success"``, ``"error"``, or
            ``"already_exists"`` (used as the ``success_rate`` signal).
        """
        success_rate = 1.0 if outcome == "success" else 0.0
        logger.info(
            "CB lifecycle: %s | %s | outcome=%s | %s",
            pattern_id,
            decision,
            outcome,
            context,
        )
        try:
            from cognitive_brain.quantum.memory import MemoryPattern, SQLiteMemory  # noqa: PGH003

            features: dict[str, float] = {
                "success": success_rate,
                "has_repo": float(bool(context.get("repo"))),
                "has_sha": float(bool(context.get("sha"))),
                "has_pr_number": float(bool(context.get("pr_number"))),
            }
            pattern = MemoryPattern(
                pattern_id=pattern_id,
                features=features,
                decision=decision,
                confidence=0.9,
                success_rate=success_rate,
            )
            mem = SQLiteMemory()
            mem.store_pattern(pattern)
            logger.debug("CB pattern stored: %s", pattern_id)
        except Exception as _cb_exc:  # noqa: BLE001 — fail-open
            logger.debug(
                "CB pattern storage skipped (%s: %s)",
                type(_cb_exc).__name__,
                _cb_exc,
            )

    def retrieve_cb_patterns(
        self,
        limit: int = 10,
        pattern_prefix: str = "CB-",
    ) -> str:
        """Retrieve recent cognitive-brain patterns for session context injection (IMP-013).

        Queries the SQLite cognitive-brain memory for the most recent patterns
        whose ``pattern_id`` starts with *pattern_prefix*.  Returns a
        Markdown-formatted block suitable for injection into a
        ``@copilot continue`` comment body.

        Fail-open: if ``cognitive_brain`` is not importable (e.g. in CI
        without the package) or the database is empty, returns an empty
        string so callers can concatenate without conditional logic.

        Parameters
        ----------
        limit:
            Maximum number of patterns to return (default 10).
        pattern_prefix:
            Only return patterns whose ``pattern_id`` starts with this
            prefix (default ``"CB-"``).

        Returns
        -------
        str
            Markdown block of recent CB patterns, or ``""`` on failure/empty.
        """
        try:
            from cognitive_brain.quantum.memory import SQLiteMemory  # noqa: PGH003

            mem = SQLiteMemory()
            all_patterns = mem.get_recent_patterns(limit=limit * 4)
            patterns = [
                p for p in all_patterns if getattr(p, "pattern_id", "").startswith(pattern_prefix)
            ][:limit]

            if not patterns:
                return ""

            lines = [
                "### 🧠 Recent Cognitive-Brain Patterns",
                "",
                "| Pattern | Decision | Outcome |",
                "|---------|----------|---------|",
            ]
            for p in patterns:
                pid = getattr(p, "pattern_id", "unknown")
                dec = getattr(p, "decision", "")[:60]
                sr = getattr(p, "success_rate", None)
                outcome = (
                    "✅ success" if sr == 1.0 else ("⚠️ partial" if sr and sr > 0 else "❌ fail")
                )
                lines.append(f"| `{pid}` | {dec} | {outcome} |")

            return "\n".join(lines) + "\n"

        except Exception as _exc:  # noqa: BLE001 — fail-open
            logger.debug("CB pattern retrieval skipped (%s: %s)", type(_exc).__name__, _exc)
            return ""

    def _require_token(self) -> None:
        """Raise RuntimeError if no token is available.

        Requires the token to have ``contents: write`` scope.
        """
        if not self._token:
            raise RuntimeError(
                "No GitHub token available. Set CODEX_MASTER_KEY. "
                "See .codex/docs/ADMIN_MANUAL_SETUP_GUIDE.md § 3."
            )

    def _get(self, url: str) -> dict[str, Any]:
        """Execute a single GET request to the GitHub REST API (no retry).

        Use :meth:`_request` with ``method="GET"`` when retry-on-rate-limit is
        needed.  This lightweight helper is used by the Git Data API helpers
        (:meth:`_get_ref_sha`, :meth:`_get_commit_tree_sha`) where a single
        attempt is sufficient.
        """
        if not url.startswith("https://"):
            raise ValueError(f"URL scheme must be https: {url}")
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": _ACCEPT,
                "X-GitHub-Api-Version": _API_VERSION,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode(errors="replace")
            logger.error("GitHub API GET %s → %d: %s", url, exc.code, error_body)
            raise

    def _request(
        self,
        method: str,
        url: str,
        payload: dict[str, Any],
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Execute a GitHub REST API call with exponential back-off retry.

        Retries on HTTP 403 (secondary rate limit) and 429 (primary rate
        limit).  Respects the ``Retry-After`` response header when present.
        Non-retryable errors (4xx other than 403/429, 5xx) are raised
        immediately after logging.

        Parameters
        ----------
        method:
            HTTP method string, e.g. ``"POST"`` or ``"PATCH"``.
        url:
            Fully-qualified HTTPS URL.
        payload:
            Request body as a JSON-serialisable dict.
        max_retries:
            Maximum number of retry attempts after the first failure
            (default 3, giving up to 4 total attempts).
        """
        if not url.startswith("https://"):
            raise ValueError(f"URL scheme must be https: {url}")
        data = json.dumps(payload).encode()
        last_exc: urllib.error.HTTPError | None = None
        for attempt in range(max_retries + 1):
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
                with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
                    body = resp.read()
                    return json.loads(body) if body else {}
            except urllib.error.HTTPError as exc:
                last_exc = exc
                # Only retry on rate-limiting, not on real permission/auth errors.
                # 429 (primary rate limit) — always retryable.
                # 403 (secondary rate limit) — retryable only when GitHub signals
                #   throttling via a Retry-After header or x-ratelimit-remaining=0.
                is_rate_limited = False
                if exc.code == 429:
                    is_rate_limited = True
                elif exc.code == 403:
                    retry_after_hdr = exc.headers.get("Retry-After", "")
                    remaining = exc.headers.get("x-ratelimit-remaining", "")
                    is_rate_limited = bool(retry_after_hdr) or remaining == "0"

                if is_rate_limited and attempt < max_retries:
                    retry_after_hdr = exc.headers.get("Retry-After", "")
                    try:
                        wait = float(retry_after_hdr)
                    except (TypeError, ValueError):
                        wait = (2**attempt) * 1.0  # 1s, 2s, 4s …
                    logger.warning(
                        "GitHub API rate-limited (%d). Retrying in %.0fs (attempt %d/%d)…",
                        exc.code,
                        wait,
                        attempt + 1,
                        max_retries,
                    )
                    time.sleep(wait)
                else:
                    error_body = exc.read().decode(errors="replace")
                    logger.error("GitHub API %s %s → %d: %s", method, url, exc.code, error_body)
                    raise
        # Should be unreachable, but satisfy type checker
        raise last_exc  # type: ignore[misc]

    def _graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        url = f"{_GITHUB_API}/graphql"
        return self._request("POST", url, {"query": query, "variables": variables})

    def _graphql_with_retry(
        self,
        query: str,
        variables: dict[str, Any],
        *,
        max_retries: int = 3,
        operation_name: str = "GraphQL",
    ) -> dict[str, Any]:
        """Execute a GraphQL mutation/query with exponential back-off retry.

        Hardened posting pipeline (Phase 8 P6):
        - Detects GraphQL ``errors`` array in the response body and raises.
        - Recognises ``RATE_LIMITED`` errors from GitHub and waits/retries.
        - Retries on transient network errors (``urllib.error.URLError``,
          ``http.client.RemoteDisconnected``, ``TimeoutError``).
        - Non-retryable errors (``FORBIDDEN``, ``NOT_FOUND``, auth failures)
          are raised immediately.
        - Returns ``result["data"]`` on success (unwraps the envelope).

        Returns:
            The full parsed JSON response dict (including ``data`` key) so
            callers can continue to use the same access pattern.
        """
        _NON_RETRYABLE_TYPES = frozenset({"FORBIDDEN", "NOT_FOUND", "UNPROCESSABLE", "BAD_REQUEST"})
        _RETRYABLE_TYPES = frozenset({"RATE_LIMITED", "SERVICE_UNAVAILABLE", "INTERNAL"})

        last_exc: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                url = f"{_GITHUB_API}/graphql"
                result = self._request("POST", url, {"query": query, "variables": variables})

                # Check for GraphQL-level errors (HTTP 200 but errors in body)
                gql_errors = result.get("errors")
                if gql_errors:
                    first = gql_errors[0]
                    err_type = first.get("type", "UNKNOWN")
                    err_msg = first.get("message", str(gql_errors))

                    if err_type in _NON_RETRYABLE_TYPES:
                        raise ValueError(f"{operation_name} GraphQL {err_type}: {err_msg}")

                    if err_type in _RETRYABLE_TYPES and attempt < max_retries:
                        wait = 2 ** (attempt + 1)
                        print(
                            f"[mcp_poster] {operation_name} GraphQL {err_type} "
                            f"(attempt {attempt + 1}/{max_retries + 1}) — retry in {wait}s",
                            file=sys.stderr,
                        )
                        time.sleep(wait)
                        continue

                    # Unknown error type or retries exhausted
                    raise RuntimeError(f"{operation_name} GraphQL error ({err_type}): {err_msg}")

                return result

            except (urllib.error.URLError, TimeoutError, ConnectionResetError) as exc:
                last_exc = exc
                if attempt < max_retries:
                    wait = 2 ** (attempt + 1)
                    print(
                        f"[mcp_poster] {operation_name} network error "
                        f"(attempt {attempt + 1}/{max_retries + 1}) — retry in {wait}s: {exc}",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                else:
                    raise

        # Should never reach here but satisfy type checker
        if last_exc is not None:
            raise last_exc
        raise RuntimeError(f"{operation_name}: max retries ({max_retries}) exceeded")

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
        result = self._graphql_with_retry(
            query, {"owner": owner, "repo": repo}, operation_name="ResolveDiscussionIds"
        )
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
            # Fall back to first available category when slug not matched.
            fallback = categories[0]
            fallback_slug = fallback.get("slug") or fallback.get("name", "?")
            logger.warning(
                "Discussion category %r not found in %r; falling back to %r.",
                category_slug,
                f"{owner}/{repo}",
                fallback_slug,
            )
            category_id = fallback["id"]
        return repo_id, category_id


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m codex.github.mcp_poster",
        description=(
            "Post GitHub PR comments and Discussions, create branches, "
            "and open PRs using CODEX_MASTER_KEY."
        ),
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

    # add-discussion-comment
    adc = sub.add_parser(
        "add-discussion-comment",
        help="Add a comment to an existing GitHub Discussion",
    )
    adc.add_argument("--repo", required=True, help="owner/repo")
    adc.add_argument("--number", required=True, type=int, help="Discussion number")
    adc_group = adc.add_mutually_exclusive_group(required=True)
    adc_group.add_argument("--body", help="Comment body string")
    adc_group.add_argument("--body-file", help="Path to markdown file")

    # upsert-discussion-comment
    udc = sub.add_parser(
        "upsert-discussion-comment",
        help="Add or update a Discussion comment identified by a unique marker string",
    )
    udc.add_argument("--repo", required=True, help="owner/repo")
    udc.add_argument("--number", required=True, type=int, help="Discussion number")
    udc_group = udc.add_mutually_exclusive_group(required=True)
    udc_group.add_argument("--body", help="Comment body string")
    udc_group.add_argument("--body-file", help="Path to markdown file")
    udc.add_argument(
        "--marker",
        default="",
        help="Unique HTML comment marker used to detect an existing comment to update",
    )

    # post-ci-pattern-summary
    pcps = sub.add_parser(
        "post-ci-pattern-summary",
        help="Post (or update) CI pattern knowledge-graph summary to a Discussion",
    )
    pcps.add_argument("--repo", required=True, help="owner/repo")
    pcps.add_argument("--number", required=True, type=int, help="Discussion number")
    pcps.add_argument("--body-file", required=True, help="Path to markdown summary file")
    pcps.add_argument(
        "--session-id",
        default="",
        help="Session ID for deduplication marker (optional)",
    )

    # post-continuation
    pct = sub.add_parser(
        "post-continuation",
        help="Post a tokenized continuation chain prompt as a new Discussion comment",
    )
    pct.add_argument("--repo", required=True, help="owner/repo")
    pct.add_argument("--number", required=True, type=int, help="Discussion number")
    pct_group = pct.add_mutually_exclusive_group(required=True)
    pct_group.add_argument("--body", help="Continuation chain body string")
    pct_group.add_argument("--body-file", help="Path to markdown file")

    # create-discussion
    cd = sub.add_parser("create-discussion", help="Create a GitHub Discussion")
    cd.add_argument("--repo", required=True)
    cd.add_argument("--title", required=True)
    cd.add_argument("--body-file", required=True)
    cd.add_argument("--category", default="cognitive-brain-patterns")

    # update-discussion
    ud = sub.add_parser("update-discussion", help="Update title/body/category of a Discussion")
    ud.add_argument("--repo", required=True, help="owner/repo")
    ud.add_argument("--number", required=True, type=int, help="Discussion number")
    ud.add_argument("--title", default=None, help="New title (optional)")
    ud.add_argument("--body-file", default=None, help="Path to file containing new body (optional)")
    ud.add_argument("--category", default=None, help="New category slug (optional)")

    # lock-discussion
    ld = sub.add_parser("lock-discussion", help="Lock a Discussion")
    ld.add_argument("--repo", required=True, help="owner/repo")
    ld.add_argument("--number", required=True, type=int, help="Discussion number")
    ld.add_argument(
        "--reason",
        default="RESOLVED",
        choices=["OFF_TOPIC", "RESOLVED", "SPAM", "TOO_HEATED"],
        help="Lock reason",
    )

    # unlock-discussion
    uld = sub.add_parser("unlock-discussion", help="Unlock a Discussion")
    uld.add_argument("--repo", required=True, help="owner/repo")
    uld.add_argument("--number", required=True, type=int, help="Discussion number")

    # delete-discussion
    dld = sub.add_parser("delete-discussion", help="Permanently delete a Discussion")
    dld.add_argument("--repo", required=True, help="owner/repo")
    dld.add_argument("--number", required=True, type=int, help="Discussion number")

    # delete-discussion-comment
    ddc = sub.add_parser("delete-discussion-comment", help="Delete a Discussion comment by node ID")
    ddc.add_argument("--comment-id", required=True, help="GraphQL node ID of the comment")

    # mark-answer
    ma = sub.add_parser("mark-answer", help="Mark a Discussion comment as the accepted answer")
    ma.add_argument("--comment-id", required=True, help="GraphQL node ID of the comment")

    # unmark-answer
    uma = sub.add_parser("unmark-answer", help="Unmark a Discussion comment as the accepted answer")
    uma.add_argument("--comment-id", required=True, help="GraphQL node ID of the comment")

    # list-discussions
    lsd = sub.add_parser("list-discussions", help="List Discussions in a repository")
    lsd.add_argument("--repo", required=True, help="owner/repo")
    lsd.add_argument("--category", default=None, help="Filter by category slug (optional)")
    lsd.add_argument("--first", type=int, default=20, help="Max number to return (default 20)")
    lsd.add_argument(
        "--after",
        default=None,
        help="Pagination cursor (endCursor from previous page)",
    )
    lsd.add_argument("--json", action="store_true", help="Output as JSON")

    # get-discussion
    gd = sub.add_parser("get-discussion", help="Get a single Discussion with its comments")
    gd.add_argument("--repo", required=True, help="owner/repo")
    gd.add_argument("--number", required=True, type=int, help="Discussion number")
    gd.add_argument("--comments-first", type=int, default=50, help="Comments per page (default 50)")
    gd.add_argument("--comments-after", default=None, help="Pagination cursor for comments")
    gd.add_argument("--json", action="store_true", help="Output as JSON")

    # list-discussion-categories
    ldc = sub.add_parser("list-discussion-categories", help="List all Discussion categories")
    ldc.add_argument("--repo", required=True, help="owner/repo")
    ldc.add_argument("--json", action="store_true", help="Output as JSON")

    # pin-discussion / unpin-discussion
    pd = sub.add_parser("pin-discussion", help="Pin a Discussion to the repository")
    pd.add_argument("--repo", required=True, help="owner/repo")
    pd.add_argument("--number", required=True, type=int, help="Discussion number")

    upd = sub.add_parser("unpin-discussion", help="Unpin a Discussion from the repository")
    upd.add_argument("--repo", required=True, help="owner/repo")
    upd.add_argument("--number", required=True, type=int, help="Discussion number")

    # create-branch  (IMP-001 / IMP-010 — S174)
    cb = sub.add_parser(
        "create-branch",
        help="Create a branch ref on GitHub (requires contents:write token)",
    )
    cb.add_argument("--repo", required=True, help="owner/repo")
    cb.add_argument(
        "--ref",
        required=True,
        help="Full ref name, e.g. refs/heads/0D_base_ (heads/ prefix added if omitted)",
    )
    cb.add_argument("--sha", required=True, help="40-char commit SHA to point the new ref to")

    # create-pr  (IMP-001 / IMP-010 — S174)
    cpr = sub.add_parser(
        "create-pr",
        help="Open a pull request (requires pull-requests:write token)",
    )
    cpr.add_argument("--repo", required=True, help="owner/repo")
    cpr.add_argument("--title", required=True)
    cpr.add_argument("--body", default="", help="PR description markdown (or use --body-file)")
    cpr.add_argument("--body-file", default="", help="Path to markdown file for PR body")
    cpr.add_argument("--head", required=True, help="Head (source) branch name")
    cpr.add_argument("--base", default="main", help="Base (target) branch name (default: main)")
    cpr.add_argument("--draft", action="store_true", help="Open as draft PR")

    # merge-branch  (IMP-001 / IMP-010 — S174)
    mb = sub.add_parser(
        "merge-branch",
        help="Server-side branch merge via GitHub API (requires contents:write token)",
    )
    mb.add_argument("--repo", required=True, help="owner/repo")
    mb.add_argument("--base", required=True, help="Target branch to merge into")
    mb.add_argument("--head", required=True, help="Source branch or SHA to merge from")
    mb.add_argument("--message", default="", help="Optional merge commit message")

    # retrieve-patterns  (IMP-013 — S175)
    rp = sub.add_parser(
        "retrieve-patterns",
        help="Print recent cognitive-brain patterns as Markdown (IMP-013)",
    )
    rp.add_argument("--limit", type=int, default=10, help="Maximum patterns to return (default 10)")
    rp.add_argument(
        "--prefix",
        default="CB-",
        help="Filter patterns by pattern_id prefix (default: CB-)",
    )

    # commit-files  (IMP-002 — S178)
    cf = sub.add_parser(
        "commit-files",
        help="Push file changes as a single commit via Git Data API (IMP-002)",
    )
    cf.add_argument("--repo", required=True, help="owner/repo")
    cf.add_argument("--branch", required=True, help="Target branch name")
    cf.add_argument("--message", required=True, help="Commit message")
    cf.add_argument(
        "--file",
        dest="files",
        action="append",
        metavar="DEST:SRC",
        required=True,
        help=(
            "File mapping in DEST:SRC format where DEST is the repo-relative "
            "path and SRC is the local file path to read content from. "
            "Repeat for multiple files."
        ),
    )
    cf.add_argument("--force", action="store_true", default=False, help="Force-update ref")

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
            poster.set_repo_variable(args.repo, args.name, args.value)
            print(f"✅ Variable set: {args.name}={args.value}")

        elif args.command == "create-discussion":
            body = Path(args.body_file).read_text()
            result = poster.create_discussion(args.repo, args.title, body, args.category)
            print(f"✅ Discussion created: {result.get('url', result)}")

        elif args.command == "update-discussion":
            body = Path(args.body_file).read_text() if args.body_file else None
            result = poster.update_discussion(
                args.repo, args.number, title=args.title, body=body, category_slug=args.category
            )
            print(f"✅ Discussion #{args.number} updated: {result.get('url', result)}")

        elif args.command == "lock-discussion":
            poster.lock_discussion(args.repo, args.number, args.reason)
            print(f"✅ Discussion #{args.number} locked ({args.reason})")

        elif args.command == "unlock-discussion":
            poster.unlock_discussion(args.repo, args.number)
            print(f"✅ Discussion #{args.number} unlocked")

        elif args.command == "delete-discussion":
            ok = poster.delete_discussion(args.repo, args.number)
            if ok:
                print(f"✅ Discussion #{args.number} deleted")
            else:
                print(f"❌ Failed to delete Discussion #{args.number}", file=sys.stderr)
                return 1

        elif args.command == "delete-discussion-comment":
            ok = poster.delete_discussion_comment(args.comment_id)
            if ok:
                print(f"✅ Comment {args.comment_id} deleted")
            else:
                print(f"❌ Failed to delete comment {args.comment_id}", file=sys.stderr)
                return 1

        elif args.command == "mark-answer":
            result = poster.mark_answer(args.comment_id)
            num = result.get("number", "?")
            print(f"✅ Comment {args.comment_id} marked as answer on discussion #{num}")

        elif args.command == "unmark-answer":
            result = poster.unmark_answer(args.comment_id)
            num = result.get("number", "?")
            print(f"✅ Comment {args.comment_id} unmarked as answer on discussion #{num}")

        elif args.command == "list-discussions":
            page = poster.list_discussions(args.repo, args.category, args.first, args.after)
            discussions = page["nodes"]
            page_info = page["pageInfo"]
            if getattr(args, "json", False):
                import json as _json

                print(_json.dumps(page, indent=2))
            else:
                for d in discussions:
                    cat = d.get("category", {}).get("slug", "?")
                    answered = "✅" if d.get("isAnswered") else "  "
                    print(f"#{d['number']:5}  {answered}  [{cat}]  {d['title'][:70]}")
                print(f"\n{len(discussions)} discussion(s) found")
                if page_info.get("hasNextPage"):
                    print(f"Next page cursor: {page_info['endCursor']}")
                    print("  (use --after <cursor> to fetch next page)")

        elif args.command == "get-discussion":
            disc = poster.get_discussion(
                args.repo,
                args.number,
                comments_first=args.comments_first,
                comments_after=args.comments_after,
            )
            if getattr(args, "json", False):
                import json as _json

                print(_json.dumps(disc, indent=2))
            else:
                print(f"## Discussion #{disc['number']}: {disc['title']}")
                print(f"   URL: {disc['url']}")
                print(f"   Category: {disc.get('category', {}).get('name', '?')}")
                print(
                    f"   Answered: {disc.get('isAnswered', False)}"
                    f"  |  Locked: {disc.get('isLocked', False)}"
                )
                print(f"   Comments: {disc.get('comments', {}).get('totalCount', 0)}")
                comments_page_info = disc.get("comments", {}).get("pageInfo", {})
                if comments_page_info.get("hasNextPage"):
                    print(f"   Next comments cursor: {comments_page_info['endCursor']}")
                    print("   (use --comments-after <cursor> to fetch next page)")

        elif args.command == "list-discussion-categories":
            cats = poster.list_discussion_categories(args.repo)
            if getattr(args, "json", False):
                import json as _json

                print(_json.dumps(cats, indent=2))
            else:
                print(f"{'Slug':35}  {'Name':30}  Answerable")
                print("-" * 75)
                for c in cats:
                    slug = c.get("slug", "")
                    name = c.get("name", "")
                    answerable = c.get("isAnswerable", False)
                    print(f"{slug:35}  {name:30}  {answerable}")
                print(f"\n{len(cats)} category/categories")

        elif args.command == "create-branch":
            result = poster.create_ref(args.repo, args.ref, args.sha)
            print(f"✅ Branch created: {result.get('ref', args.ref)} @ {args.sha[:8]}")

        elif args.command == "pin-discussion":
            result = poster.pin_discussion(args.repo, args.number)
            num = result.get("number", args.number)
            print(f"✅ Discussion #{num} pinned in {args.repo}")

        elif args.command == "unpin-discussion":
            result = poster.unpin_discussion(args.repo, args.number)
            num = result.get("number", args.number)
            print(f"✅ Discussion #{num} unpinned in {args.repo}")

        elif args.command == "create-pr":
            body = args.body
            if not body and args.body_file:
                body = Path(args.body_file).read_text()
            result = poster.create_pull_request(
                args.repo, args.title, body, args.head, args.base, args.draft
            )
            print(f"✅ PR #{result.get('number')} opened: {result.get('html_url', result)}")

        elif args.command == "merge-branch":
            result = poster.merge_branch(args.repo, args.base, args.head, args.message)
            if result:
                sha = result.get("sha", "")
                print(f"✅ Merged {args.head} → {args.base}: {sha[:8] if sha else 'up-to-date'}")
            else:
                print(f"✅ {args.head} already up-to-date with {args.base} — no merge needed")

        elif args.command == "retrieve-patterns":
            md = poster.retrieve_cb_patterns(limit=args.limit, pattern_prefix=args.prefix)
            if md:
                print(md)
            else:
                print("ℹ️  No cognitive-brain patterns found (CB package unavailable or DB empty).")

        elif args.command == "commit-files":
            files: dict[str, str] = {}
            for mapping in args.files:
                dest, _, src = mapping.partition(":")
                if not dest or not src:
                    print(
                        f"❌ Invalid --file mapping {mapping!r} — expected DEST:SRC",
                        file=sys.stderr,
                    )  # noqa: E501
                    return 1
                files[dest] = Path(src).read_text(encoding="utf-8")
            commit_sha = poster.commit_files(
                args.repo, args.branch, files, args.message, args.force
            )  # noqa: E501
            print(f"✅ Committed {len(files)} file(s) to {args.branch}: {commit_sha[:8]}")

        elif args.command == "add-discussion-comment":
            body = args.body or Path(args.body_file).read_text(encoding="utf-8")
            result = poster.add_discussion_comment(args.repo, args.number, body)
            print(f"✅ Discussion comment posted: {result.get('url', result)}")

        elif args.command == "upsert-discussion-comment":
            body = args.body or Path(args.body_file).read_text(encoding="utf-8")
            result = poster.upsert_discussion_comment(args.repo, args.number, body, args.marker)
            print(f"✅ Discussion comment upserted: {result.get('url', result)}")

        elif args.command == "post-ci-pattern-summary":
            body = Path(args.body_file).read_text(encoding="utf-8")
            result = poster.post_ci_pattern_summary(args.repo, args.number, body, args.session_id)
            print(
                f"✅ CI pattern summary posted to discussion #{args.number}: {result.get('url', result)}"  # noqa: E501
            )

        elif args.command == "post-continuation":
            body = args.body or Path(args.body_file).read_text(encoding="utf-8")
            result = poster.post_continuation_chain(args.repo, args.number, body)
            print(
                f"✅ Continuation chain posted to discussion #{args.number}: {result.get('url', result)}"  # noqa: E501
            )

    except RuntimeError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    except urllib.error.HTTPError as exc:
        print(f"❌ GitHub API error {exc.code}: {exc.reason}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
