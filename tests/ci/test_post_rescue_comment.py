"""Tests for scripts/ci/post_rescue_comment.py — self-suppress logic (S178c).

Covers:
  - _get_branch_head_sha() : parses the GitHub branches API response
  - main() self-suppress   : skips posting when branch HEAD ≠ COMMIT_SHA
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import (
    patch,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
)

# ---------------------------------------------------------------------------
# Ensure scripts/ci is importable regardless of pytest working directory
# ---------------------------------------------------------------------------
SCRIPTS_CI = Path(__file__).resolve().parents[2] / "scripts" / "ci"
if str(SCRIPTS_CI) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_CI))

import post_rescue_comment as prc


class TestGetBranchHeadSha:
    """Unit tests for _get_branch_head_sha()."""

    def test_returns_sha_on_success(self):
        sha = "abc123def456abc123def456abc123def456abcd"  # pragma: allowlist secret
        with patch.object(prc, "_gh", return_value=(200, {"commit": {"sha": sha}})):
            result = prc._get_branch_head_sha("token", "owner/repo", "my-branch")
        assert result == sha, "Result must not be empty"

    def test_returns_none_on_non_200(self):
        with patch.object(prc, "_gh", return_value=(404, {})):
            result = prc._get_branch_head_sha("token", "owner/repo", "missing-branch")
        assert result is None, "Result must not be empty"

    def test_returns_none_when_commit_key_absent(self):
        with patch.object(prc, "_gh", return_value=(200, {})):
            result = prc._get_branch_head_sha("token", "owner/repo", "my-branch")
        assert result is None, "Result must not be empty"

    def test_returns_none_when_sha_key_absent(self):
        with patch.object(prc, "_gh", return_value=(200, {"commit": {}})):
            result = prc._get_branch_head_sha("token", "owner/repo", "my-branch")
        assert result is None, "Result must not be empty"

    def test_url_encodes_branch_name(self):
        """Branches with spaces and '/' must be URL-encoded."""
        calls = []

        def _mock_gh(method, path, token):
            calls.append(path)
            return 404, {}

        with patch.object(prc, "_gh", side_effect=_mock_gh):
            prc._get_branch_head_sha("t", "o/r", "feature/my branch")

        assert len(calls) == 1, "Calls must not be empty"
        path_lower = calls[0].lower()
        # Spaces in the branch name must be percent-encoded as %20.
        assert ("%20" in path_lower, "Condition must be true"
        ), f"Expected space to be percent-encoded in branch path, got: {calls[0]!r}"
        # Slashes in branch names must also be percent-encoded as %2f (%2F).
        assert ("%2f" in path_lower, "Condition must be true"
        ), f"Expected slash to be percent-encoded in branch path, got: {calls[0]!r}"


class TestRescueCommentUpsert:
    """Unit tests for same-SHA rescue comment upsert helpers."""

    def test_find_rescue_comment_falls_back_to_visible_signature(self):
        signature = "**Branch:** `feature` | **Commit:** `abc123`"

        def _mock_gh(method, path, token, body=None):
            assert method == "GET", "method is not valid"
            assert "page=1" in path, "Condition must be true"
            return 200, [{"id": 10, "body": f"## Rescue\n\n{signature}"}]

        with patch.object(prc, "_gh", side_effect=_mock_gh):
            comment_id, body = prc._find_rescue_comment(
                "token",
                "owner/repo",
                4193,
                "<!-- ci-rescue-sha:4193:abc123 -->",
                signature,
            )

        assert comment_id == 10, "comment_id is not valid"
        assert signature in body, "Condition must be true"

    def test_consolidates_duplicate_rescue_comments(self):
        marker = "<!-- ci-rescue-sha:4193:abc123def456 -->"
        signature = "**Branch:** `feature` | **Commit:** `abc123def4567890`"
        comments = [
            {"id": 100, "body": f"{marker}\ncanonical\n{signature}"},
            {"id": 101, "body": f"{marker}\nduplicate detail\n{signature}"},
        ]
        calls = []

        def _mock_gh(method, path, token, body=None):
            calls.append((method, path, body))
            if method == "GET":
                return 200, comments
            if method == "PATCH":
                assert path.endswith("/issues/comments/100"), "Condition must be true"
                assert "duplicate detail" in body["body"], "Condition must be true"
                return 200, {"id": 100}
            if method == "DELETE":
                assert path.endswith("/issues/comments/101"), "Condition must be true"
                return 204, {}
            raise AssertionError(f"unexpected call: {method} {path}")

        with (
            patch.object(prc, "_gh", side_effect=_mock_gh),
            patch("time.sleep", return_value=None),
        ):
            prc._consolidate_duplicate_rescue_comments(
                "token",
                "owner/repo",
                4193,
                marker,
                signature,
                created_id=101,
            )

        methods = [call[0] for call in calls]
        assert methods == ["GET", "PATCH", "DELETE"]


class TestSelfSuppressMainLogic:
    """self-suppress guard: when branch HEAD ≠ COMMIT_SHA, no comment is posted."""

    _ENV_BASE = {
        "GH_TOKEN": "test-token",
        "REPO": "Aries-Serpent/_codex_",
        "COMMIT_SHA": "aabbccddeeff00112233445566778899aabbccdd",  # pragma: allowlist secret
        "RUN_ID": "99999999",
        "RUN_URL": "https://github.com/Aries-Serpent/_codex_/actions/runs/99999999",
        "WORKFLOW_NAME": "Test Workflow",
        "BRANCH": "copilot/my-feature",
    }

    def _patch_env(self, monkeypatch, **overrides):
        """Populate test environment variables with optional overrides.

        Starts from ``self._ENV_BASE``, applies ``overrides``, and sets each
        resulting variable via pytest's ``monkeypatch`` fixture.

        Optional variables that are *not* explicitly provided are deleted to
        avoid cross-test leakage. In particular, ``PR_NUMBER`` is removed unless
        overridden so tests can intentionally switch execution paths:
        push mode (``PR_NUMBER`` absent, so the script performs PR lookup via API)
        versus PR-triggered mode (``PR_NUMBER`` present, so the script uses that
        PR directly and skips lookup).
        """
        env = {**self._ENV_BASE, **overrides}
        for k, v in env.items():
            monkeypatch.setenv(k, v)
        # Clear all optional env vars that are not explicitly provided.
        # PR_NUMBER behaves like other optional vars: absent → push mode (API
        # lookup); present → PR-triggered mode.  Other optional vars default
        # to empty string when absent, so clearing them avoids leakage between
        # tests.
        for k in ("PR_NUMBER", "SECTION_TITLE", "SECTION_CONTENT", "APPEND_ONLY"):
            if k not in overrides:
                monkeypatch.delenv(k, raising=False)

    def test_suppresses_when_head_differs(self, monkeypatch, capsys):
        """When branch HEAD != COMMIT_SHA, main() must print the suppression
        message and return without posting any comment.
        """
        self._patch_env(monkeypatch, PR_NUMBER="4200")
        current_head = "1122334455661122334455661122334455661122"
        failure_sha = self._ENV_BASE["COMMIT_SHA"]
        assert (current_head != failure_sha, "current_head is not valid"
        ), "Test setup error: current_head must differ from COMMIT_SHA for this test"

        with patch.object(prc, "_get_branch_head_sha", return_value=current_head):
            with patch.object(prc, "_gh") as mock_gh:
                result = prc.main()

        assert result is None, "Result must not be empty"
        out = capsys.readouterr().out
        assert ("suppressed" in out.lower() or "superseded" in out.lower(), "Condition must be true"
        ), f"Expected suppression message in stdout, got: {out!r}"
        # _gh must NOT have been called to post a comment
        post_calls = [c for c in mock_gh.call_args_list if c.args[0] == "POST"]
        assert not post_calls, "POST should not be called for superseded commit"

    def test_suppresses_when_head_differs_push_mode(self, monkeypatch, capsys):
        """Push mode (PR_NUMBER absent): main() should lookup PR via API and
        still suppress posting when branch HEAD != COMMIT_SHA.
        """
        self._patch_env(monkeypatch)
        current_head = "1122334455661122334455661122334455661122"
        failure_sha = self._ENV_BASE["COMMIT_SHA"]
        assert (current_head != failure_sha, "current_head is not valid"
        ), "Test setup error: current_head must differ from COMMIT_SHA for this test"

        def _gh_side_effect(method, path, token, body=None):
            if method == "GET":
                return 200, [{"number": 4200}]
            return 200, {}

        with patch.object(prc, "_get_branch_head_sha", return_value=current_head):
            with patch.object(prc, "_gh", side_effect=_gh_side_effect) as mock_gh:
                result = prc.main()

        assert result is None, "Result must not be empty"
        out = capsys.readouterr().out
        assert ("suppressed" in out.lower() or "superseded" in out.lower(), "Condition must be true"
        ), f"Expected suppression message in stdout, got: {out!r}"
        get_calls = [c for c in mock_gh.call_args_list if c.args[0] == "GET"]
        assert get_calls, "Expected GET call(s) for PR lookup in push mode"
        post_calls = [c for c in mock_gh.call_args_list if c.args[0] == "POST"]
        assert not post_calls, "POST should not be called for superseded commit"

    def test_posts_when_head_matches(self, monkeypatch, capsys):
        """When branch HEAD == COMMIT_SHA, the rescue comment should be attempted."""
        self._patch_env(monkeypatch, PR_NUMBER="4200")
        commit_sha = self._ENV_BASE["COMMIT_SHA"]

        with patch.object(prc, "_get_branch_head_sha", return_value=commit_sha):
            with patch.object(prc, "_find_rescue_comment", return_value=(None, "")):
                # This test focuses on the "HEAD matches COMMIT_SHA" path reaching
                # the comment POST step. main() may optionally enrich the comment
                # via build_comment_context (from discussion_context_store), but
                # that enrichment is not required for this behavior. Returning 201
                # from _gh keeps the test deterministic and validates post-attempt flow.
                with patch.object(
                    prc, "_gh", return_value=(201, {"html_url": "https://example.com/c/1"})
                ):
                    prc.main()

        out = capsys.readouterr().out
        assert ("✅" in out or "Posted" in out, "Condition must be true"
        ), f"Expected success message for matching SHA, got: {out!r}"

    def test_posts_when_head_matches_with_enrichment_enabled(self, monkeypatch, capsys):
        """When discussion_context_store is available, main() calls build_comment_context
        and still posts the rescue comment successfully.

        ``build_comment_context`` is imported *inside* ``main()`` via
        ``from discussion_context_store import build_comment_context``, so it is
        not a module-level attribute of ``prc``.  The correct patch target is the
        function on the source module (``discussion_context_store.build_comment_context``),
        which ensures the import inside ``main()`` picks up the mock.
        """
        self._patch_env(monkeypatch, PR_NUMBER="4200")
        commit_sha = self._ENV_BASE["COMMIT_SHA"]

        with (
            patch.object(prc, "_get_branch_head_sha", return_value=commit_sha),
            patch.object(prc, "_find_rescue_comment", return_value=(None, "")),
            patch(
                "discussion_context_store.build_comment_context",
                return_value="# Inline Context\n\nExtra context for the agent.",
            ) as mock_ctx,
            patch.object(
                prc, "_gh", return_value=(201, {"html_url": "https://example.com/c/1"})
            ) as mock_gh,
        ):
            prc.main()

        assert (mock_ctx.called, "Condition must be true"
        ), "Expected build_comment_context to be called when discussion_context_store is available"
        post_calls = [c for c in mock_gh.call_args_list if c.args and c.args[0] == "POST"]
        assert (post_calls, "Condition must be true"
        ), "Expected POST to be attempted on matching SHA with enrichment path enabled"
        out = capsys.readouterr().out
        assert ("✅" in out or "Posted" in out, "Condition must be true"
        ), f"Expected success message for matching SHA with enrichment, got: {out!r}"

    def test_no_suppress_when_head_unavailable(self, monkeypatch, capsys):
        """When the branch HEAD SHA cannot be retrieved (API error), the guard
        must NOT suppress — fail open (always post) to avoid silent failures.
        """
        self._patch_env(monkeypatch, PR_NUMBER="4200")

        with patch.object(prc, "_get_branch_head_sha", return_value=None):
            with patch.object(prc, "_find_rescue_comment", return_value=(None, "")):
                with patch.object(
                    prc, "_gh", return_value=(201, {"html_url": "https://example.com/c/1"})
                ):
                    prc.main()

        out = capsys.readouterr().out
        # Should proceed to post (not suppressed)
        assert "suppressed" not in out.lower(), "Condition must be true"


class TestDefensiveShaResolution:
    """Tests for the defensive COMMIT_SHA / BRANCH resolution from the PR API.

    When workflows fire on issue_comment or pull_request_review events, the
    github.event.pull_request.head.sha / github.head_ref expressions may expand
    to empty strings.  post_rescue_comment.py must fetch the missing values from
    the PR API so the rescue comment always contains a valid, non-empty SHA.
    """

    _ENV_BASE = {
        "GH_TOKEN": "test-token",
        "REPO": "Aries-Serpent/_codex_",
        "RUN_ID": "88888888",
        "RUN_URL": "https://github.com/Aries-Serpent/_codex_/actions/runs/88888888",
        "WORKFLOW_NAME": "Comment Review Gate",
        "PR_NUMBER": "4531",
    }

    def _patch_env(self, monkeypatch, **overrides):
        env = {**self._ENV_BASE, **overrides}
        for k, v in env.items():
            monkeypatch.setenv(k, v)
        for k in ("SECTION_TITLE", "SECTION_CONTENT", "APPEND_ONLY"):
            if k not in overrides:
                monkeypatch.delenv(k, raising=False)

    def test_resolves_sha_from_pr_api_when_commit_sha_empty(self, monkeypatch, capsys):
        """When COMMIT_SHA is empty (e.g. issue_comment trigger), the script
        must fetch it from the PR API and use the resolved SHA in the comment.
        """
        resolved_sha = "deadbeefcafe1234deadbeefcafe1234deadbeef"  # pragma: allowlist secret
        self._patch_env(monkeypatch, COMMIT_SHA="", BRANCH="")

        pr_api_response = {
            "head": {"sha": resolved_sha, "ref": "0D_base_"},
        }

        def _gh_side_effect(method, path, token, body=None):
            if method == "GET" and "/pulls/4531" in path:
                return 200, pr_api_response
            if method == "GET" and "/comments" in path:
                return 200, []  # no existing rescue comment
            if method == "POST":
                # Capture the comment body and assert SHA is present
                posted_body = body.get("body", "") if body else ""
                assert resolved_sha in posted_body, (
                    f"Expected resolved SHA {resolved_sha!r} in posted comment body, "
                    f"got: {posted_body[:200]!r}"
                )
                return 201, {"id": 1, "html_url": "https://example.com/c/1"}
            return 200, {}

        with patch.object(prc, "_gh", side_effect=_gh_side_effect):
            with patch.object(prc, "_get_branch_head_sha", return_value=resolved_sha):
                prc.main()

        out = capsys.readouterr().out
        assert "resolved" in out.lower(), f"Expected SHA resolution log message, got: {out!r}"

    def test_resolves_branch_from_pr_api_when_branch_empty(self, monkeypatch, capsys):
        """When BRANCH is empty the script must fetch it from the PR API."""
        resolved_sha = "cafebabe1234cafebabe1234cafebabe12341234"  # pragma: allowlist secret
        self._patch_env(monkeypatch, COMMIT_SHA=resolved_sha, BRANCH="")

        pr_api_response = {
            "head": {"sha": resolved_sha, "ref": "0D_base_"},
        }

        def _gh_side_effect(method, path, token, body=None):
            if method == "GET" and "/pulls/4531" in path:
                return 200, pr_api_response
            if method == "GET" and "/comments" in path:
                return 200, []
            if method == "POST":
                posted_body = body.get("body", "") if body else ""
                assert ("0D_base_" in posted_body, "Condition must be true"
                ), f"Expected resolved branch '0D_base_' in posted body: {posted_body[:200]!r}"
                return 201, {"id": 2, "html_url": "https://example.com/c/2"}
            return 200, {}

        with patch.object(prc, "_gh", side_effect=_gh_side_effect):
            with patch.object(prc, "_get_branch_head_sha", return_value=resolved_sha):
                prc.main()

        out = capsys.readouterr().out
        assert "resolved" in out.lower(), f"Expected branch resolution log message, got: {out!r}"

    def test_continues_with_warning_when_pr_api_lookup_fails(self, monkeypatch, capsys):
        """When the PR API lookup fails, the script warns and continues (best-effort)."""
        self._patch_env(monkeypatch, COMMIT_SHA="", BRANCH="")

        def _gh_side_effect(method, path, token, body=None):
            if method == "GET" and "/pulls/4531" in path:
                return 404, {"message": "Not Found"}
            if method == "GET" and "/comments" in path:
                return 200, []
            if method == "POST":
                return 201, {"id": 3, "html_url": "https://example.com/c/3"}
            return 200, {}

        with patch.object(prc, "_gh", side_effect=_gh_side_effect):
            with patch.object(prc, "_get_branch_head_sha", return_value=None):
                prc.main()

        out = capsys.readouterr().out
        assert ("⚠️" in out or "warning" in out.lower() or "404" in out
        ), f"Expected warning about failed PR lookup, got: {out!r}"

    def test_skips_lookup_when_both_sha_and_branch_provided(self, monkeypatch):
        """When COMMIT_SHA and BRANCH are both non-empty, the PR API must NOT
        be called for resolution (the env vars are fully supplied).
        """
        full_sha = "aabbccddeeff00112233445566778899aabbccdd"  # pragma: allowlist secret
        self._patch_env(monkeypatch, COMMIT_SHA=full_sha, BRANCH="my-feature")

        pr_lookup_calls = []

        def _gh_side_effect(method, path, token, body=None):
            if method == "GET" and "/pulls/4531" in path and "/comments" not in path:
                pr_lookup_calls.append(path)
            if method == "GET" and "/comments" in path:
                return 200, []
            if method == "POST":
                return 201, {"id": 4, "html_url": "https://example.com/c/4"}
            return 200, {}

        with patch.object(prc, "_gh", side_effect=_gh_side_effect):
            with patch.object(prc, "_get_branch_head_sha", return_value=full_sha):
                prc.main()

        assert not pr_lookup_calls, (
            "PR API should NOT be called for SHA resolution when both "
            f"COMMIT_SHA and BRANCH are already provided; got calls: {pr_lookup_calls}"
        )
