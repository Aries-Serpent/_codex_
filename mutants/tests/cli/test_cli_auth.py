"""
Tests for the ``codex auth`` CLI subcommands.

Validates ``codex auth register``, ``codex auth login``, and
``codex auth logout`` via the Click test runner.
"""

import pytest
from click.testing import CliRunner

from codex.cli import cli

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# Auth group
# ---------------------------------------------------------------------------


class TestAuthGroup:

    def test_auth_help_displayed(self, runner):
        result = runner.invoke(cli, ["auth", "--help"])
        assert result.exit_code == 0, "Result must not be empty"
        assert "register" in result.output, "Result must not be empty"
        assert "login" in result.output, "Result must not be empty"
        assert "logout" in result.output, "Result must not be empty"

    def test_auth_no_subcommand_shows_help(self, runner):
        result = runner.invoke(cli, ["auth"])
        assert result.exit_code == 0, "Result must not be empty"


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------


class TestAuthRegisterCLI:

    def test_register_success(self, runner):
        result = runner.invoke(
            cli,
            ["auth", "register", "-u", "testuser", "-e", "test@example.com", "-p", "Str0ngPass!"],
        )
        assert result.exit_code == 0, "Result must not be empty"
        assert "Registered user" in result.output, "Result must not be empty"
        assert "testuser" in result.output, "Result must not be empty"

    def test_register_weak_password_fails(self, runner):
        result = runner.invoke(
            cli,
            ["auth", "register", "-u", "badpw", "-e", "bad@example.com", "-p", "short"],
        )
        assert result.exit_code != 0, "Result must not be empty"

    def test_register_missing_username_fails(self, runner):
        result = runner.invoke(
            cli,
            ["auth", "register", "-e", "no@user.com", "-p", "Str0ngPass!"],
        )
        assert result.exit_code != 0, "Result must not be empty"


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


class TestAuthLoginCLI:

    def test_login_unknown_user_fails(self, runner):
        """Login with a non-existent user should fail."""
        result = runner.invoke(
            cli,
            ["auth", "login", "-u", "ghost", "-p", "Str0ngPass!"],
        )
        assert result.exit_code != 0, "Result must not be empty"
        assert "Login failed" in result.output, "Result must not be empty"


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


class TestAuthLogoutCLI:

    def test_logout_invalid_token(self, runner):
        result = runner.invoke(
            cli,
            ["auth", "logout", "-s", "not-a-real-token"],
        )
        assert result.exit_code == 0, "Result must not be empty"
        assert "invalid or expired" in result.output, "Result must not be empty"
