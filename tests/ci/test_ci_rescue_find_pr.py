"""
Tests for ci_rescue.py — find_pr_for_run() multi-PR selection logic.

Covers the S230 fix: when multiple PRs share the same HEAD branch,
find_pr_for_run() must return the PR with the *highest* number (most
recently opened) rather than prs[0] (oldest), to avoid posting rescue
comments on the wrong PR.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------
SCRIPTS_CI = Path(__file__).resolve().parents[2] / "scripts" / "ci"
if str(SCRIPTS_CI) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_CI))

import ci_rescue

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pr(number: int, sha: str) -> dict[str, Any]:
    """Build a minimal PR dict matching GitHub API shape."""
    return {"number": number, "head": {"sha": sha}}


def _make_run_data(prs: list[dict], head_sha: str) -> dict[str, Any]:
    """Build a minimal workflow run API response."""
    return {"pull_requests": prs, "head_sha": head_sha}


def _mock_gh_api(responses: dict[str, Any]):
    """Return a mock for `_gh_api` that returns pre-canned responses keyed by path prefix."""

    def _impl(path: str, _token: str, **_kwargs):
        for prefix, data in responses.items():
            if path.startswith(prefix):
                return 200, data
        return 404, {}

    return _impl


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFindPrForRun:
    """Unit tests for find_pr_for_run() covering the S230 multi-PR fix."""

    def _run(self, run_data: dict, open_prs: list[dict] | None = None) -> int | None:
        """Call find_pr_for_run with pre-canned API responses."""
        open_prs = open_prs or []
        responses = {
            "/repos/owner/repo/actions/runs/999": run_data,
            "/repos/owner/repo/pulls": open_prs,
        }
        with patch.object(ci_rescue, "_gh_api", side_effect=_mock_gh_api(responses)):
            return ci_rescue.find_pr_for_run(999, "owner/repo", "fake-token")

    # -- Single PR (regression: original prs[0] behaviour preserved) --------

    def test_single_pr_returns_that_pr(self):
        """When only one PR is linked to the run, return it."""
        sha = "abc123"
        data = _make_run_data([_make_pr(42, sha)], sha)
        assert self._run(data) == 42, "Data must not be empty"

    # -- Multiple PRs sharing same HEAD SHA (S230 cross-PR contamination) ---

    def test_multiple_prs_same_sha_returns_highest(self):
        """When two PRs share the same head SHA, prefer the highest PR number."""
        sha = "deadbeef"
        prs = [_make_pr(3790, sha), _make_pr(3798, sha)]
        data = _make_run_data(prs, sha)
        assert self._run(data) == 3798, "Data must not be empty"

    def test_multiple_prs_same_sha_order_irrelevant(self):
        """Highest-PR preference must be independent of list order."""
        sha = "cafebabe"
        # Older PR listed first in GitHub API response
        prs = [_make_pr(100, sha), _make_pr(200, sha), _make_pr(150, sha)]
        data = _make_run_data(prs, sha)
        assert self._run(data) == 200, "Data must not be empty"

    def test_multiple_prs_only_one_matches_sha(self):
        """When only one PR's SHA matches, return that one regardless of order."""
        sha_match = "aaaa1111"
        sha_other = "bbbb2222"
        prs = [_make_pr(3790, sha_other), _make_pr(3798, sha_match)]
        data = _make_run_data(prs, sha_match)
        assert self._run(data) == 3798, "Data must not be empty"

    def test_multiple_prs_no_sha_match_returns_highest(self):
        """When no PR SHA matches head_sha, fall back to highest PR number."""
        prs = [_make_pr(10, "xxxx"), _make_pr(20, "yyyy")]
        data = _make_run_data(prs, "zzzz")  # head_sha doesn't match any
        assert self._run(data) == 20, "Data must not be empty"

    # -- Fallback path (empty pull_requests list) ----------------------------

    def test_fallback_to_open_prs_single_match(self):
        """When pull_requests is empty, scan open PRs and return the match."""
        sha = "fallback123"
        data = _make_run_data([], sha)
        open_prs = [_make_pr(77, sha)]
        assert self._run(data, open_prs) == 77

    def test_fallback_to_open_prs_multiple_matches_returns_highest(self):
        """Fallback path: multiple open PRs matching SHA → return highest number."""
        sha = "multi456"
        data = _make_run_data([], sha)
        open_prs = [_make_pr(50, sha), _make_pr(75, sha), _make_pr(60, sha)]
        assert self._run(data, open_prs) == 75

    def test_fallback_no_match_returns_none(self):
        """When no PR matches in either path, return None."""
        data = _make_run_data([], "no-match-sha")
        open_prs = [_make_pr(1, "different-sha")]
        assert self._run(data, open_prs) is None

    # -- Edge cases ---------------------------------------------------------

    def test_invalid_run_data_returns_none(self):
        """Non-dict API response should return None gracefully."""
        with patch.object(ci_rescue, "_gh_api", return_value=(404, None)):
            result = ci_rescue.find_pr_for_run(999, "owner/repo", "fake-token")
        assert result is None, "Result must not be empty"

    def test_empty_pull_requests_and_no_sha_returns_none(self):
        """Empty pull_requests + no head_sha → None."""
        data = {"pull_requests": [], "head_sha": ""}
        assert self._run(data, []) is None
