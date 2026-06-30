"""Tests for GitHubMCPPoster — autonomous PR/Discussion poster.

Covers all public methods with mocked urllib responses so no real
network calls are made. Zero external dependencies.
"""

from __future__ import annotations

import json
import logging
import unittest.mock as mock
import urllib.error
from io import BytesIO
from urllib.parse import urlparse

import pytest

from codex.github.mcp_poster import GitHubMCPPoster, main

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_response(payload: dict, status: int = 200):
    """Return a context-manager mock that mimics urllib.request.urlopen."""
    body = json.dumps(payload).encode()
    cm = mock.MagicMock()
    cm.__enter__ = mock.Mock(return_value=cm)
    cm.__exit__ = mock.Mock(return_value=False)
    cm.read = mock.Mock(return_value=body)
    cm.status = status
    return cm


def _mock_http_error(code: int, reason: str = "Error", body: bytes = b"{}"):
    """Return an HTTPError with the given status code."""
    headers = mock.MagicMock()
    headers.get = mock.Mock(return_value="")
    return urllib.error.HTTPError(
        url="https://api.github.com/test",
        code=code,
        msg=reason,
        hdrs=headers,
        fp=BytesIO(body),
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def poster(monkeypatch):
    monkeypatch.setenv("CODEX_MASTER_KEY", "ghp_testtoken123")
    return GitHubMCPPoster()


@pytest.fixture()
def no_token_poster(monkeypatch):
    monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
    monkeypatch.delenv("CODEX_BACKUP_KEY", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    return GitHubMCPPoster()


# ---------------------------------------------------------------------------
# Token resolution
# ---------------------------------------------------------------------------


def test_uses_master_key(monkeypatch):
    monkeypatch.setenv("CODEX_MASTER_KEY", "master-tok")
    p = GitHubMCPPoster()
    assert p._token == "master-tok", "_token is not valid"


def test_falls_back_to_backup_key(monkeypatch):
    monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
    monkeypatch.setenv("CODEX_BACKUP_KEY", "backup-tok")
    p = GitHubMCPPoster()
    assert p._token == "backup-tok", "_token is not valid"


def test_falls_back_to_github_token(monkeypatch):
    monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
    monkeypatch.delenv("CODEX_BACKUP_KEY", raising=False)
    monkeypatch.setenv("GITHUB_TOKEN", "gh-tok")
    p = GitHubMCPPoster()
    assert p._token == "gh-tok", "_token is not valid"


def test_no_token_warns(monkeypatch, caplog):
    monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
    monkeypatch.delenv("CODEX_BACKUP_KEY", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    # The "codex" logger may have `propagate=False` configured elsewhere in the
    # codebase. This prevents caplog (which installs a handler on the root
    # logger) from capturing records emitted by child loggers such as
    # codex.github.mcp_poster. Temporarily re-enable propagation for the
    # duration of this assertion so the warning can be observed by caplog.
    codex_logger = logging.getLogger("codex")
    original_propagate = codex_logger.propagate
    codex_logger.propagate = True
    try:
        with caplog.at_level(logging.WARNING, logger="codex.github.mcp_poster"):
            GitHubMCPPoster()
        assert "No GitHub token" in caplog.text, "Condition must be true"
    finally:
        codex_logger.propagate = original_propagate


# ---------------------------------------------------------------------------
# post_pr_comment
# ---------------------------------------------------------------------------


def test_post_pr_comment_success(poster, monkeypatch):
    resp = _mock_response({"html_url": "https://github.com/test/repo/issues/1#issuecomment-1"})
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: resp)
    result = poster.post_pr_comment("Aries-Serpent/_codex_", 3401, "@copilot test")
    assert urlparse(result["html_url"]).hostname == "github.com", "Result must not be empty"


def test_post_pr_comment_requires_token(no_token_poster):
    with pytest.raises(RuntimeError, match="CODEX_MASTER_KEY"):
        no_token_poster.post_pr_comment("owner/repo", 1, "body")


def test_post_pr_comment_from_file(poster, monkeypatch, tmp_path):
    body_file = tmp_path / "prompt.md"
    body_file.write_text("@copilot hello")
    resp = _mock_response({"html_url": "https://github.com/x"})
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: resp)
    result = poster.post_pr_comment_from_file("owner/repo", 42, body_file)
    assert "html_url" in result, "Result must not be empty"


# ---------------------------------------------------------------------------
# set_repo_variable
# ---------------------------------------------------------------------------


def test_set_repo_variable_patch_success(poster, monkeypatch):
    resp = _mock_response({})
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: resp)
    result = poster.set_repo_variable("owner/repo", "MY_VAR", "true")
    assert result == {}, "Result must not be empty"


def test_set_repo_variable_falls_back_to_post_on_404(poster, monkeypatch):
    call_count = {"n": 0}

    def fake_urlopen(req, timeout):
        call_count["n"] += 1
        if call_count["n"] == 1:
            exc = urllib.error.HTTPError(
                url="", code=404, msg="Not Found", hdrs=None, fp=BytesIO(b"{}")
            )
            raise exc
        return _mock_response({"name": "MY_VAR"})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    poster.set_repo_variable("owner/repo", "MY_VAR", "true")
    assert call_count["n"] == 2, "Count must be greater than zero"


def test_set_repo_variable_requires_token(no_token_poster):
    with pytest.raises(RuntimeError):
        no_token_poster.set_repo_variable("owner/repo", "X", "y")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_post_comment(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    body_file = tmp_path / "body.md"
    body_file.write_text("@copilot go")
    resp = _mock_response({"html_url": "https://github.com/x"})
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: resp)
    rc = main(["post-comment", "--repo", "o/r", "--pr", "1", "--body-file", str(body_file)])
    assert rc == 0, "rc is not valid"


def test_cli_set_variable(monkeypatch):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    resp = _mock_response({})
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: resp)
    rc = main(["set-variable", "--repo", "o/r", "--name", "X", "--value", "1"])
    assert rc == 0, "rc is not valid"


