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
import logging
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from codex.github.api_client import APIClient
from codex.github.cognitive_brain_integration import CognitiveBrainIntegration
from codex.github.discussion_manager import DiscussionManager
from codex.github.git_operations import GitOperations
from codex.github.pull_request_manager import PullRequestManager

logger = logging.getLogger(__name__)


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

    **Note:** This class delegates to specialized modules (APIClient, DiscussionManager,
    PullRequestManager, GitOperations, CognitiveBrainIntegration) for specific operations.
    The public API remains unchanged for backward compatibility.
    """

    def __init__(self, token: str | None = None) -> None:
        """Initialize the MCP poster with all specialized managers.

        Parameters
        ----------
        token:
            Optional explicit token. If None, resolves from environment.
        """
        # Initialize the base API client
        self._api = APIClient(token)

        # Initialize all specialized managers
        self._discussions = DiscussionManager(self._api)
        self._prs = PullRequestManager(self._api)
        self._git = GitOperations(self._api)
        self._cb = CognitiveBrainIntegration(self._api)

        # Expose token source for compatibility
        self._token_source = self._api._token_source

    @property
    def _token(self) -> str:
        """Backward compatibility: expose token from APIClient."""
        return self._api._token

    # ------------------------------------------------------------------
    # Token health check (delegates to APIClient)
    # ------------------------------------------------------------------

    def check_token_health(self) -> dict[str, object]:
        """Check GitHub token health and scopes. See APIClient.check_token_health()."""
        return self._api.check_token_health()

    # ------------------------------------------------------------------
    # PR comments (delegates to PullRequestManager)
    # ------------------------------------------------------------------

    def post_pr_comment(self, repo: str, pr_number: int, body: str) -> dict[str, Any]:
        """Post a comment on a PR. See PullRequestManager.post_pr_comment()."""
        return self._prs.post_pr_comment(repo, pr_number, body)

    def post_pr_comment_from_file(
        self, repo: str, pr_number: int, body_file: str | Path
    ) -> dict[str, Any]:
        """Read a file and post as a PR comment. See PullRequestManager.post_pr_comment_from_file()."""
        return self._prs.post_pr_comment_from_file(repo, pr_number, body_file)

    # ------------------------------------------------------------------
    # GitHub Discussions (delegates to DiscussionManager)
    # ------------------------------------------------------------------

    def create_discussion(
        self,
        repo: str,
        title: str,
        body: str,
        category_slug: str = "cognitive-brain-patterns",
    ) -> dict[str, Any]:
        """Create a GitHub Discussion. See DiscussionManager.create_discussion()."""
        return self._discussions.create_discussion(repo, title, body, category_slug)

    def post_session_summary_discussion(
        self, repo: str, session_num: int, summary_md: str
    ) -> dict[str, Any]:
        """Post a session summary as a Discussion. See DiscussionManager.post_session_summary_discussion()."""
        return self._discussions.post_session_summary_discussion(repo, session_num, summary_md)

    def add_discussion_comment(
        self, repo: str, discussion_number: int, body: str
    ) -> dict[str, Any]:
        """Add a comment to a Discussion. See DiscussionManager.add_discussion_comment()."""
        return self._discussions.add_discussion_comment(repo, discussion_number, body)

    def upsert_discussion_comment(
        self, repo: str, discussion_number: int, body: str, marker: str = ""
    ) -> dict[str, Any]:
        """Add or update a Discussion comment. See DiscussionManager.upsert_discussion_comment()."""
        return self._discussions.upsert_discussion_comment(repo, discussion_number, body, marker)

    def post_ci_pattern_summary(
        self, repo: str, discussion_number: int, summary_md: str, session_id: str = ""
    ) -> dict[str, Any]:
        """Post a CI pattern summary to a Discussion.

        Uses upsert_discussion_comment to replace previous summary.
        """
        marker = (
            f"<!-- ci-pattern-summary:{session_id} -->"
            if session_id
            else "<!-- ci-pattern-summary -->"
        )
        full_body = f"{marker}\n{summary_md}"
        return self.upsert_discussion_comment(repo, discussion_number, full_body, marker)

    def post_continuation_chain(
        self, repo: str, discussion_number: int, chain_md: str
    ) -> dict[str, Any]:
        """Post a continuation chain as a Discussion comment."""
        return self.add_discussion_comment(repo, discussion_number, chain_md)

    def find_or_create_pr_discussion(
        self,
        repo: str,
        pr_number: int,
        purpose: str,
        category_slug: str = "show-and-tell",
    ) -> tuple[int, str]:
        """Find or create a per-PR Discussion. See DiscussionManager.find_or_create_pr_discussion()."""
        return self._discussions.find_or_create_pr_discussion(
            repo, pr_number, purpose, category_slug
        )

    def check_discussion_replies(
        self,
        repo: str,
        discussion_number: int,
        since_marker: str = "",
        max_comments: int = 200,
    ) -> list[dict[str, Any]]:
        """Check for unread human replies in a Discussion. See DiscussionManager.check_discussion_replies()."""
        return self._discussions.check_discussion_replies(
            repo, discussion_number, since_marker, max_comments
        )

    def update_discussion(
        self,
        repo: str,
        discussion_number: int,
        *,
        title: str | None = None,
        body: str | None = None,
        category_slug: str | None = None,
    ) -> dict[str, Any]:
        """Update a Discussion. See DiscussionManager.update_discussion()."""
        return self._discussions.update_discussion(
            repo, discussion_number, title=title, body=body, category_slug=category_slug
        )

    def lock_discussion(
        self, repo: str, discussion_number: int, reason: str = "RESOLVED"
    ) -> dict[str, Any]:
        """Lock a Discussion. See DiscussionManager.lock_discussion()."""
        return self._discussions.lock_discussion(repo, discussion_number, reason)

    def unlock_discussion(self, repo: str, discussion_number: int) -> dict[str, Any]:
        """Unlock a Discussion. See DiscussionManager.unlock_discussion()."""
        return self._discussions.unlock_discussion(repo, discussion_number)

    def delete_discussion(self, repo: str, discussion_number: int) -> bool:
        """Delete a Discussion. See DiscussionManager.delete_discussion()."""
        return self._discussions.delete_discussion(repo, discussion_number)

    def delete_discussion_comment(self, comment_id: str) -> bool:
        """Delete a Discussion comment. See DiscussionManager.delete_discussion_comment()."""
        return self._discussions.delete_discussion_comment(comment_id)

    def mark_answer(self, comment_id: str) -> dict[str, Any]:
        """Mark a comment as the answer. See DiscussionManager.mark_answer()."""
        return self._discussions.mark_answer(comment_id)

    def unmark_answer(self, comment_id: str) -> dict[str, Any]:
        """Unmark a comment as the answer. See DiscussionManager.unmark_answer()."""
        return self._discussions.unmark_answer(comment_id)

    def list_discussions(
        self,
        repo: str,
        category_slug: str | None = None,
        first: int = 20,
        after: str | None = None,
    ) -> dict[str, Any]:
        """List Discussions in a repo. See DiscussionManager.list_discussions()."""
        return self._discussions.list_discussions(repo, category_slug, first, after)

    def get_discussion(
        self,
        repo: str,
        discussion_number: int,
        comments_first: int = 50,
        comments_after: str | None = None,
    ) -> dict[str, Any]:
        """Get a single Discussion with comments. See DiscussionManager.get_discussion()."""
        return self._discussions.get_discussion(
            repo, discussion_number, comments_first, comments_after
        )

    def pin_discussion(self, repo: str, discussion_number: int) -> dict[str, Any]:
        """Pin a Discussion. See DiscussionManager.pin_discussion()."""
        return self._discussions.pin_discussion(repo, discussion_number)

    def unpin_discussion(self, repo: str, discussion_number: int) -> dict[str, Any]:
        """Unpin a Discussion. See DiscussionManager.unpin_discussion()."""
        return self._discussions.unpin_discussion(repo, discussion_number)

    def list_discussion_categories(self, repo: str) -> list[dict[str, Any]]:
        """List Discussion categories. See DiscussionManager.list_discussion_categories()."""
        return self._discussions.list_discussion_categories(repo)

    # ------------------------------------------------------------------
    # Repository variables
    # ------------------------------------------------------------------

    def set_repo_variable(self, repo: str, name: str, value: str) -> dict[str, Any]:
        """Create or update a repository variable. See CognitiveBrainIntegration.set_repo_variable()."""
        return self._cb.set_repo_variable(repo, name, value)

    # ------------------------------------------------------------------
    # Branch & PR management (delegates to GitOperations and PullRequestManager)
    # ------------------------------------------------------------------

    def create_ref(self, repo: str, ref: str, sha: str) -> dict[str, Any]:
        """Create a git reference (branch or tag). See GitOperations.create_ref()."""
        return self._git.create_ref(repo, ref, sha)

    def create_pull_request(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str,
        draft: bool = False,
    ) -> dict[str, Any]:
        """Open a pull request. See PullRequestManager.create_pull_request()."""
        return self._prs.create_pull_request(repo, title, body, head, base, draft)

    def list_pull_requests(
        self,
        repo: str,
        state: str = "open",
        head: str = "",
        base: str = "",
        per_page: int = 30,
    ) -> list[dict[str, Any]]:
        """List pull requests. See PullRequestManager.list_pull_requests()."""
        return self._prs.list_pull_requests(repo, state, head, base, per_page)

    def merge_branch(
        self,
        repo: str,
        base: str,
        head: str,
        commit_message: str = "",
    ) -> dict[str, Any]:
        """Merge branches server-side. See GitOperations.merge_branch()."""
        return self._git.merge_branch(repo, base, head, commit_message)

    def commit_files(
        self,
        repo: str,
        branch: str,
        files: dict[str, str],
        message: str,
        force: bool = False,
    ) -> str:
        """Commit files via Git Data API. See GitOperations.commit_files()."""
        return self._git.commit_files(repo, branch, files, message, force)

    # ------------------------------------------------------------------
    # Cognitive brain integration (delegates to CognitiveBrainIntegration)
    # ------------------------------------------------------------------

    def retrieve_cb_patterns(
        self,
        limit: int = 10,
        pattern_prefix: str = "CB-",
    ) -> str:
        """Retrieve cognitive-brain patterns. See CognitiveBrainIntegration.retrieve_cb_patterns()."""
        return self._cb.retrieve_cb_patterns(limit, pattern_prefix)

    # ------------------------------------------------------------------
    # Internal methods (exposed for testing & backward compatibility)
    # ------------------------------------------------------------------

    def _record_cb_pattern(
        self,
        pattern_id: str,
        summary: str,
        context: dict[str, str] | None = None,
        outcome: str = "pending",
    ) -> None:
        """Record a cognitive-brain pattern. Delegates to CognitiveBrainIntegration."""
        return self._cb._record_cb_pattern(pattern_id, summary, context, outcome)

    def _request(
        self,
        method: str,
        url: str,
        body: str | dict | None = None,
        headers: dict[str, str] | None = None,
        max_retries: int = 3,
    ) -> dict:
        """Make an HTTP request. Delegates to APIClient."""
        return self._api._request(method, url, body, headers, max_retries)

    def _get(self, url: str) -> dict:
        """Make a GET request. Delegates to APIClient."""
        return self._api._get(url)

    def _resolve_discussion_node_id(self, repo: str, discussion_number: int) -> str:
        """Resolve discussion number to GraphQL node ID. Delegates to DiscussionManager."""
        return self._discussions._resolve_discussion_node_id(repo, discussion_number)

    def _find_discussion_comment(
        self, repo: str, discussion_number: int, marker: str
    ) -> dict[str, str] | None:
        """Find a discussion comment by marker. Delegates to DiscussionManager."""
        return self._discussions._find_discussion_comment(repo, discussion_number, marker)


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
            logger.error(
                f"✅ Comment posted: {result.get('html_url', result)}"
            )  # codeql[py/clear-text-logging-sensitive-data]

        elif args.command == "set-variable":
            poster.set_repo_variable(args.repo, args.name, args.value)
            logger.info(f"✅ Variable set: {args.name}={args.value}")

        elif args.command == "create-discussion":
            body = Path(args.body_file).read_text()
            result = poster.create_discussion(args.repo, args.title, body, args.category)
            logger.info(f"✅ Discussion created: {result.get('url', result)}")

        elif args.command == "update-discussion":
            body = Path(args.body_file).read_text() if args.body_file else None
            result = poster.update_discussion(
                args.repo, args.number, title=args.title, body=body, category_slug=args.category
            )
            logger.info(f"✅ Discussion #{args.number} updated: {result.get('url', result)}")

        elif args.command == "lock-discussion":
            poster.lock_discussion(args.repo, args.number, args.reason)
            logger.info(f"✅ Discussion #{args.number} locked ({args.reason})")

        elif args.command == "unlock-discussion":
            poster.unlock_discussion(args.repo, args.number)
            logger.info(f"✅ Discussion #{args.number} unlocked")

        elif args.command == "delete-discussion":
            ok = poster.delete_discussion(args.repo, args.number)
            if ok:
                logger.info(f"✅ Discussion #{args.number} deleted")
            else:
                logger.error(f"❌ Failed to delete Discussion #{args.number}")
                return 1

        elif args.command == "delete-discussion-comment":
            ok = poster.delete_discussion_comment(args.comment_id)
            if ok:
                logger.info(f"✅ Comment {args.comment_id} deleted")
            else:
                logger.error(f"❌ Failed to delete comment {args.comment_id}")
                return 1

        elif args.command == "mark-answer":
            result = poster.mark_answer(args.comment_id)
            num = result.get("number", "?")
            logger.info(f"✅ Comment {args.comment_id} marked as answer on discussion #{num}")

        elif args.command == "unmark-answer":
            result = poster.unmark_answer(args.comment_id)
            num = result.get("number", "?")
            logger.info(f"✅ Comment {args.comment_id} unmarked as answer on discussion #{num}")

        elif args.command == "list-discussions":
            page = poster.list_discussions(args.repo, args.category, args.first, args.after)
            discussions = page["nodes"]
            page_info = page["pageInfo"]
            if getattr(args, "json", False):
                import json as _json

                logger.info(_json.dumps(page, indent=2))
            else:
                for d in discussions:
                    cat = d.get("category", {}).get("slug", "?")
                    answered = "✅" if d.get("isAnswered") else "  "
                    logger.info(f"#{d['number']:5}  {answered}  [{cat}]  {d['title'][:70]}")
                logger.info(f"\n{len(discussions)} discussion(s) found")
                if page_info.get("hasNextPage"):
                    logger.info(f"Next page cursor: {page_info['endCursor']}")
                    logger.info("  (use --after <cursor> to fetch next page)")

        elif args.command == "get-discussion":
            disc = poster.get_discussion(
                args.repo,
                args.number,
                comments_first=args.comments_first,
                comments_after=args.comments_after,
            )
            if getattr(args, "json", False):
                import json as _json

                logger.info(_json.dumps(disc, indent=2))
            else:
                logger.info(f"## Discussion #{disc['number']}: {disc['title']}")
                logger.info(
                    f"   URL: {disc['url']}"
                )  # codeql[py/clear-text-logging-sensitive-data]
                logger.info(f"   Category: {disc.get('category', {}).get('name', '?')}")
                logger.info(
                    f"   Answered: {disc.get('isAnswered', False)}"
                    f"  |  Locked: {disc.get('isLocked', False)}"
                )
                logger.info(f"   Comments: {disc.get('comments', {}).get('totalCount', 0)}")
                comments_page_info = disc.get("comments", {}).get("pageInfo", {})
                if comments_page_info.get("hasNextPage"):
                    logger.info(f"   Next comments cursor: {comments_page_info['endCursor']}")
                    logger.info("   (use --comments-after <cursor> to fetch next page)")

        elif args.command == "list-discussion-categories":
            cats = poster.list_discussion_categories(args.repo)
            if getattr(args, "json", False):
                import json as _json

                logger.info(_json.dumps(cats, indent=2))
            else:
                logger.info(f"{'Slug':35}  {'Name':30}  Answerable")
                logger.info("-" * 75)
                for c in cats:
                    slug = c.get("slug", "")
                    name = c.get("name", "")
                    answerable = c.get("isAnswerable", False)
                    logger.info(f"{slug:35}  {name:30}  {answerable}")
                logger.info(f"\n{len(cats)} category/categories")

        elif args.command == "create-branch":
            result = poster.create_ref(args.repo, args.ref, args.sha)
            logger.info(f"✅ Branch created: {result.get('ref', args.ref)} @ {args.sha[:8]}")

        elif args.command == "pin-discussion":
            result = poster.pin_discussion(args.repo, args.number)
            num = result.get("number", args.number)
            logger.info(f"✅ Discussion #{num} pinned in {args.repo}")

        elif args.command == "unpin-discussion":
            result = poster.unpin_discussion(args.repo, args.number)
            num = result.get("number", args.number)
            logger.info(f"✅ Discussion #{num} unpinned in {args.repo}")

        elif args.command == "create-pr":
            body = args.body
            if not body and args.body_file:
                body = Path(args.body_file).read_text()
            result = poster.create_pull_request(
                args.repo, args.title, body, args.head, args.base, args.draft
            )
            logger.info(f"✅ PR #{result.get('number')} opened: {result.get('html_url', result)}")

        elif args.command == "merge-branch":
            result = poster.merge_branch(args.repo, args.base, args.head, args.message)
            if result:
                sha = result.get("sha", "")
                logger.info(
                    f"✅ Merged {args.head} → {args.base}: {sha[:8] if sha else 'up-to-date'}"
                )
            else:
                logger.info(f"✅ {args.head} already up-to-date with {args.base} — no merge needed")

        elif args.command == "retrieve-patterns":
            md = poster.retrieve_cb_patterns(limit=args.limit, pattern_prefix=args.prefix)
            if md:
                logger.info(md)
            else:
                logger.info(
                    "ℹ️  No cognitive-brain patterns found (CB package unavailable or DB empty)."
                )

        elif args.command == "commit-files":
            files: dict[str, str] = {}
            for mapping in args.files:
                dest, _, src = mapping.partition(":")
                if not dest or not src:
                    logger.error(
                        f"❌ Invalid --file mapping {mapping!r} — expected DEST:SRC",
                    )
                    return 1
                files[dest] = Path(src).read_text(encoding="utf-8")
            commit_sha = poster.commit_files(
                args.repo, args.branch, files, args.message, args.force
            )
            logger.info(f"✅ Committed {len(files)} file(s) to {args.branch}: {commit_sha[:8]}")

        elif args.command == "add-discussion-comment":
            body = args.body or Path(args.body_file).read_text(encoding="utf-8")
            result = poster.add_discussion_comment(args.repo, args.number, body)
            logger.info(f"✅ Discussion comment posted: {result.get('url', result)}")

        elif args.command == "upsert-discussion-comment":
            body = args.body or Path(args.body_file).read_text(encoding="utf-8")
            result = poster.upsert_discussion_comment(args.repo, args.number, body, args.marker)
            logger.info(f"✅ Discussion comment upserted: {result.get('url', result)}")

        elif args.command == "post-ci-pattern-summary":
            body = Path(args.body_file).read_text(encoding="utf-8")
            result = poster.post_ci_pattern_summary(args.repo, args.number, body, args.session_id)
            logger.info(
                f"✅ CI pattern summary posted to discussion #{args.number}: {result.get('url', result)}"
            )  # noqa: E501

        elif args.command == "post-continuation":
            body = args.body or Path(args.body_file).read_text(encoding="utf-8")
            result = poster.post_continuation_chain(args.repo, args.number, body)
            logger.info(
                f"✅ Continuation chain posted to discussion #{args.number}: {result.get('url', result)}"
            )  # noqa: E501

    except RuntimeError as exc:
        type(exc).__name__
        logger.info("❌ <ERROR_TYPE>")
        return 1
    except urllib.error.HTTPError as exc:
        logger.error(f"❌ GitHub API error {exc.code}: {exc.reason}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
