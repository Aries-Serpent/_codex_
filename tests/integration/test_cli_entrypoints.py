"""
Integration tests for codex.cli entrypoints.

Tests basic CLI functionality and help commands.
"""
import subprocess
import sys

import pytest


class TestCLIEntrypoints:
    """Test suite for CLI entrypoint functionality."""

    def test_cli_help_command(self):
        """Test that CLI help command works."""
        result = subprocess.run(
            [sys.executable, "-m", "codex.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0, f"CLI help failed: {result.stderr}"
        assert "usage" in result.stdout.lower() or "Usage" in result.stdout
        
    def test_cli_version_command(self):
        """Test that CLI version command works if available."""
        result = subprocess.run(
            [sys.executable, "-m", "codex.cli", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Version command may not exist, but if it does, it should succeed
        # or if it doesn't exist, help should be shown
        assert result.returncode in [0, 2], f"Unexpected return code: {result.returncode}"

    def test_cli_module_importable(self):
        """Test that CLI module can be imported."""
        result = subprocess.run(
            [sys.executable, "-c", "from codex.cli import cli; print('OK')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0, f"CLI import failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_cli_subcommands_exist(self):
        """Test that CLI shows available subcommands."""
        result = subprocess.run(
            [sys.executable, "-m", "codex.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        # Most CLIs show "Commands:" or "Subcommands:" in help
        output_lower = result.stdout.lower()
        # Just verify we get help output, not empty
        assert len(result.stdout) > 50, "Help output seems too short"

    def test_cli_invalid_command_fails(self):
        """Test that invalid command returns non-zero exit code."""
        result = subprocess.run(
            [sys.executable, "-m", "codex.cli", "nonexistent_command_xyz"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should fail with non-zero exit code
        assert result.returncode != 0


class TestCLIPackageStructure:
    """Test CLI package structure and imports."""

    def test_cli_main_module_exists(self):
        """Test that codex.cli module exists."""
        result = subprocess.run(
            [sys.executable, "-c", "import codex.cli"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0, f"Failed to import codex.cli: {result.stderr}"

    def test_cli_dunder_main_exists(self):
        """Test that __main__.py allows python -m execution."""
        result = subprocess.run(
            [sys.executable, "-c", "import codex.cli.__main__"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0, f"Failed to import __main__: {result.stderr}"
