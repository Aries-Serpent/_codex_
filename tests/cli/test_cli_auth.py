"""
Tests for the ``codex auth`` CLI subcommands.

Validates ``codex auth register``, ``codex auth login``, and
``codex auth logout`` via the Click test runner.
"""

import pytest
from click.testing import CliRunner

from codex.cli import auth_group, cli


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
        assert result.exit_code == 0
        assert "register" in result.output
        assert "login" in result.output
        assert "logout" in result.output

    def test_auth_no_subcommand_shows_help(self, runner):
        result = runner.invoke(cli, ["auth"])
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------


class TestAuthRegisterCLI:

    def test_register_success(self, runner):
        result = runner.invoke(
            cli,
            ["auth", "register", "-u", "testuser", "-e", "test@example.com", "-p", "Str0ngPass!"],
        )
        assert result.exit_code == 0
        assert "Registered user" in result.output
        assert "testuser" in result.output

    def test_register_weak_password_fails(self, runner):
        result = runner.invoke(
            cli,
            ["auth", "register", "-u", "badpw", "-e", "bad@example.com", "-p", "short"],
        )
        assert result.exit_code != 0

    def test_register_missing_username_fails(self, runner):
        result = runner.invoke(
            cli,
            ["auth", "register", "-e", "no@user.com", "-p", "Str0ngPass!"],
        )
        assert result.exit_code != 0


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
        assert result.exit_code != 0
        assert "Login failed" in result.output


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


class TestAuthLogoutCLI:

    def test_logout_invalid_token(self, runner):
        result = runner.invoke(
            cli,
            ["auth", "logout", "-s", "not-a-real-token"],
        )
        assert result.exit_code == 0
        assert "invalid or expired" in result.output
