"""Tests for scripts/ci/post_rescue_comment.py — self-suppress logic (S178c).

Covers:
  - _get_branch_head_sha() : parses the GitHub branches API response
  - main() self-suppress   : skips posting when branch HEAD ≠ COMMIT_SHA
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Ensure scripts/ci is importable regardless of pytest working directory
# ---------------------------------------------------------------------------
SCRIPTS_CI = Path(__file__).resolve().parents[2] / "scripts" / "ci"
if str(SCRIPTS_CI) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_CI))

import post_rescue_comment as prc  # noqa: E402  (after sys.path fix)


class TestGetBranchHeadSha:
    """Unit tests for _get_branch_head_sha()."""

    def test_returns_sha_on_success(self):
        sha = "abc123def456abc123def456abc123def456abcd"
        with patch.object(prc, "_gh", return_value=(200, {"commit": {"sha": sha}})):
            result = prc._get_branch_head_sha("token", "owner/repo", "my-branch")
        assert result == sha

    def test_returns_none_on_non_200(self):
        with patch.object(prc, "_gh", return_value=(404, {})):
            result = prc._get_branch_head_sha("token", "owner/repo", "missing-branch")
        assert result is None

    def test_returns_none_when_commit_key_absent(self):
        with patch.object(prc, "_gh", return_value=(200, {})):
            result = prc._get_branch_head_sha("token", "owner/repo", "my-branch")
        assert result is None

    def test_returns_none_when_sha_key_absent(self):
        with patch.object(prc, "_gh", return_value=(200, {"commit": {}})):
            result = prc._get_branch_head_sha("token", "owner/repo", "my-branch")
        assert result is None

    def test_url_encodes_branch_name(self):
        """Branches with '/' or special chars must be URL-encoded."""
        calls = []

        def _mock_gh(method, path, token):
            calls.append(path)
            return 404, {}

        with patch.object(prc, "_gh", side_effect=_mock_gh):
            prc._get_branch_head_sha("t", "o/r", "feature/my branch")

        assert len(calls) == 1
        # The branch name should be URL-encoded in the path
        assert "feature%2Fmy%20branch" in calls[0] or "feature/my%20branch" in calls[0] or "feature%2F" in calls[0]


class TestSelfSuppressMainLogic:
    """self-suppress guard: when branch HEAD ≠ COMMIT_SHA, no comment is posted."""

    _ENV_BASE = {
        "GH_TOKEN": "fake-token",
        "REPO": "Aries-Serpent/_codex_",
        "COMMIT_SHA": "aabbccddeeff00112233445566778899aabbccdd",
        "RUN_ID": "99999999",
        "RUN_URL": "https://github.com/Aries-Serpent/_codex_/actions/runs/99999999",
        "WORKFLOW_NAME": "Test Workflow",
        "BRANCH": "copilot/my-feature",
    }

    def _patch_env(self, monkeypatch, **overrides):
        env = {**self._ENV_BASE, **overrides}
        for k, v in env.items():
            monkeypatch.setenv(k, v)
        # Clear optional env vars *only if not provided in overrides*
        for k in ("SECTION_TITLE", "SECTION_CONTENT", "APPEND_ONLY"):
            if k not in overrides:
                monkeypatch.delenv(k, raising=False)
        # PR_NUMBER is optional in push mode; only clear if explicitly omitted
        if "PR_NUMBER" not in overrides:
            monkeypatch.delenv("PR_NUMBER", raising=False)

    def test_suppresses_when_head_differs(self, monkeypatch, capsys):
        """When branch HEAD != COMMIT_SHA, main() must print the suppression
        message and return without posting any comment.
        """
        self._patch_env(monkeypatch, PR_NUMBER="4200")
        current_head = "1122334455661122334455661122334455661122"
        failure_sha = self._ENV_BASE["COMMIT_SHA"]
        assert current_head != failure_sha

        with patch.object(prc, "_get_branch_head_sha", return_value=current_head):
            with patch.object(prc, "_gh") as mock_gh:
                prc.main()

        out = capsys.readouterr().out
        assert "suppressed" in out.lower() or "superseded" in out.lower(), (
            f"Expected suppression message in stdout, got: {out!r}"
        )
        # _gh must NOT have been called to post a comment
        post_calls = [c for c in mock_gh.call_args_list if c.args[0] == "POST"]
        assert not post_calls, "POST should not be called for superseded commit"

    def test_posts_when_head_matches(self, monkeypatch, capsys):
        """When branch HEAD == COMMIT_SHA, the rescue comment should be attempted."""
        self._patch_env(monkeypatch, PR_NUMBER="4200")
        commit_sha = self._ENV_BASE["COMMIT_SHA"]

        with patch.object(prc, "_get_branch_head_sha", return_value=commit_sha):
            with patch.object(prc, "_find_rescue_comment", return_value=(None, "")):
                # build_comment_context import will fail gracefully
                with patch.object(prc, "_gh", return_value=(201, {"html_url": "https://example.com/c/1"})):
                    prc.main()

        out = capsys.readouterr().out
        assert "✅" in out or "Posted" in out, (
            f"Expected success message for matching SHA, got: {out!r}"
        )

    def test_no_suppress_when_head_unavailable(self, monkeypatch, capsys):
        """When the branch HEAD SHA cannot be retrieved (API error), the guard
        must NOT suppress — fail open (always post) to avoid silent failures.
        """
        self._patch_env(monkeypatch, PR_NUMBER="4200")

        with patch.object(prc, "_get_branch_head_sha", return_value=None):
            with patch.object(prc, "_find_rescue_comment", return_value=(None, "")):
                with patch.object(prc, "_gh", return_value=(201, {"html_url": "https://example.com/c/1"})):
                    prc.main()

        out = capsys.readouterr().out
        # Should proceed to post (not suppressed)
        assert "suppressed" not in out.lower()
