"""End-to-end delegation test fixture for GitHubMCPPoster (IMP-017).

Tests the full branch-create → PR-open roundtrip in a single session using
mocked urllib responses (no real network calls, no secrets required).
"""

from __future__ import annotations

import json
import unittest.mock as mock  # pragma: allowlist secret

import pytest

from codex.github.mcp_poster import GitHubMCPPoster


@pytest.fixture(autouse=True)
def cleanup_mocks(): # pragma: allowlist secret
    """Automatically reset all mocks after each test."""
    yield
    mock.patch.stopall()

# ---------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------- # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret


def mock_urlopen(payload: dict, status: int = 200):
    """Return a context-manager mock that mimics urllib.request.urlopen."""
    body = json.dumps(payload).encode()
    cm = mock.MagicMock()
    cm.__enter__ = mock.Mock(return_value=cm)
    cm.__exit__ = mock.Mock(return_value=False)
    cm.read = mock.Mock(return_value=body)
    cm.status = status
    return cm


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def poster():
    return GitHubMCPPoster(token="test-token-delegation")


# ---------------------------------------------------------------------------
# Roundtrip test (IMP-017)
# ---------------------------------------------------------------------------


def test_create_ref_and_pr_roundtrip(poster, monkeypatch):
    """GitHubMCPPoster can create a branch and immediately open a PR.

    This exercises the two most critical write methods that the agent uses
    to manage `0D_base_` branch lifecycle:

    1. ``create_ref`` → ``POST /git/refs``
    2. ``create_pull_request`` → ``POST /pulls``

    Both calls are intercepted by monkeypatched urllib so no network traffic
    is produced and no real GitHub credentials are required.
    """
    repo = "Aries-Serpent/_codex_"
    sha = "abc123def456abc123def456abc123def456abc1"
    branch = "0D_base_"
    full_ref = f"refs/heads/{branch}"

    ref_response = {"ref": full_ref, "object": {"sha": sha, "type": "commit"}}
    pr_response = {
        "number": 9999,
        "html_url": f"https://github.com/{repo}/pull/9999",
        "title": "S176 promotion",
        "state": "open",
    }

    call_order: list[str] = []

    def _fake_urlopen(req, timeout=30):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "/git/refs" in url:
            call_order.append("create_ref")
            return mock_urlopen(ref_response, 201)
        if "/pulls" in url:
            call_order.append("create_pull_request")
            return mock_urlopen(pr_response, 201)
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)

    # Step 1 — create branch ref
    ref_result = poster.create_ref(repo, branch, sha)
    assert ref_result["ref"] == full_ref, "Result must not be empty"
    assert ref_result["object"]["sha"] == sha, "Result must not be empty"

    # Step 2 — open PR from that branch
    pr_result = poster.create_pull_request(
        repo=repo,
        title="S176 promotion",
        body="Automated promotion via agent session S176.",
        head=branch,
        base="main",
    )
    assert pr_result["number"] == 9999, "Result must not be empty"
    assert pr_result["state"] == "open", "Result must not be empty"

    # Verify both API calls were made in the correct order
    assert call_order == [
        "create_ref",
        "create_pull_request",
    ], f"Expected ['create_ref', 'create_pull_request'], got {call_order}"


def test_create_ref_and_pr_uses_correct_endpoints(poster, monkeypatch):
    """Verify that create_ref and create_pull_request POST to the expected GitHub URLs."""
    repo = "Aries-Serpent/_codex_"
    captured_urls: list[str] = []

    def _fake_urlopen(req, timeout=30):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        captured_urls.append(url)
        if "/git/refs" in url:
            body = json.dumps({"ref": "refs/heads/test", "object": {"sha": "abc123"}}).encode()
        else:
            body = json.dumps({"number": 1, "html_url": "..."}).encode()
        cm = mock.MagicMock()
        cm.__enter__ = mock.Mock(return_value=cm)
        cm.__exit__ = mock.Mock(return_value=False)
        cm.read = mock.Mock(return_value=body)
        return cm

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)

    poster.create_ref(repo, "test-branch", "abc123")
    poster.create_pull_request(repo, "title", "body", "test-branch", "main")

    assert any(
        f"/repos/{repo}/git/refs" in u for u in captured_urls
    ), "create_ref should POST to /repos/{repo}/git/refs"
    assert any(
        f"/repos/{repo}/pulls" in u for u in captured_urls
    ), "create_pull_request should POST to /repos/{repo}/pulls"
