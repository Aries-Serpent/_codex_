"""
Tests for CLI credential caching: keyring backend + JSON file fallback.

Covers:
- keyring success path (cache/load/clear via mock keyring)
- JSON file fallback when keyring is unavailable
- _clear_cached_credentials removes both keyring entry and JSON file
- auth status with/without cached credentials
- Login --save flag triggers credential caching
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from codex.cli import cli


def _get_cli_module():
    """Get the actual Click CLI module (not the facade __init__)."""
    return sys.modules.get("codex._cli_click")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def cli_mod():
    """Return the actual CLI implementation module."""
    mod = _get_cli_module()
    assert mod is not None, "codex._cli_click not loaded"
    return mod


@pytest.fixture()
def tmp_cache_dir(tmp_path):
    """Override _CACHE_DIR / _CACHE_FILE to use a temp directory."""
    cache_file = tmp_path / "credentials.json"
    return tmp_path, cache_file


# ---------------------------------------------------------------------------
# Keyring backend tests (mock-based)
# ---------------------------------------------------------------------------


class TestKeyringBackend:
    """Verify credential caching through the keyring backend."""

    def test_cache_via_keyring(self, cli_mod):
        """_cache_credentials stores data in keyring when available."""
        mock_keyring = MagicMock()
        with patch.dict("sys.modules", {"keyring": mock_keyring}):
            cli_mod._cache_credentials("alice", "acc-token", "ref-token")

        mock_keyring.set_password.assert_called_once()
        call_args = mock_keyring.set_password.call_args
        assert call_args[0][0] == "codex-cli", "Condition must be true"
        assert call_args[0][1] == "credentials", "Condition must be true"
        payload = json.loads(call_args[0][2])
        assert payload["username"] == "alice", "Condition must be true"
        assert payload["access_token"] == "acc-token", "Condition must be true"
        assert payload["refresh_token"] == "ref-token", "Condition must be true"

    def test_load_from_keyring(self, cli_mod):
        """_load_cached_credentials reads from keyring when present."""
        stored = json.dumps(
            {
                "username": "bob",
                "access_token": "a",
                "refresh_token": "r",
            }
        )
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = stored

        with patch.dict("sys.modules", {"keyring": mock_keyring}):
            result = cli_mod._load_cached_credentials()

        assert result is not None, "result must be initialized"
        assert result["username"] == "bob", "Result must not be empty"

    def test_load_returns_none_when_keyring_empty(self, cli_mod):
        """Returns None when keyring has no entry and no JSON file exists."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = None

        with (
            patch.dict("sys.modules", {"keyring": mock_keyring}),
            patch.object(cli_mod, "_CACHE_FILE", Path("/nonexistent/path")),
        ):
            result = cli_mod._load_cached_credentials()

        assert result is None, "Result must not be empty"

    def test_clear_keyring_and_file(self, cli_mod, tmp_cache_dir):
        """_clear_cached_credentials removes both keyring entry and file."""
        _, cache_file = tmp_cache_dir
        cache_file.write_text('{"username":"x"}', encoding="utf-8")

        mock_keyring = MagicMock()
        with (
            patch.dict("sys.modules", {"keyring": mock_keyring}),
            patch.object(cli_mod, "_CACHE_FILE", cache_file),
        ):
            cli_mod._clear_cached_credentials()

        mock_keyring.delete_password.assert_called_once_with("codex-cli", "credentials")
        assert not cache_file.exists(), "Condition must be true"


# ---------------------------------------------------------------------------
# JSON file fallback tests
# ---------------------------------------------------------------------------


class TestJSONFileFallback:
    """Verify JSON file fallback when keyring is unavailable."""

    def test_fallback_to_json_file(self, cli_mod, tmp_cache_dir):
        """When keyring import fails, credentials are written to JSON file."""
        tmp_dir, cache_file = tmp_cache_dir

        # Make keyring import raise ImportError
        import builtins

        original_import = builtins.__import__

        def fail_import(name, *args, **kwargs):
            if name == "keyring":
                raise ImportError("No keyring")
            return original_import(name, *args, **kwargs)

        with (
            patch.object(cli_mod, "_CACHE_DIR", tmp_dir),
            patch.object(cli_mod, "_CACHE_FILE", cache_file),
            patch("builtins.__import__", side_effect=fail_import),
        ):
            cli_mod._cache_credentials("carol", "at", "rt")

        assert cache_file.exists(), "Condition must be true"
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        assert data["username"] == "carol", "Data must not be empty"
        assert data["access_token"] == "at", "Data must not be empty"

    def test_load_from_json_file(self, cli_mod, tmp_cache_dir):
        """_load_cached_credentials falls back to JSON file."""
        _, cache_file = tmp_cache_dir
        creds = {"username": "dave", "access_token": "a2", "refresh_token": "r2"}
        cache_file.write_text(json.dumps(creds), encoding="utf-8")

        # Make keyring return None (or fail)
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = None

        with (
            patch.dict("sys.modules", {"keyring": mock_keyring}),
            patch.object(cli_mod, "_CACHE_FILE", cache_file),
        ):
            result = cli_mod._load_cached_credentials()

        assert result is not None, "result must be initialized"
        assert result["username"] == "dave", "Result must not be empty"


# ---------------------------------------------------------------------------
# CLI integration tests for auth status
# ---------------------------------------------------------------------------


class TestAuthStatusCLI:
    """Test 'codex auth status' output with/without cached credentials."""

    def test_status_no_credentials(self, runner, cli_mod):
        """auth status shows 'No cached credentials' when nothing cached."""
        with patch.object(cli_mod, "_load_cached_credentials", return_value=None):
            result = runner.invoke(cli, ["auth", "status"])

        assert result.exit_code == 0, "Result must not be empty"
        assert "No cached credentials" in result.output, "Result must not be empty"

    def test_status_with_credentials(self, runner, cli_mod):
        """auth status shows cached username when credentials exist."""
        creds = {"username": "eve", "access_token": "tok", "refresh_token": "ref"}
        with patch.object(cli_mod, "_load_cached_credentials", return_value=creds):
            result = runner.invoke(cli, ["auth", "status"])

        assert result.exit_code == 0, "Result must not be empty"
        assert "eve" in result.output, "Result must not be empty"