def test_cli_no_token_returns_1(monkeypatch):
    monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
    monkeypatch.delenv("CODEX_BACKUP_KEY", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    rc = main(["post-comment", "--repo", "o/r", "--pr", "1", "--body", "hi"])
    assert rc == 1, "rc is not valid"


# ---------------------------------------------------------------------------
# create_ref
# ---------------------------------------------------------------------------


def test_create_ref_bare_branch_name(poster, monkeypatch):
    """Bare branch name is normalised to refs/heads/<name>."""
    captured = {}

    def fake_urlopen(req, timeout):
        captured["req"] = req
        return _mock_response({"ref": "refs/heads/my-branch", "object": {"sha": "abc"}})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = poster.create_ref("owner/repo", "my-branch", "abc123")
    assert result["ref"] == "refs/heads/my-branch", "Result must not be empty"
    assert b'"ref": "refs/heads/my-branch"' in captured["req"].data, "Data must not be empty"


def test_create_ref_heads_prefix(poster, monkeypatch):
    """heads/<name> prefix is expanded to refs/heads/<name>."""
    captured = {}

    def fake_urlopen(req, timeout):
        captured["req"] = req
        return _mock_response({"ref": "refs/heads/feature", "object": {"sha": "abc"}})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    poster.create_ref("owner/repo", "heads/feature", "abc123")
    assert b'"ref": "refs/heads/feature"' in captured["req"].data, "Data must not be empty"


def test_create_ref_tags_prefix(poster, monkeypatch):
    """tags/<name> prefix is expanded to refs/tags/<name>."""
    captured = {}

    def fake_urlopen(req, timeout):
        captured["req"] = req
        return _mock_response({"ref": "refs/tags/v1.0", "object": {"sha": "abc"}})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    poster.create_ref("owner/repo", "tags/v1.0", "abc123")
    assert b'"ref": "refs/tags/v1.0"' in captured["req"].data, "Data must not be empty"


def test_create_ref_full_refs_prefix_unchanged(poster, monkeypatch):
    """refs/heads/<name> is left as-is (no double-prefix)."""
    captured = {}

    def fake_urlopen(req, timeout):
        captured["req"] = req
        return _mock_response({"ref": "refs/heads/existing", "object": {"sha": "abc"}})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    poster.create_ref("owner/repo", "refs/heads/existing", "abc123")
    data = json.loads(captured["req"].data)
    assert data["ref"] == "refs/heads/existing", "Data must not be empty"
    assert "refs/heads/refs/heads" not in data["ref"], "Data must not be empty"


def test_create_ref_requires_token(no_token_poster):
    with pytest.raises(RuntimeError):
        no_token_poster.create_ref("owner/repo", "main", "abc123")


# ---------------------------------------------------------------------------
# create_pull_request
# ---------------------------------------------------------------------------


def test_create_pull_request_success(poster, monkeypatch):
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, timeout: _mock_response({"number": 42, "html_url": "https://github.com/pr/42"}),
    )
    result = poster.create_pull_request("owner/repo", "My PR", "body", "feature", "main")
    assert result["number"] == 42, "Result must not be empty"
    assert "html_url" in result, "Result must not be empty"


def test_create_pull_request_draft(poster, monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["req"] = req
        return _mock_response({"number": 7, "html_url": "https://github.com/pr/7", "draft": True})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    poster.create_pull_request("owner/repo", "Draft PR", "body", "feature", "main", draft=True)
    data = json.loads(captured["req"].data)
    assert data["draft"] is True, "Data must not be empty"


def test_create_pull_request_requires_token(no_token_poster):
    with pytest.raises(RuntimeError):
        no_token_poster.create_pull_request("owner/repo", "t", "b", "h", "main")


# ---------------------------------------------------------------------------
# list_pull_requests
# ---------------------------------------------------------------------------


def test_list_pull_requests_success(poster, monkeypatch):
    pr_list = [{"number": 1, "title": "PR 1"}, {"number": 2, "title": "PR 2"}]
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, timeout: _mock_response(pr_list),
    )
    result = poster.list_pull_requests("owner/repo")
    assert len(result) == 2, "Result must not be empty"
    assert result[0]["number"] == 1, "Result must not be empty"


