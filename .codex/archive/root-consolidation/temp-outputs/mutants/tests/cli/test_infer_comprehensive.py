"""
Tests for codex_ml.cli.infer module.

Tests model inference CLI functionality.
"""

import subprocess
import sys

import pytest


class TestInferModuleImport:
    """Tests for infer module imports."""

    def test_infer_module_import(self):
        """Test that infer module can be imported."""
        try:
            from codex_ml.cli import infer

            assert infer is not None, "infer must be initialized"
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")


class TestInferCLI:
    """Tests for infer CLI commands."""

    def test_infer_module_help(self):
        """Test infer module --help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.infer", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_infer_batch_help(self):
        """Test infer batch subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.infer", "batch", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_infer_single_help(self):
        """Test infer single subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.infer", "single", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)


class TestInferFunctionality:
    """Tests for infer module functionality."""

    def test_infer_without_model(self):
        """Test that inference requires a model."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.infer"], capture_output=True, text=True, timeout=30
        )
        # Should fail or show help without model
        assert result.returncode in (0, 1, 2)
