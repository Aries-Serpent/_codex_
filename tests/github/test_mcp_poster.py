"""Tests for GitHubMCPPoster — autonomous PR/Discussion poster.

Covers all public methods with mocked urllib responses so no real
network calls are made. Zero external dependencies.
"""
from __future__ import annotations

import json
import unittest.mock as mock
from io import BytesIO

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
    assert p._token == "master-tok"


def test_falls_back_to_backup_key(monkeypatch):
    monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
    monkeypatch.setenv("CODEX_BACKUP_KEY", "backup-tok")
    p = GitHubMCPPoster()
    assert p._token == "backup-tok"


def test_falls_back_to_github_token(monkeypatch):
    monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
    monkeypatch.delenv("CODEX_BACKUP_KEY", raising=False)
    monkeypatch.setenv("GITHUB_TOKEN", "gh-tok")
    p = GitHubMCPPoster()
    assert p._token == "gh-tok"


def test_no_token_warns(monkeypatch, caplog):
    monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
    monkeypatch.delenv("CODEX_BACKUP_KEY", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    import logging
    with caplog.at_level(logging.WARNING, logger="codex.github.mcp_poster"):
        GitHubMCPPoster()
    assert "No GitHub token" in caplog.text


# ---------------------------------------------------------------------------
# post_pr_comment
# ---------------------------------------------------------------------------


def test_post_pr_comment_success(poster, monkeypatch):
    resp = _mock_response({"html_url": "https://github.com/test/repo/issues/1#issuecomment-1"})
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: resp)
    result = poster.post_pr_comment("Aries-Serpent/_codex_", 3401, "@copilot test")
    assert result["html_url"].startswith("https://github.com")


def test_post_pr_comment_requires_token(no_token_poster):
    with pytest.raises(RuntimeError, match="CODEX_MASTER_KEY"):
        no_token_poster.post_pr_comment("owner/repo", 1, "body")


def test_post_pr_comment_from_file(poster, monkeypatch, tmp_path):
    body_file = tmp_path / "prompt.md"
    body_file.write_text("@copilot hello")
    resp = _mock_response({"html_url": "https://github.com/x"})
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: resp)
    result = poster.post_pr_comment_from_file("owner/repo", 42, body_file)
    assert "html_url" in result


# ---------------------------------------------------------------------------
# set_repo_variable
# ---------------------------------------------------------------------------


def test_set_repo_variable_patch_success(poster, monkeypatch):
    resp = _mock_response({})
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: resp)
    result = poster.set_repo_variable("owner/repo", "MY_VAR", "true")
    assert result == {}


def test_set_repo_variable_falls_back_to_post_on_404(poster, monkeypatch):
    import urllib.error

    call_count = {"n": 0}

    def fake_urlopen(req, timeout):
        call_count["n"] += 1
        if call_count["n"] == 1:
            exc = urllib.error.HTTPError(url="", code=404, msg="Not Found", hdrs=None, fp=BytesIO(b"{}"))
            raise exc
        return _mock_response({"name": "MY_VAR"})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    poster.set_repo_variable("owner/repo", "MY_VAR", "true")
    assert call_count["n"] == 2  # PATCH failed → POST


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
    assert rc == 0


def test_cli_set_variable(monkeypatch):
    monkeypatch.setenv("CODEX_MASTER_KEY", "tok")
    resp = _mock_response({})
    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout: resp)
    rc = main(["set-variable", "--repo", "o/r", "--name", "X", "--value", "1"])
    assert rc == 0


def test_cli_no_token_returns_1(monkeypatch):
    monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
    monkeypatch.delenv("CODEX_BACKUP_KEY", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    rc = main(["post-comment", "--repo", "o/r", "--pr", "1", "--body", "hi"])
    assert rc == 1
