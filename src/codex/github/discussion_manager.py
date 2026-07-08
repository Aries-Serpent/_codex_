"""GitHub Discussions management and operations.

Encapsulates all Discussion CRUD operations, comment management, pinning, and
category handling.
"""

from __future__ import annotations

import logging
from typing import Any

from codex.github.api_client import APIClient

logger = logging.getLogger(__name__)


class DiscussionManager:
    """GitHub Discussions management operations.

    Handles:
    - Creating and managing Discussions
    - Adding and updating comments
    - Discussion lifecycle (lock, unlock, delete)
    - Category and pinning operations
    - Detecting unread human replies
    """

    def __init__(self, api_client: APIClient) -> None:
        """Initialize with an APIClient for making requests."""
        self._api = api_client

    # Bot login names that should be filtered out when checking for unread replies
    _BOT_LOGINS: frozenset[str] = frozenset(
        {
            "github-actions[bot]",
            "copilot-swe-agent[bot]",
            "github-copilot[bot]",
            "copilot[bot]",
            "dependabot[bot]",
        }
    )

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
        self._api._require_token()
        owner, repo_name = repo.split("/", 1)

        # Step 1: resolve repository + category node IDs
        repo_id, category_id = self._api._resolve_discussion_ids(owner, repo_name, category_slug)

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
        result = self._api._graphql_with_retry(
            mutation, variables, operation_name="CreateDiscussion"
        )
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
        self._api._require_token()
        owner, repo_name = repo.split("/", 1)

        # Step 1: resolve the discussion node ID
        discussion_id = self._api._resolve_discussion_node_id(owner, repo_name, discussion_number)

        # Step 2: add comment
        mutation = """
        mutation AddDiscussionComment($discussionId: ID!, $body: String!) {
          addDiscussionComment(input: { discussionId: $discussionId, body: $body }) {
            comment { id url body }
          }
        }
        """
        result = self._api._graphql(mutation, {"discussionId": discussion_id, "body": body})
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
        self._api._require_token()
        owner, repo_name = repo.split("/", 1)

        if marker:
            existing_id = self._api._find_discussion_comment(
                owner, repo_name, discussion_number, marker
            )
            if existing_id:
                return self._api._update_discussion_comment(existing_id, body)

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
        result = self._api._graphql(
            query, {"owner": owner, "repo": repo, "number": discussion_number}
        )
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
            result = self._api._graphql(
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
        self._api._require_token()
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
            result = self._api._graphql(
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
        self._api._require_token()
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
        all_comments: list[dict[str, Any]] = []
        cursor: str | None = None
        fetched = 0
        while fetched < max_comments:
            result = self._api._graphql(
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
            if login in self._api._BOT_LOGINS:
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
                if login in self._api._BOT_LOGINS:
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
        result = self._api._graphql(mutation, {"commentId": comment_id, "body": body})
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
        self._api._require_token()
        owner, repo_name = repo.split("/", 1)
        discussion_id = self._api._resolve_discussion_node_id(owner, repo_name, discussion_number)

        variables: dict[str, Any] = {"discussionId": discussion_id}
        if title is not None:
            variables["title"] = title
        if body is not None:
            variables["body"] = body
        if category_slug is not None:
            _, category_id = self._api._resolve_discussion_ids(owner, repo_name, category_slug)
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
        result = self._api._graphql(mutation, variables)
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
        self._api._require_token()
        owner, repo_name = repo.split("/", 1)
        discussion_id = self._api._resolve_discussion_node_id(owner, repo_name, discussion_number)
        mutation = """
        mutation LockDiscussion($id: ID!, $reason: LockReason) {
          lockLockable(input: { lockableId: $id, lockReason: $reason }) {
            lockedRecord { ... on Discussion { number url } }
          }
        }
        """
        result = self._api._graphql(mutation, {"id": discussion_id, "reason": reason})
        return result.get("data", {}).get("lockLockable", result)

    def unlock_discussion(self, repo: str, discussion_number: int) -> dict[str, Any]:
        """Unlock a previously locked Discussion."""
        self._api._require_token()
        owner, repo_name = repo.split("/", 1)
        discussion_id = self._api._resolve_discussion_node_id(owner, repo_name, discussion_number)
        mutation = """
        mutation UnlockDiscussion($id: ID!) {
          unlockLockable(input: { lockableId: $id }) {
            unlockedRecord { ... on Discussion { number url } }
          }
        }
        """
        result = self._api._graphql(mutation, {"id": discussion_id})
        return result.get("data", {}).get("unlockLockable", result)

    def delete_discussion(self, repo: str, discussion_number: int) -> bool:
        """Permanently delete a Discussion.

        Returns ``True`` if deletion succeeded, ``False`` otherwise.
        Requires admin-level token with ``discussions:write`` scope.
        """
        self._api._require_token()
        owner, repo_name = repo.split("/", 1)
        discussion_id = self._api._resolve_discussion_node_id(owner, repo_name, discussion_number)
        mutation = """
        mutation DeleteDiscussion($id: ID!) {
          deleteDiscussion(input: { id: $id }) {
            clientMutationId
          }
        }
        """
        result = self._api._graphql(mutation, {"id": discussion_id})
        return "errors" not in result

    def delete_discussion_comment(self, comment_id: str) -> bool:
        """Delete a Discussion comment by its GraphQL node ID.

        Returns ``True`` if deletion succeeded, ``False`` otherwise.
        """
        self._api._require_token()
        mutation = """
        mutation DeleteDiscussionComment($id: ID!) {
          deleteDiscussionComment(input: { id: $id }) {
            clientMutationId
          }
        }
        """
        result = self._api._graphql(mutation, {"id": comment_id})
        return "errors" not in result

    def mark_answer(self, comment_id: str) -> dict[str, Any]:
        """Mark a Discussion comment as the accepted answer.

        Parameters
        ----------
        comment_id:
            GraphQL node ID of the comment (obtain from ``add_discussion_comment``
            or ``_find_discussion_comment``).
        """
        self._api._require_token()
        mutation = """
        mutation MarkAnswer($commentId: ID!) {
          markDiscussionCommentAsAnswer(input: { id: $commentId }) {
            discussion { number url }
          }
        }
        """
        result = self._api._graphql(mutation, {"commentId": comment_id})
        return (
            result.get("data", {})
            .get("markDiscussionCommentAsAnswer", {})
            .get("discussion", result)
        )

    def unmark_answer(self, comment_id: str) -> dict[str, Any]:
        """Unmark a previously accepted answer on a Discussion."""
        self._api._require_token()
        mutation = """
        mutation UnmarkAnswer($commentId: ID!) {
          unmarkDiscussionCommentAsAnswer(input: { id: $commentId }) {
            discussion { number url }
          }
        }
        """
        result = self._api._graphql(mutation, {"commentId": comment_id})
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
        self._api._require_token()
        owner, repo_name = repo.split("/", 1)

        category_id: str | None = None
        if category_slug:
            _, category_id = self._api._resolve_discussion_ids(owner, repo_name, category_slug)

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
        result = self._api._graphql(query, variables)
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
        self._api._require_token()
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
        result = self._api._graphql(
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
        self._api._require_token()
        disc = self.get_discussion(repo, discussion_number)
        discussion_id: str = disc["id"]
        mutation = """
        mutation PinDiscussion($discussionId: ID!) {
          pinDiscussion(input: { discussionId: $discussionId }) {
            discussion { id number title url }
          }
        }
        """
        result = self._api._graphql(mutation, {"discussionId": discussion_id})
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
        self._api._require_token()
        disc = self.get_discussion(repo, discussion_number)
        discussion_id: str = disc["id"]
        mutation = """
        mutation UnpinDiscussion($discussionId: ID!) {
          unpinDiscussion(input: { discussionId: $discussionId }) {
            discussion { id number title url }
          }
        }
        """
        result = self._api._graphql(mutation, {"discussionId": discussion_id})
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
        self._api._require_token()
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
        result = self._api._graphql(query, {"owner": owner, "repo": repo_name})
        return (
            result.get("data", {})
            .get("repository", {})
            .get("discussionCategories", {})
            .get("nodes", [])
        )

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
        result = self._api._graphql_with_retry(
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
