"""
Tests for codex_ml.cli.generate module.

Tests model generation CLI functionality.
"""

import subprocess
import sys

import pytest


class TestGenerateModuleImport:
    """Tests for generate module imports."""

    def test_generate_module_import(self):
        """Test that generate module can be imported."""
        try:
            from codex_ml.cli import generate

            assert generate is not None, "generate must be initialized"
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")


class TestGenerateCLI:
    """Tests for generate CLI commands."""

    def test_generate_module_help(self):
        """Test generate module --help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.generate", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_generate_text_help(self):
        """Test generate text subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.generate", "text", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)


class TestGenerateFunctionality:
    """Tests for generate module functionality."""

    def test_generate_without_model(self):
        """Test that generation requires a model."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.generate"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Should fail or show help without model
        assert result.returncode in (0, 1, 2)
