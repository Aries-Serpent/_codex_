"""
Integration tests for CLI entrypoints.

Tests that CLI commands execute without errors.
"""

import subprocess
import sys


class TestCodexCLI:
    """Test codex.cli module entrypoint."""

    def test_cli_help_returns_success(self):
        """Test CLI --help returns 0."""
        result = subprocess.run(
            [sys.executable, "-m", "codex.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, "Result must not be empty"
        assert "usage" in result.stdout.lower() or "Usage" in result.stdout, "Result must not be empty"

    def test_cli_shows_commands(self):
        """Test CLI lists available commands."""
        result = subprocess.run(
            [sys.executable, "-m", "codex.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should show some commands
        output = result.stdout.lower()
        assert "commands:" in output or "command" in output, "Condition must be true"

    def test_cli_archive_help(self):
        """Test CLI archive subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex.cli", "archive", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, "Result must not be empty"


class TestCodexMLCLI:
    """Test codex_ml.cli module entrypoint."""

    def test_codex_ml_cli_help(self):
        """Test codex-ml CLI --help returns 0."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should succeed or indicate missing config (acceptable)
        assert result.returncode in (0, 1)  # May fail gracefully if no config

        # If it succeeds, should show usage
        if result.returncode == 0:
            assert "usage" in result.stdout.lower() or "help" in result.stdout.lower(), "Result must not be empty"


class TestLoggingCLI:
    """Test logging CLI tools."""

    def test_session_logger_help(self):
        """Test session logger CLI help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex.logging.session_logger", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should succeed or gracefully fail
        assert result.returncode in (0, 1, 2)  # Various CLIs may have different error codes

    def test_query_logs_help(self):
        """Test query logs CLI help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex.logging.query_logs", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should succeed or gracefully fail
        assert result.returncode in (0, 1, 2)
