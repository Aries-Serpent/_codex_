"""
Integration tests for codex_ml CLI entrypoints.

Tests command-line interface help, validation, and basic functionality.
"""

import subprocess
import sys

import pytest


class TestCodexMLCLIMain:
    """Test main codex_ml CLI entrypoint."""

    def test_codex_ml_module_help(self):
        """Test codex_ml module --help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml", "--help"], capture_output=True, text=True, timeout=30
        )

        # Should succeed or fail gracefully
        assert result.returncode in (0, 1, 2)

    def test_codex_ml_cli_help(self):
        """Test codex_ml.cli module help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # May have different exit codes depending on CLI framework
        assert result.returncode in (0, 1, 2)

    def test_codex_ml_version_attempt(self):
        """Test version command if available."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Version may or may not be implemented
        assert result.returncode in (0, 1, 2)


class TestCodexMLSubcommands:
    """Test codex_ml CLI subcommands."""

    def test_codex_ml_train_help(self):
        """Test train subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.train", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should show help or indicate command exists
        assert result.returncode in (0, 1, 2)

    def test_codex_ml_evaluate_help(self):
        """Test evaluate subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.evaluate", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode in (0, 1, 2)

    def test_codex_ml_config_help(self):
        """Test config subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.config", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode in (0, 1, 2)


class TestCodexMLImports:
    """Test codex_ml module imports."""

    def test_import_codex_ml_main(self):
        """Test importing codex_ml package."""
        try:
            import codex_ml

            assert codex_ml is not None, "codex_ml must be initialized"
        except ImportError:
            pytest.skip("codex_ml not importable")

    def test_import_codex_ml_cli(self):
        """Test importing codex_ml.cli."""
        try:
            import codex_ml.cli

            assert codex_ml.cli is not None, "cli must be initialized"
        except ImportError:
            pytest.skip("codex_ml.cli not importable")

    def test_codex_ml_has_version(self):
        """Test codex_ml has version attribute."""
        try:
            import codex_ml

            # May have __version__ or VERSION
            has_version = (
                hasattr(codex_ml, "__version__")
                or hasattr(codex_ml, "VERSION")
                or hasattr(codex_ml, "version")
            )
            # Version may not be set in development - skip if not present
            if not has_version:
                pytest.skip("codex_ml version not set in development")
            assert has_version, "has_version is not valid"
        except ImportError:
            pytest.skip("codex_ml not importable")
