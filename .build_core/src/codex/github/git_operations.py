"""Git operations for autonomous branch and commit management.

Encapsulates Git Data API operations for creating refs, branches, commits,
and managing repository content without local git clone.
"""

from __future__ import annotations

import logging
from typing import Any

from codex.github.api_client import _GITHUB_API, APIClient

logger = logging.getLogger(__name__)


class GitOperations:
    """GitHub Git Data API operations for autonomous commits and branches.

    Handles:
    - Creating and updating git references (branches, tags)
    - Server-side merges
    - Autonomous file commits via Git Data API (blobs → trees → commits → refs)
    """

    def __init__(self, api_client: APIClient) -> None:
        """Initialize with an APIClient for making requests."""
        self._api = api_client

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
        self._api._require_token()
        # Normalise the ref: only add refs/heads/ when the caller passes a bare
        # branch name (no slash at all). Explicit refs/heads/…, refs/tags/…, or
        # heads/… / tags/… prefixes are left intact to avoid double-prefixing.
        if not ref.startswith("refs/"):
            if ref.startswith("heads/") or ref.startswith("tags/"):
                ref = f"refs/{ref}"
            else:
                ref = f"refs/heads/{ref}"
        url = f"{_GITHUB_API}/repos/{repo}/git/refs"
        result = self._api._request("POST", url, {"ref": ref, "sha": sha})
        self._api._record_cb_pattern(
            "CB-branch-create",
            f"create_ref: {ref} @ {sha[:8] if sha else sha}",
            {"repo": repo, "ref": ref, "sha": sha},
        )
        return result

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
        The resulting commit SHA can be used with create_ref() to
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
        self._api._require_token()
        url = f"{_GITHUB_API}/repos/{repo}/merges"
        payload: dict[str, Any] = {"base": base, "head": head}
        if commit_message:
            payload["commit_message"] = commit_message
        result = self._api._request("POST", url, payload)
        outcome = "success" if result else "already_exists"
        self._api._record_cb_pattern(
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
    # Git Data API — autonomous commits
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
        result = self._api._request("POST", url, {"content": content, "encoding": encoding})
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
            SHA of the tree to build on top of. Pass an empty string to
            create a standalone root tree (rarely needed — usually the
            current commit tree SHA should be passed here).
        """
        url = f"{_GITHUB_API}/repos/{repo}/git/trees"
        payload: dict[str, Any] = {"tree": tree_items}
        if base_tree_sha:
            payload["base_tree"] = base_tree_sha
        result = self._api._request("POST", url, payload)
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
            SHA of the root tree for this commit (from _create_tree()).
        parent_shas:
            List of parent commit SHAs (typically one — the current HEAD).
        """
        url = f"{_GITHUB_API}/repos/{repo}/git/commits"
        result = self._api._request(
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
            Full ref name, e.g. ``"refs/heads/0D_base_"``. A bare branch
            name is accepted and will be normalised to ``refs/heads/<name>``.
        sha:
            New target commit SHA.
        force:
            When ``True``, perform a force-update (non-fast-forward).
        """
        if not ref.startswith("refs/"):
            ref = f"refs/heads/{ref}"
        url = f"{_GITHUB_API}/repos/{repo}/git/refs/{ref.removeprefix('refs/')}"
        return self._api._request("PATCH", url, {"sha": sha, "force": force})

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
        result_get = self._api._get(url)
        return result_get["object"]["sha"]

    def _get_commit_tree_sha(self, repo: str, commit_sha: str) -> str:
        """Return the tree SHA for a given commit SHA."""
        url = f"{_GITHUB_API}/repos/{repo}/git/commits/{commit_sha}"
        result = self._api._get(url)
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

        Closes the "agent can only push via report_progress" constraint.
        Uses the low-level Git Data API (blobs → trees → commits → PATCH refs)
        to create a commit entirely through HTTPS REST calls, without requiring
        a local ``git clone`` or ``git push``.

        Requires the token to have ``contents: write`` scope.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format, e.g. ``"Aries-Serpent/_codex_"``.
        branch:
            Target branch name (e.g. ``"0D_base_"``). The branch must
            already exist.
        files:
            Mapping of file paths (repo-relative, e.g.
            ``"src/codex/foo.py"``) to their new UTF-8 string content.
        message:
            Commit message.
        force:
            When ``True``, force-update the branch ref even for
            non-fast-forward situations. Use with caution.

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
        """
        self._api._require_token()

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

        self._api._record_cb_pattern(
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
