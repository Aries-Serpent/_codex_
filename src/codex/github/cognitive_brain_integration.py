"""Cognitive brain integration for pattern recording and retrieval.

Records and retrieves patterns from the cognitive-brain system for
session context injection and learning loop integration.
"""

from __future__ import annotations

import logging
from typing import Any

from codex.github.api_client import _GITHUB_API, APIClient

logger = logging.getLogger(__name__)


class CognitiveBrainIntegration:
    """Cognitive brain integration for pattern recording and memory.

    Handles:
    - Recording lifecycle patterns to the cognitive-brain memory
    - Retrieving patterns for session context injection
    - Repository variable management
    """

    def __init__(self, api_client: APIClient) -> None:
        """Initialize with an APIClient for making requests."""
        self._api = api_client

    def post_ci_pattern_summary(
        self,
        repo: str,
        discussion_number: int,
        summary_md: str,
        session_id: str = "",
    ) -> dict[str, Any]:
        """Post (or update) a CI pattern knowledge-graph summary as a Discussion comment.

        Uses upsert_discussion_comment so each session's summary replaces
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
        # Note: We delegate to the discussion manager for actual posting
        # This is handled by the facade in mcp_poster.py
        return {"marker": marker, "body": full_body}

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
        # Note: actual posting is delegated to discussion manager
        return {"repo": repo, "discussion_number": discussion_number, "body": chain_md}

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
            from cognitive_brain.quantum.memory import MemoryPattern, SQLiteMemory

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
            logger.debug(
                "CB pattern stored: %s", pattern_id
            )  # codeql[py/clear-text-logging-sensitive-data]
        except (ValueError, TypeError, RuntimeError) as _cb_exc:
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
        """Retrieve recent cognitive-brain patterns for session context injection.

        Queries the SQLite cognitive-brain memory for the most recent patterns
        whose ``pattern_id`` starts with *pattern_prefix*. Returns a
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
            from cognitive_brain.quantum.memory import SQLiteMemory

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

        except (IOError, OSError) as _exc:
            logger.debug(
                "CB pattern retrieval skipped (%s: %s)", type(_exc).__name__, _exc
            )  # codeql[py/clear-text-logging-sensitive-data]
            return ""

    def set_repo_variable(self, repo: str, name: str, value: str) -> dict[str, Any]:
        """Create or update a repository Actions variable.

        Requires the token to have ``actions: write`` scope.
        """
        self._api._require_token()
        url = f"{_GITHUB_API}/repos/{repo}/actions/variables/{name}"
        # Try PATCH first (update existing); fall back to POST (create new)
        try:
            return self._api._request("PATCH", url, {"name": name, "value": value})
        except Exception as exc:
            # Check if it's a 404 (not found) — if so, try POST
            if hasattr(exc, "code") and exc.code == 404:
                url_create = f"{_GITHUB_API}/repos/{repo}/actions/variables"
                return self._api._request("POST", url_create, {"name": name, "value": value})
            raise
