"""S109 org rollout — mcp_poster + COGNITIVE_BRAIN_SESSION_NUMBER update tests.

Covers:
- set_repo_variable for COGNITIVE_BRAIN_SESSION_NUMBER
- set_repo_variable for COGNITIVE_BRAIN_ALLOWED_ACTORS
- PATCH (update) and POST (create) fallback paths
- Token token auth priority with CODEX_MASTER_KEY / CODEX_BACKUP_KEY
- CLI main() for set-variable command
"""

from __future__ import annotations

import json
import unittest.mock as mock

import pytest

# Ensure codex.github is registered as an attribute of the codex package before
# pytest's monkeypatch.setattr() tries to resolve dotted paths like
# "codex.github.mcp_poster.urllib.request.urlopen".  A plain "from X import Y"
# sets X as an attribute on its parent only after the submodule is imported;
# the explicit import below guarantees the attribute is present even if test
# collection order changes.
from codex.github.mcp_poster import GitHubMCPPoster, main

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_urlopen(payload: dict, status: int = 200):
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
    monkeypatch.setenv("CODEX_MASTER_KEY", "ghp_testtoken_s109")
    return GitHubMCPPoster()


# ---------------------------------------------------------------------------
# set_repo_variable — session number update
# ---------------------------------------------------------------------------


def test_set_session_number_patch(poster, monkeypatch):
    """COGNITIVE_BRAIN_SESSION_NUMBER PATCH updates existing variable."""
    monkeypatch.setattr(
        "codex.github.mcp_poster.urllib.request.urlopen",
        mock.Mock(
            return_value=_mock_urlopen({"name": "COGNITIVE_BRAIN_SESSION_NUMBER", "value": "109"})
        ),
    )
    result = poster.set_repo_variable(
        "Aries-Serpent/_codex_", "COGNITIVE_BRAIN_SESSION_NUMBER", "109"
    )
    assert result.get("value") == "109" or result.get("name") == "COGNITIVE_BRAIN_SESSION_NUMBER"


def test_set_session_number_creates_on_404(poster, monkeypatch):
    """Falls back to POST (create) when PATCH returns 404."""
    call_count = {"n": 0}

    def side_effect(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            err = __import__("urllib.error", fromlist=["HTTPError"]).HTTPError
            raise err("url", 404, "Not Found", {}, None)
        return _mock_urlopen({"name": "COGNITIVE_BRAIN_SESSION_NUMBER", "value": "109"})

    monkeypatch.setattr(
        "codex.github.mcp_poster.urllib.request.urlopen", mock.Mock(side_effect=side_effect)
    )
    result = poster.set_repo_variable(
        "Aries-Serpent/_codex_", "COGNITIVE_BRAIN_SESSION_NUMBER", "109"
    )
    assert result.get("name") == "COGNITIVE_BRAIN_SESSION_NUMBER", "name must match"
    assert call_count["n"] == 2, "Count must be greater than zero"


def test_set_allowed_actors_patch(poster, monkeypatch):
    """COGNITIVE_BRAIN_ALLOWED_ACTORS update via PATCH."""
    new_value = "mbaetiong,github-actions[bot],copilot-swe-agent[bot]"
    monkeypatch.setattr(
        "codex.github.mcp_poster.urllib.request.urlopen",
        mock.Mock(
            return_value=_mock_urlopen(
                {"name": "COGNITIVE_BRAIN_ALLOWED_ACTORS", "value": new_value}
            )
        ),
    )
    result = poster.set_repo_variable(
        "Aries-Serpent/_codex_", "COGNITIVE_BRAIN_ALLOWED_ACTORS", new_value
    )
    assert result.get("name") == "COGNITIVE_BRAIN_ALLOWED_ACTORS", "name must match variable key"
    assert result.get("value") == new_value, "returned value must match the value we set"


def test_set_injection_enabled_true(poster, monkeypatch):
    """COGNITIVE_BRAIN_INJECTION_ENABLED=true update."""
    monkeypatch.setattr(
        "codex.github.mcp_poster.urllib.request.urlopen",
        mock.Mock(
            return_value=_mock_urlopen(
                {"name": "COGNITIVE_BRAIN_INJECTION_ENABLED", "value": "true"}
            )
        ),
    )
    result = poster.set_repo_variable(
        "Aries-Serpent/_codex_", "COGNITIVE_BRAIN_INJECTION_ENABLED", "true"
    )
    assert result.get("name") == "COGNITIVE_BRAIN_INJECTION_ENABLED", "name must match variable key"
    assert result.get("value") == "true", "value must match the enabled flag"


def test_set_variable_requires_token(monkeypatch):
    """set_repo_variable raises RuntimeError when no token configured."""
    monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
    monkeypatch.delenv("CODEX_BACKUP_KEY", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    poster = GitHubMCPPoster()
    with pytest.raises(RuntimeError, match="No GitHub token available"):
        poster.set_repo_variable("Aries-Serpent/_codex_", "VAR", "val")


# ---------------------------------------------------------------------------
# Token priority: CODEX_MASTER_KEY > CODEX_BACKUP_KEY > GITHUB_TOKEN
# ---------------------------------------------------------------------------


def test_uses_master_key_for_variable_update(monkeypatch):
    monkeypatch.setenv("CODEX_MASTER_KEY", "master_token_s109")
    monkeypatch.setenv("CODEX_BACKUP_KEY", "backup_token_s109")
    p = GitHubMCPPoster()
    assert p._token == "master_token_s109", "_token is not valid"


def test_uses_backup_key_when_master_absent(monkeypatch):
    monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
    monkeypatch.setenv("CODEX_BACKUP_KEY", "backup_token_s109")
    p = GitHubMCPPoster()
    assert p._token == "backup_token_s109", "_token is not valid"


# ---------------------------------------------------------------------------
# CLI set-variable for session number S109
# ---------------------------------------------------------------------------


def test_cli_set_session_number_s109(monkeypatch):
    """CLI set-variable updates COGNITIVE_BRAIN_SESSION_NUMBER to 109."""
    monkeypatch.setenv("CODEX_MASTER_KEY", "ghp_s109_cli_token")
    monkeypatch.setattr(
        "codex.github.mcp_poster.urllib.request.urlopen",
        mock.Mock(
            return_value=_mock_urlopen({"name": "COGNITIVE_BRAIN_SESSION_NUMBER", "value": "109"})
        ),
    )
    rc = main(
        [
            "set-variable",
            "--repo",
            "Aries-Serpent/_codex_",
            "--name",
            "COGNITIVE_BRAIN_SESSION_NUMBER",
            "--value",
            "109",
        ]
    )
    assert rc == 0, "rc is not valid"


def test_cli_set_allowed_actors_s109(monkeypatch):
    """CLI set-variable updates COGNITIVE_BRAIN_ALLOWED_ACTORS for org rollout."""
    monkeypatch.setenv("CODEX_MASTER_KEY", "ghp_s109_cli_token")
    new_actors = "mbaetiong,github-actions[bot],copilot-swe-agent[bot]"
    monkeypatch.setattr(
        "codex.github.mcp_poster.urllib.request.urlopen",
        mock.Mock(
            return_value=_mock_urlopen(
                {"name": "COGNITIVE_BRAIN_ALLOWED_ACTORS", "value": new_actors}
            )
        ),
    )
    rc = main(
        [
            "set-variable",
            "--repo",
            "Aries-Serpent/_codex_",
            "--name",
            "COGNITIVE_BRAIN_ALLOWED_ACTORS",
            "--value",
            new_actors,
        ]
    )
    assert rc == 0, "rc is not valid"