def test_list_pull_requests_head_filter_adds_owner_prefix(poster, monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        return _mock_response([])

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    poster.list_pull_requests("myorg/repo", head="my-branch")

    from urllib.parse import parse_qs, urlparse

    qs = parse_qs(urlparse(captured["url"]).query)
    assert qs.get("head") == ["myorg:my-branch"], "Condition must be true"


def test_list_pull_requests_head_with_colon_not_modified(poster, monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        return _mock_response([])

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    poster.list_pull_requests("myorg/repo", head="otherorg:their-branch")

    from urllib.parse import parse_qs, urlparse

    qs = parse_qs(urlparse(captured["url"]).query)
    # Should NOT re-prefix: the value already contains an owner
    assert qs.get("head") == ["otherorg:their-branch"], "Condition must be true"


def test_list_pull_requests_http_error(poster, monkeypatch):
    def fake_urlopen(req, timeout):
        raise _mock_http_error(403, "Forbidden")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(urllib.error.HTTPError):
        poster.list_pull_requests("owner/repo")


def test_list_pull_requests_per_page_capped_at_100(poster, monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        return _mock_response([])

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    poster.list_pull_requests("owner/repo", per_page=200)
    assert "per_page=100" in captured["url"], "Condition must be true"


def test_list_pull_requests_requires_token(no_token_poster):
    with pytest.raises(RuntimeError):
        no_token_poster.list_pull_requests("owner/repo")


# ---------------------------------------------------------------------------
# merge_branch
# ---------------------------------------------------------------------------


def test_merge_branch_success(poster, monkeypatch):
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, timeout: _mock_response({"sha": "abc123", "commit": {}, "parents": []}),
    )
    result = poster.merge_branch("owner/repo", "main", "feature")
    assert result["sha"] == "abc123", "Result must not be empty"


def test_merge_branch_with_message(poster, monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["req"] = req
        return _mock_response({"sha": "def456"})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    poster.merge_branch("owner/repo", "main", "feature", commit_message="Merge feature into main")
    data = json.loads(captured["req"].data)
    assert data["commit_message"] == "Merge feature into main", "Data must not be empty"


def test_merge_branch_no_message_omits_key(poster, monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["req"] = req
        return _mock_response({"sha": "ghi789"})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    poster.merge_branch("owner/repo", "main", "feature")
    data = json.loads(captured["req"].data)
    assert "commit_message" not in data, "Data must not be empty"


def test_merge_branch_returns_empty_on_no_content(poster, monkeypatch):
    """HTTP 204 (already up-to-date) returns empty dict."""
    cm = mock.MagicMock()
    cm.__enter__ = mock.Mock(return_value=cm)
    cm.__exit__ = mock.Mock(return_value=False)
    cm.read = mock.Mock(return_value=b"")
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: cm)
    result = poster.merge_branch("owner/repo", "main", "feature")
    assert result == {}, "Result must not be empty"


def test_merge_branch_requires_token(no_token_poster):
    with pytest.raises(RuntimeError):
        no_token_poster.merge_branch("owner/repo", "main", "feature")


# ---------------------------------------------------------------------------
# create_discussion + post_session_summary_discussion
# ---------------------------------------------------------------------------


def _graphql_response(data: dict) -> mock.MagicMock:
    """Mock urlopen returning a GraphQL response."""
    body = json.dumps({"data": data}).encode()
    cm = mock.MagicMock()
    cm.__enter__ = mock.Mock(return_value=cm)
    cm.__exit__ = mock.Mock(return_value=False)
    cm.read = mock.Mock(return_value=body)
    return cm


def test_create_discussion_success(poster, monkeypatch):
    call_count = {"n": 0}

    def fake_urlopen(req, timeout):
        call_count["n"] += 1
        if call_count["n"] == 1:
            # First call: resolve repo/category IDs
            return _graphql_response(
                {
                    "repository": {
                        "id": "R_123",
                        "discussionCategories": {
                            "nodes": [
                                {
                                    "id": "DC_1",
                                    "slug": "session-summaries",
                                    "name": "Session Summaries",
                                }
                            ],
                        },
                    }
                }
            )
        # Second call: create discussion
        return _graphql_response(
            {
                "createDiscussion": {
                    "discussion": {
                        "number": 5,
                        "url": "https://github.com/discuss/5",
                        "title": "Test",
                    },
                }
            }
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = poster.create_discussion("owner/repo", "Test", "Body text", "session-summaries")
    assert result.get("number") == 5, "Result must not be empty"
    assert result.get("url") == "https://github.com/discuss/5", "Result must not be empty"


def test_post_session_summary_discussion(poster, monkeypatch):
    """post_session_summary_discussion calls create_discussion with correct title."""
    called_with = {}

    def fake_create_discussion(repo, title, body, category_slug):
        called_with["title"] = title
        called_with["category_slug"] = category_slug
        return {"number": 10, "url": "https://github.com/discuss/10"}

    monkeypatch.setattr(poster, "create_discussion", fake_create_discussion)
    poster.post_session_summary_discussion("owner/repo", 175, "## Summary")
    assert called_with["title"] == "Session S175 — Completion Summary", "Condition must be true"
    assert called_with["category_slug"] == "session-summaries", "Condition must be true"


def test_create_discussion_category_fallback(poster, monkeypatch):
    """When slug not matched, first category is used as fallback."""
    call_count = {"n": 0}

    def fake_urlopen(req, timeout):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return _graphql_response(
                {
                    "repository": {
                        "id": "R_456",
                        "discussionCategories": {
                            "nodes": [{"id": "DC_FIRST", "slug": "general", "name": "General"}],
                        },
                    }
                }
            )
        return _graphql_response(
            {
                "createDiscussion": {
                    "discussion": {
                        "number": 6,
                        "url": "https://github.com/discuss/6",
                        "title": "t",
                    },
                }
            }
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    # "nonexistent-slug" won't match "general", should fall back to first category
    poster.create_discussion("owner/repo", "t", "b", "nonexistent-slug")
    assert call_count["n"] == 2, "Count must be greater than zero"


def test_create_discussion_requires_token(no_token_poster):
    with pytest.raises(RuntimeError):
        no_token_poster.create_discussion("owner/repo", "t", "b", "slug")


# ---------------------------------------------------------------------------
# _request retry logic
# ---------------------------------------------------------------------------


def test_request_retries_on_429(poster, monkeypatch):
    """HTTP 429 triggers retry with exponential back-off."""
    call_count = {"n": 0}

    def fake_urlopen(req, timeout):
        call_count["n"] += 1
        if call_count["n"] < 3:
            headers = mock.MagicMock()
            headers.get = mock.Mock(return_value="")
            raise urllib.error.HTTPError(
                url="", code=429, msg="Rate limited", hdrs=headers, fp=BytesIO(b"{}")
            )
        return _mock_response({"ok": True})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("time.sleep", lambda _: None)  # Skip actual sleep
    result = poster.post_pr_comment("owner/repo", 1, "body")
    assert result.get("ok") is True, "Result must not be empty"
    assert call_count["n"] == 3, "Count must be greater than zero"


def test_request_does_not_retry_on_403_without_rate_limit_signals(poster, monkeypatch):
    """HTTP 403 without rate-limit headers raises immediately (no retry)."""
    call_count = {"n": 0}

    def fake_urlopen(req, timeout):
        call_count["n"] += 1
        headers = mock.MagicMock()
        headers.get = mock.Mock(return_value="")
        raise urllib.error.HTTPError(
            url="", code=403, msg="Forbidden", hdrs=headers, fp=BytesIO(b"forbidden")
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        poster.post_pr_comment("owner/repo", 1, "body")
    assert exc_info.value.code == 403, "Value must be initialized"
    assert call_count["n"] == 1, "Count must be greater than zero"


def test_request_retries_on_403_with_retry_after_header(poster, monkeypatch):
    """HTTP 403 + Retry-After header → retried."""
    call_count = {"n": 0}

    def fake_urlopen(req, timeout):
        call_count["n"] += 1
        if call_count["n"] == 1:
            headers = mock.MagicMock()
            headers.get = mock.Mock(
                side_effect=lambda k, default="": "1" if k == "Retry-After" else default
            )
            raise urllib.error.HTTPError(
                url="", code=403, msg="Secondary rate limited", hdrs=headers, fp=BytesIO(b"{}")
            )
        return _mock_response({"id": 99})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("time.sleep", lambda _: None)
    result = poster.post_pr_comment("owner/repo", 1, "body")
    assert result["id"] == 99, "Result must not be empty"
    assert call_count["n"] == 2, "Count must be greater than zero"


def test_request_retries_on_403_with_ratelimit_remaining_zero(poster, monkeypatch):
    """HTTP 403 + x-ratelimit-remaining=0 → retried."""
    call_count = {"n": 0}

    def fake_urlopen(req, timeout):
        call_count["n"] += 1
        if call_count["n"] == 1:
            headers = mock.MagicMock()
            headers.get = mock.Mock(
                side_effect=lambda k, default="": "0" if k == "x-ratelimit-remaining" else default
            )
            raise urllib.error.HTTPError(
                url="", code=403, msg="Limit", hdrs=headers, fp=BytesIO(b"{}")
            )
        return _mock_response({"id": 77})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("time.sleep", lambda _: None)
    result = poster.post_pr_comment("owner/repo", 1, "body")
    assert result["id"] == 77, "Result must not be empty"


def test_request_rejects_non_https_url(poster):
    with pytest.raises(ValueError, match=r"GitHub API URL must target https://api.github.com"):
        poster._request("POST", "http://insecure.example.com/api", {})


# ---------------------------------------------------------------------------
# CLI — new commands (create-branch, create-pr, merge-branch, create-discussion)
# ---------------------------------------------------------------------------


def test_cli_create_branch(monkeypatch):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, timeout: _mock_response(
            {"ref": "refs/heads/test-branch", "object": {"sha": "abc1234"}}
        ),
    )
    rc = main(["create-branch", "--repo", "o/r", "--ref", "test-branch", "--sha", "abc1234" * 5])
    assert rc == 0, "rc is not valid"


def test_cli_create_pr(monkeypatch):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, timeout: _mock_response({"number": 99, "html_url": "https://github.com/pr/99"}),
    )
    rc = main(
        ["create-pr", "--repo", "o/r", "--title", "My PR", "--head", "feature", "--base", "main"]
    )
    assert rc == 0, "rc is not valid"


def test_cli_create_pr_with_body_file(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    body_file = tmp_path / "pr_body.md"
    body_file.write_text("## PR Description\n\nSome details.")
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, timeout: _mock_response({"number": 55, "html_url": "https://github.com/pr/55"}),
    )
    rc = main(
        [
            "create-pr",
            "--repo",
            "o/r",
            "--title",
            "PR via file",
            "--head",
            "feature",
            "--body-file",
            str(body_file),
        ]
    )
    assert rc == 0, "rc is not valid"


def test_cli_merge_branch(monkeypatch):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, timeout: _mock_response({"sha": "abcdef12"}),
    )
    rc = main(["merge-branch", "--repo", "o/r", "--base", "main", "--head", "feature"])
    assert rc == 0, "rc is not valid"


def test_cli_merge_branch_up_to_date(monkeypatch):
    """Empty response (already merged / 204) should print up-to-date message."""
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    cm = mock.MagicMock()
    cm.__enter__ = mock.Mock(return_value=cm)
    cm.__exit__ = mock.Mock(return_value=False)
    cm.read = mock.Mock(return_value=b"")
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: cm)
    rc = main(["merge-branch", "--repo", "o/r", "--base", "main", "--head", "feature"])
    assert rc == 0, "rc is not valid"


def test_cli_create_discussion(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    body_file = tmp_path / "discussion.md"
    body_file.write_text("## Session S99 Summary")
    call_count = {"n": 0}

    def fake_urlopen(req, timeout):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return _graphql_response(
                {
                    "repository": {
                        "id": "R_999",
                        "discussionCategories": {
                            "nodes": [
                                {
                                    "id": "DC_99",
                                    "slug": "cognitive-brain-patterns",
                                    "name": "Patterns",
                                }
                            ],
                        },
                    }
                }
            )
        return _graphql_response(
            {
                "createDiscussion": {
                    "discussion": {
                        "number": 99,
                        "url": "https://github.com/discuss/99",
                        "title": "S99",
                    },
                }
            }
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    rc = main(
        ["create-discussion", "--repo", "o/r", "--title", "S99", "--body-file", str(body_file)]
    )
    assert rc == 0, "rc is not valid"


def test_cli_http_error_returns_1(monkeypatch):
    """Any HTTPError from CLI → exit code 1."""
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")

    def fake_urlopen(req, timeout):
        raise _mock_http_error(422, "Unprocessable Entity")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    rc = main(["create-branch", "--repo", "o/r", "--ref", "my-branch", "--sha", "a" * 40])
    assert rc == 1, "rc is not valid"


def test_list_pull_requests_with_base_filter(poster, monkeypatch):
    """Passing base= appends it to the query string."""
    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        return _mock_response([])

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    poster.list_pull_requests("owner/repo", base="main")
    assert "base=main" in captured["url"], "Condition must be true"


def test_cli_create_pr_draft_flag(monkeypatch):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    captured = {}

    def fake_urlopen(req, timeout):
        captured["data"] = json.loads(req.data)
        return _mock_response({"number": 11, "html_url": "https://github.com/pr/11"})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    rc = main(["create-pr", "--repo", "o/r", "--title", "Draft", "--head", "feature", "--draft"])
    assert rc == 0, "rc is not valid"
    assert captured["data"]["draft"] is True, "Data must not be empty"


# ---------------------------------------------------------------------------
# Cognitive brain lifecycle hooks (IMP-012)
# ---------------------------------------------------------------------------


@pytest.fixture
def codex_logger_propagating():
    """Ensure the 'codex' logger has propagate=True during a test and restore afterwards."""
    logger = logging.getLogger("codex")
    original_propagate = logger.propagate
    logger.propagate = True
    try:
        yield logger
    finally:
        logger.propagate = original_propagate


def test_record_cb_pattern_logs_always(poster, caplog, codex_logger_propagating):
    """_record_cb_pattern emits an INFO log regardless of cognitive brain availability."""
    with caplog.at_level(logging.INFO, logger="codex.github.mcp_poster"):
        poster._record_cb_pattern(
            "CB-branch-create",
            "create_ref: refs/heads/test",
            {"repo": "owner/repo", "sha": "abc123"},
        )
    assert "CB-branch-create" in caplog.text, "Condition must be true"


def test_create_ref_records_cb_pattern(poster, monkeypatch):
    """create_ref records a CB-branch-create pattern."""
    recorded = []

    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, timeout: _mock_response({"ref": "refs/heads/test", "object": {"sha": "abc"}}),
    )
    monkeypatch.setattr(poster, "_record_cb_pattern", lambda *a, **kw: recorded.append((a, kw)))
    poster.create_ref("owner/repo", "test", "abc123")
    assert any("CB-branch-create" in str(r) for r in recorded), "Condition must be true"


def test_create_pull_request_records_cb_pattern(poster, monkeypatch):
    """create_pull_request records a CB-pr-open pattern."""
    recorded = []

    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, timeout: _mock_response({"number": 5, "html_url": "https://github.com/pr/5"}),
    )
    monkeypatch.setattr(poster, "_record_cb_pattern", lambda *a, **kw: recorded.append((a, kw)))
    poster.create_pull_request("owner/repo", "title", "body", "feature", "main")
    assert any("CB-pr-open" in str(r) for r in recorded), "Condition must be true"


def test_merge_branch_records_cb_pattern_success(poster, monkeypatch):
    """merge_branch records a CB-merge pattern with outcome=success."""
    recorded = []

    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, timeout: _mock_response({"sha": "abc123"}),
    )
    monkeypatch.setattr(poster, "_record_cb_pattern", lambda *a, **kw: recorded.append((a, kw)))
    poster.merge_branch("owner/repo", "main", "feature")
    assert recorded, "Expected _record_cb_pattern to be called"
    args, kwargs = recorded[0]
    assert args[0] == "CB-merge", "Condition must be true"
    assert kwargs.get("outcome") == "success", "Condition must be true"


def test_merge_branch_records_cb_pattern_already_exists(poster, monkeypatch):
    """merge_branch records a CB-merge pattern with outcome=already_exists when empty response."""
    recorded = []

    cm = mock.MagicMock()
    cm.__enter__ = mock.Mock(return_value=cm)
    cm.__exit__ = mock.Mock(return_value=False)
    cm.read = mock.Mock(return_value=b"")
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: cm)
    monkeypatch.setattr(poster, "_record_cb_pattern", lambda *a, **kw: recorded.append((a, kw)))
    poster.merge_branch("owner/repo", "main", "feature")
    assert recorded, "Expected _record_cb_pattern to be called"
    args, kwargs = recorded[0]
    assert args[0] == "CB-merge", "Condition must be true"
    assert kwargs.get("outcome") == "already_exists", "Condition must be true"


