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
        result = self._request("POST", url, {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
            "draft": draft,
        })
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
        result = self._request("POST", url, {
            "message": message,
            "tree": tree_sha,
            "parents": parent_shas,
        })
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
            tree_items.append({
                "path": path,
                "mode": "100644",  # regular file
                "type": "blob",
                "sha": blob_sha,
            })

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
            pattern_id, decision, outcome, context,
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
                p for p in all_patterns
                if getattr(p, "pattern_id", "").startswith(pattern_prefix)
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
                    "✅ success"
                    if sr == 1.0
                    else ("⚠️ partial" if sr and sr > 0 else "❌ fail")
                )
                lines.append(f"| `{pid}` | {dec} | {outcome} |")

            return "\n".join(lines) + "\n"

        except Exception as _exc:  # noqa: BLE001 — fail-open
            logger.debug(
                "CB pattern retrieval skipped (%s: %s)", type(_exc).__name__, _exc
            )
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
                        wait = (2 ** attempt) * 1.0  # 1s, 2s, 4s …
                    logger.warning(
                        "GitHub API rate-limited (%d). Retrying in %.0fs (attempt %d/%d)…",
                        exc.code, wait, attempt + 1, max_retries,
                    )
                    time.sleep(wait)
                else:
                    error_body = exc.read().decode(errors="replace")
                    logger.error(
                        "GitHub API %s %s → %d: %s", method, url, exc.code, error_body
                    )
                    raise
        # Should be unreachable, but satisfy type checker
        raise last_exc  # type: ignore[misc]

    def _graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        url = f"{_GITHUB_API}/graphql"
        return self._request("POST", url, {"query": query, "variables": variables})

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

    # create-discussion
    cd = sub.add_parser("create-discussion", help="Create a GitHub Discussion")
    cd.add_argument("--repo", required=True)
    cd.add_argument("--title", required=True)
    cd.add_argument("--body-file", required=True)
    cd.add_argument("--category", default="cognitive-brain-patterns")

    # create-branch  (IMP-001 / IMP-010 — S174)
    cb = sub.add_parser(
        "create-branch",
        help="Create a branch ref on GitHub (requires contents:write token)",
    )
    cb.add_argument("--repo", required=True, help="owner/repo")
    cb.add_argument(
        "--ref", required=True,
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
        "--prefix", default="CB-",
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

        elif args.command == "create-branch":
            result = poster.create_ref(args.repo, args.ref, args.sha)
            print(f"✅ Branch created: {result.get('ref', args.ref)} @ {args.sha[:8]}")

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
                    print(f"❌ Invalid --file mapping {mapping!r} — expected DEST:SRC", file=sys.stderr)  # noqa: E501
                    return 1
                files[dest] = Path(src).read_text(encoding="utf-8")
            commit_sha = poster.commit_files(args.repo, args.branch, files, args.message, args.force)  # noqa: E501
            print(f"✅ Committed {len(files)} file(s) to {args.branch}: {commit_sha[:8]}")

    except RuntimeError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    except urllib.error.HTTPError as exc:
        print(f"❌ GitHub API error {exc.code}: {exc.reason}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
