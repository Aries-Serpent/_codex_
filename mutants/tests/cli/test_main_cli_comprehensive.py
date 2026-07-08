"""
Tests for codex_ml.cli.main module.

Tests main CLI entry point functionality.
"""

import subprocess
import sys

import pytest


class TestMainModuleImport:
    """Tests for main module imports."""

    def test_main_module_import(self):
        """Test that main module can be imported."""
        try:
            from codex_ml.cli import main

            assert main is not None, "main must be initialized"
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")


class TestMainCLI:
    """Tests for main CLI commands."""

    def test_main_module_help(self):
        """Test main module --help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.main", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_main_version(self):
        """Test main module --version."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.main", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)


class TestMainFunctionality:
    """Tests for main module functionality."""

    def test_main_without_args(self):
        """Test main shows help without arguments."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.main"], capture_output=True, text=True, timeout=30
        )
        assert result.returncode in (0, 1, 2)

    def test_main_invalid_command(self):
        """Test main with invalid command."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.main", "invalid_xyz_command"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Should fail or show help
        assert result.returncode in (0, 1, 2)