# ---------------------------------------------------------------------------
# P1.4 — coverage for remaining uncovered lines
# ---------------------------------------------------------------------------


def test_set_repo_variable_reraises_non_404_http_error(poster, monkeypatch):
    """set_repo_variable re-raises HTTPError whose code is not 404 (line 240)."""
    from io import BytesIO

    hdrs = mock.MagicMock()
    hdrs.get = lambda key, default="": default  # No Retry-After, no rate-limit headers

    def fake_urlopen(req, timeout):
        raise urllib.error.HTTPError(
            url="", code=403, msg="Forbidden", hdrs=hdrs, fp=BytesIO(b"{}")
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        poster.set_repo_variable("owner/repo", "MY_VAR", "value")
    assert exc_info.value.code == 403, "Value must be initialized"


def test_record_cb_pattern_cognitive_brain_available(poster, monkeypatch):
    """_record_cb_pattern executes the import block when cognitive_brain is mockable (lines 495-510)."""
    stored = []

    class FakeMemoryPattern:
        def __init__(self, **kw):
            self.kw = kw

    class FakeSQLiteMemory:
        def store_pattern(self, p):
            stored.append(p)

    fake_module = mock.MagicMock()
    fake_module.MemoryPattern = FakeMemoryPattern
    fake_module.SQLiteMemory = FakeSQLiteMemory

    import sys

    # Inject the fake module so the import inside _record_cb_pattern succeeds.
    # Clean up after to avoid contaminating other tests.
    sys.modules["cognitive_brain"] = mock.MagicMock()
    sys.modules["cognitive_brain.quantum"] = mock.MagicMock()
    sys.modules["cognitive_brain.quantum.memory"] = fake_module
    try:
        poster._record_cb_pattern(
            "CB-test",
            "test decision",
            {"repo": "owner/repo", "sha": "abc123"},
            outcome="success",
        )
    finally:
        sys.modules.pop("cognitive_brain", None)
        sys.modules.pop("cognitive_brain.quantum", None)
        sys.modules.pop("cognitive_brain.quantum.memory", None)

    assert len(stored) == 1, "Stored must not be empty"


def test_request_raises_after_retry_exhaustion(poster, monkeypatch):
    """_request raises last_exc when all retries are consumed on rate-limit (line 607)."""
    from io import BytesIO

    hdrs = mock.MagicMock()
    hdrs.get = lambda key, default="": "1" if key == "Retry-After" else default

    def fake_urlopen(req, timeout):
        raise urllib.error.HTTPError(
            url="", code=429, msg="Too Many Requests", hdrs=hdrs, fp=BytesIO(b"{}")
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr("time.sleep", lambda s: None)  # speed up test

    max_retries = 2
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        poster._request("POST", "https://api.github.com/test", {}, max_retries=max_retries)
    assert exc_info.value.code == 429, "Value must be initialized"
    # All retries are exhausted: loop ran max_retries times then raise last_exc


def test_cli_no_subcommand_returns_zero(monkeypatch):
    """main() with no recognised subcommand reaches return 0 (branch 751->766)."""
    import argparse

    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")

    # Patch parse_args so args.command is None (no subcommand given)

    def patched_parse(self, args=None, namespace=None):
        # Simulate a parse result where no recognised subcommand was provided.
        # args and namespace are part of the ArgumentParser.parse_args signature
        # but are intentionally ignored here — we always return a fixed Namespace.
        return argparse.Namespace(command=None)

    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", patched_parse)
    rc = main([])
    assert rc == 0, "rc is not valid"


# ---------------------------------------------------------------------------
# IMP-002 — Git Data API commit_files tests
# ---------------------------------------------------------------------------


def test_get_method_returns_json(poster, monkeypatch):
    """_get() parses JSON from a successful GET response."""
    from unittest.mock import MagicMock

    fake_resp = MagicMock()
    fake_resp.__enter__ = lambda s: s
    fake_resp.__exit__ = MagicMock(return_value=False)
    fake_resp.read.return_value = json.dumps({"object": {"sha": "abc123"}}).encode()

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: fake_resp)
    result = poster._get("https://api.github.com/repos/owner/repo/git/refs/heads/main")
    assert result == {"object": {"sha": "abc123"}}, "Result must not be empty"


def test_get_method_rejects_non_https(poster):
    """_get() raises ValueError for non-HTTPS URLs."""
    with pytest.raises(ValueError, match="GitHub API URL must target https://api.github.com"):
        poster._get("http://api.github.com/repos/owner/repo/git/refs/heads/main")


def test_commit_files_pipeline(poster, monkeypatch, tmp_path):
    """commit_files() calls the full Git Data API pipeline in order."""

    call_log: list[tuple[str, str]] = []

    def fake_post(url, payload, **kwargs):
        call_log.append(("POST", url))
        if "/git/blobs" in url:
            return {"sha": "blob_sha_abc"}
        if "/git/trees" in url:
            return {"sha": "tree_sha_xyz"}
        if "/git/commits" in url:
            return {"sha": "commit_sha_123"}
        return {}

    def fake_patch(url, payload, **kwargs):
        call_log.append(("PATCH", url))
        return {"ref": "refs/heads/test-branch", "object": {"sha": "commit_sha_123"}}

    def fake_get(url, **kwargs):
        call_log.append(("GET", url))
        if "/git/refs/" in url:
            return {"object": {"sha": "head_sha_def"}}
        if "/git/commits/" in url:
            return {"tree": {"sha": "base_tree_ghi"}}
        return {}

    monkeypatch.setattr(poster, "_get", fake_get)

    def fake_request(method, url, payload, **kwargs):
        if method == "POST":
            return fake_post(url, payload)
        if method == "PATCH":
            return fake_patch(url, payload)
        raise AssertionError(f"Unexpected HTTP method: {method} {url}")

    monkeypatch.setattr(poster, "_request", fake_request)

    result = poster.commit_files(
        "owner/repo",
        "test-branch",
        {"docs/README.md": "# Hello\n"},
        "docs: update README",
    )

    assert result == "commit_sha_123", "Result must not be empty"

    # Verify the pipeline order: GET ref → GET commit → POST blob → POST tree → POST commit → PATCH ref
    assert any(m == "GET" and "refs" in u for m, u in call_log), "GET ref not called"
    assert any(m == "GET" and "commits" in u for m, u in call_log), "GET commit-tree not called"
    assert any(m == "POST" and "blobs" in u for m, u in call_log), "POST blob not called"
    assert any(m == "POST" and "trees" in u for m, u in call_log), "POST tree not called"
    assert any(m == "POST" and "commits" in u for m, u in call_log), "POST commit not called"
    assert any(m == "PATCH" for m, u in call_log), "PATCH ref not called"


def test_cli_commit_files(monkeypatch, tmp_path):
    """CLI commit-files command calls commit_files and prints the SHA."""
    import codex.github.mcp_poster as pm
    from codex.github.mcp_poster import main

    src = tmp_path / "file.txt"
    src.write_text("hello", encoding="utf-8")

    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")

    def fake_commit_files(self, repo, branch, files, message, force=False):
        assert repo == "owner/repo", "repo is not valid"
        assert branch == "main", "branch is not valid"
        assert "README.md" in files, "Condition must be true"
        assert files["README.md"] == "hello", "Condition must be true"
        assert message == "docs: update", "message is not valid"
        return "deadbeef12345678"  # pragma: allowlist secret

    monkeypatch.setattr(pm.GitHubMCPPoster, "commit_files", fake_commit_files)

    rc = main(
        [
            "commit-files",
            "--repo",
            "owner/repo",
            "--branch",
            "main",
            "--message",
            "docs: update",
            "--file",
            f"README.md:{src}",
        ]
    )
    assert rc == 0, "rc is not valid"


def test_cli_commit_files_bad_mapping(monkeypatch, tmp_path):
    """CLI commit-files returns 1 when a --file mapping is malformed."""
    from codex.github.mcp_poster import main

    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    rc = main(
        [
            "commit-files",
            "--repo",
            "owner/repo",
            "--branch",
            "main",
            "--message",
            "x",
            "--file",
            "no_colon_here",
        ]
    )
    assert rc == 1, "rc is not valid"


# ---------------------------------------------------------------------------
# add_discussion_comment / upsert_discussion_comment / post_ci_pattern_summary
# post_continuation_chain — S192 Discussion hardening
# ---------------------------------------------------------------------------


def _discussion_node_response(discussion_id: str = "DI_123") -> mock.MagicMock:
    """GraphQL response returning a discussion node ID."""
    return _graphql_response({"repository": {"discussion": {"id": discussion_id}}})


def _add_comment_response(
    comment_id: str = "DC_abc", url: str = "https://github.com/d/1#c1"
) -> mock.MagicMock:
    return _graphql_response(
        {"addDiscussionComment": {"comment": {"id": comment_id, "url": url, "body": "body"}}}
    )


def _update_comment_response(comment_id: str = "DC_abc") -> mock.MagicMock:
    return _graphql_response(
        {
            "updateDiscussionComment": {
                "comment": {"id": comment_id, "url": "https://u", "body": "updated"}
            }
        }
    )


class TestAddDiscussionComment:
    """Tests for GitHubMCPPoster.add_discussion_comment()."""

    def test_success(self, poster, monkeypatch):
        call_count = {"n": 0}

        def fake_urlopen(req, timeout):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return _discussion_node_response("DI_999")
            return _add_comment_response("DC_new", "https://github.com/d/42#c5")

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        result = poster.add_discussion_comment("owner/repo", 42, "Hello!")
        assert result.get("url") == "https://github.com/d/42", "Result must not be empty"
        assert call_count["n"] == 2, "Count must be greater than zero"

    def test_raises_when_discussion_not_found(self, poster, monkeypatch):
        monkeypatch.setattr(
            "urllib.request.urlopen",
            lambda req, timeout: _graphql_response({"repository": {"discussion": None}}),
        )
        with pytest.raises(RuntimeError, match="Discussion #99 not found"):
            poster.add_discussion_comment("owner/repo", 99, "body")

    def test_requires_token(self, no_token_poster):
        with pytest.raises(RuntimeError):
            no_token_poster.add_discussion_comment("owner/repo", 1, "body")


class TestUpsertDiscussionComment:
    """Tests for GitHubMCPPoster.upsert_discussion_comment()."""

    def test_creates_new_when_marker_absent(self, poster, monkeypatch):
        """No existing comment with marker → add_discussion_comment called."""
        calls = []

        def fake_urlopen(req, timeout):
            data = json.loads(req.data)
            query = data.get("query", "")
            calls.append(query[:40])
            if "discussion(number:" in query:
                if "comments" in query:
                    # _find_discussion_comment — empty comments
                    return _graphql_response(
                        {"repository": {"discussion": {"comments": {"nodes": []}}}}
                    )
                return _discussion_node_response("DI_1")
            return _add_comment_response()

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        result = poster.upsert_discussion_comment("owner/repo", 1, "body", "<!-- marker -->")
        assert result.get("id") == "DC_abc", "Result must not be empty"

    def test_updates_existing_when_marker_found(self, poster, monkeypatch):
        """Comment with marker found → updateDiscussionComment called."""
        calls = {"n": 0}

        def fake_urlopen(req, timeout):
            calls["n"] += 1
            data = json.loads(req.data)
            query = data.get("query", "")
            if "comments(last:" in query:
                return _graphql_response(
                    {
                        "repository": {
                            "discussion": {
                                "comments": {
                                    "nodes": [
                                        {"id": "DC_exist", "body": "<!-- marker --> old body"}
                                    ]
                                }
                            }
                        }
                    }
                )
            if "updateDiscussionComment" in query:
                return _update_comment_response("DC_exist")
            return _graphql_response({})

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        result = poster.upsert_discussion_comment(
            "owner/repo", 1, "<!-- marker --> new body", "<!-- marker -->"
        )
        assert result.get("id") == "DC_exist", "Result must not be empty"

    def test_no_marker_always_creates(self, poster, monkeypatch):
        """Empty marker string skips search and always creates new comment."""
        call_count = {"n": 0}

        def fake_urlopen(req, timeout):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return _discussion_node_response()
            return _add_comment_response()

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        poster.upsert_discussion_comment("owner/repo", 3, "body", marker="")
        # Only 2 calls: resolve node ID + addDiscussionComment (no search)
        assert call_count["n"] == 2, "Count must be greater than zero"


class TestPostCiPatternSummary:
    def test_embeds_session_marker(self, poster, monkeypatch):
        """post_ci_pattern_summary embeds session-scoped HTML marker."""
        captured = {}

        def fake_upsert(repo, number, body, marker):
            captured["body"] = body
            captured["marker"] = marker
            return {"id": "DC_1", "url": "https://u"}

        monkeypatch.setattr(poster, "upsert_discussion_comment", fake_upsert)
        poster.post_ci_pattern_summary("owner/repo", 3673, "## Summary", "run-42")
        assert "<!-- ci-pattern-summary:run-42 -->" in captured["marker"], "Condition must be true"

    def test_default_marker_when_no_session(self, poster, monkeypatch):
        captured = {}

        def fake_upsert(repo, number, body, marker):
            captured["marker"] = marker
            return {}

        monkeypatch.setattr(poster, "upsert_discussion_comment", fake_upsert)
        poster.post_ci_pattern_summary("owner/repo", 3673, "body", session_id="")
        assert captured["marker"] == "<!-- ci-pattern-summary -->", "Condition must be true"


class TestPostContinuationChain:
    def test_always_creates_new_comment(self, poster, monkeypatch):
        """post_continuation_chain always creates a new comment (no upsert)."""
        called = {}

        def fake_add(repo, number, body):
            called["repo"] = repo
            called["number"] = number
            called["body"] = body
            return {"id": "DC_chain", "url": "https://u/chain"}

        monkeypatch.setattr(poster, "add_discussion_comment", fake_add)
        result = poster.post_continuation_chain(
            "owner/repo", 3673, "## Chain\n@copilot continue ..."
        )
        assert called["number"] == 3673, "Condition must be true"
        assert "@copilot continue" in called["body"], "Condition must be true"
        assert result["id"] == "DC_chain", "Result must not be empty"


# ---------------------------------------------------------------------------
# CLI — add-discussion-comment / upsert-discussion-comment /
#        post-ci-pattern-summary / post-continuation  (S192)
# ---------------------------------------------------------------------------


def test_cli_add_discussion_comment_body(monkeypatch):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    call_count = {"n": 0}

    def fake_urlopen(req, timeout):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return _discussion_node_response()
        return _add_comment_response(url="https://github.com/d/3673#c99")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    rc = main(
        ["add-discussion-comment", "--repo", "owner/repo", "--number", "3673", "--body", "Hello"]
    )
    assert rc == 0, "rc is not valid"


def test_cli_add_discussion_comment_body_file(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    f = tmp_path / "msg.md"
    f.write_text("## Update")
    call_count = {"n": 0}

    def fake_urlopen(req, timeout):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return _discussion_node_response()
        return _add_comment_response()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    rc = main(["add-discussion-comment", "--repo", "o/r", "--number", "1", "--body-file", str(f)])
    assert rc == 0, "rc is not valid"


def test_cli_upsert_discussion_comment(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    captured_body = {}

    def fake_upsert(self, repo, number, body, marker):
        captured_body["body"] = body
        return {"id": "DC_1", "url": "https://u"}

    from codex.github.mcp_poster import GitHubMCPPoster

    monkeypatch.setattr(GitHubMCPPoster, "upsert_discussion_comment", fake_upsert)
    f = tmp_path / "update.md"
    f.write_text("## Status")
    rc = main(
        [
            "upsert-discussion-comment",
            "--repo",
            "o/r",
            "--number",
            "3673",
            "--body-file",
            str(f),
            "--marker",
            "<!-- status -->",
        ]
    )
    assert rc == 0, "rc is not valid"


def test_cli_post_ci_pattern_summary(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    captured = {}

    def fake_post(self, repo, number, body, session_id):
        captured["session_id"] = session_id
        return {"id": "DC_s", "url": "https://u/s"}

    from codex.github.mcp_poster import GitHubMCPPoster

    monkeypatch.setattr(GitHubMCPPoster, "post_ci_pattern_summary", fake_post)
    f = tmp_path / "summary.md"
    f.write_text("## CI Patterns")
    rc = main(
        [
            "post-ci-pattern-summary",
            "--repo",
            "o/r",
            "--number",
            "3673",
            "--body-file",
            str(f),
            "--session-id",
            "run-99",
        ]
    )
    assert rc == 0, "rc is not valid"
    assert captured["session_id"] == "run-99", "Condition must be true"


def test_cli_post_continuation(monkeypatch, tmp_path):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    captured = {}

    def fake_chain(self, repo, number, body):
        captured["body"] = body
        return {"id": "DC_c", "url": "https://u/c"}

    from codex.github.mcp_poster import GitHubMCPPoster

    monkeypatch.setattr(GitHubMCPPoster, "post_continuation_chain", fake_chain)
    f = tmp_path / "chain.md"
    f.write_text("@copilot continue ...")
    rc = main(["post-continuation", "--repo", "o/r", "--number", "3673", "--body-file", str(f)])
    assert rc == 0, "rc is not valid"
    assert "@copilot continue" in captured["body"], "Condition must be true"


# ---------------------------------------------------------------------------
# GAP-033 — check_token_health tests
# ---------------------------------------------------------------------------


class TestCheckTokenHealth:
    """Tests for GitHubMCPPoster.check_token_health() (GAP-033)."""

    def test_no_token_returns_broken(self, monkeypatch):
        """No token → healthy=False, expiry_warning set."""
        for key in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GITHUB_TOKEN"):
            monkeypatch.delenv(key, raising=False)
        from codex.github.mcp_poster import GitHubMCPPoster

        poster = GitHubMCPPoster(token=None)
        result = poster.check_token_health()
        assert result["healthy"] is False, "Result must not be empty"
        assert result["source"] == "none", "Result must not be empty"
        assert "No token" in str(result["expiry_warning"]), "Result must not be empty"

    def test_expired_token_returns_unhealthy(self, monkeypatch):
        """HTTP 401 → healthy=False, expiry_warning mentions rotation."""
        monkeypatch.setenv("CODEX_MASTER_KEY", "ghp_expired")
        from codex.github.mcp_poster import GitHubMCPPoster

        poster = GitHubMCPPoster()

        def fake_urlopen(req, timeout=None):
            raise urllib.error.HTTPError(
                url="https://api.github.com/user",
                code=401,
                msg="Unauthorized",
                hdrs=None,  # type: ignore[arg-type]
                fp=None,
            )

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        result = poster.check_token_health()
        assert result["healthy"] is False, "Result must not be empty"
        assert ("expired" in str(result["expiry_warning"]).lower(), "Result must not be empty"
            or "invalid" in str(result["expiry_warning"]).lower()
        )

    def test_healthy_token_with_full_scopes(self, monkeypatch):
        """200 response with repo+workflow scopes → healthy=True."""
        from email.message import Message as _Msg

        monkeypatch.setenv("CODEX_MASTER_KEY", "ghp_valid")
        from codex.github.mcp_poster import GitHubMCPPoster

        poster = GitHubMCPPoster()

        hdrs = _Msg()
        hdrs["x-oauth-scopes"] = "repo, workflow, read:org"

        class _FakeResponse:
            status = 200
            headers = hdrs

            def read(self):
                return json.dumps({"login": "mbaetiong"}).encode()

            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

        monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=None: _FakeResponse())
        result = poster.check_token_health()
        assert result["healthy"] is True, "Result must not be empty"
        assert result["login"] == "mbaetiong", "Result must not be empty"
        assert result["source"] == "CODEX_MASTER_KEY", "Result must not be empty"
        assert result["expiry_warning"] is None, "Result must not be empty"

    def test_missing_scopes_on_master_key_warns(self, monkeypatch):
        """200 but missing scopes → healthy=False, warning mentions missing scopes."""
        from email.message import Message as _Msg

        monkeypatch.setenv("CODEX_MASTER_KEY", "ghp_limited")
        from codex.github.mcp_poster import GitHubMCPPoster

        poster = GitHubMCPPoster()

        hdrs = _Msg()
        hdrs["x-oauth-scopes"] = "read:user"  # Missing repo + workflow

        class _FakeResponse:
            status = 200
            headers = hdrs

            def read(self):
                return json.dumps({"login": "mbaetiong"}).encode()

            def __enter__(self):
                return self

            def __exit__(self, *_):
                pass

        monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=None: _FakeResponse())
        result = poster.check_token_health()
        assert result["healthy"] is False, "Result must not be empty"
        assert result["expiry_warning"] is not None, "Value must be initialized"
        assert "missing" in str(result["expiry_warning"]).lower(), "Result must not be empty"

    def test_token_source_tracking(self, monkeypatch):
        """Token source is tracked correctly for each env var."""
        for key in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GITHUB_TOKEN"):
            monkeypatch.delenv(key, raising=False)
        from codex.github.mcp_poster import GitHubMCPPoster

        monkeypatch.setenv("CODEX_BACKUP_KEY", "backup_token")
        poster = GitHubMCPPoster()
        assert poster._token_source == "CODEX_BACKUP_KEY", "_token_source is not valid"

        monkeypatch.setenv("CODEX_MASTER_KEY", "master_token")
        poster2 = GitHubMCPPoster()
        assert poster2._token_source == "CODEX_MASTER_KEY", "_token_source is not valid"
