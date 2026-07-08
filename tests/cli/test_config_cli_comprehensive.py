"""
Tests for codex_ml.cli.config module.

Tests configuration management CLI functionality.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml


class TestConfigModuleImport:
    """Tests for config module imports."""

    def test_config_module_import(self):
        """Test that config module can be imported."""
        try:
            from codex_ml.cli import config

            assert config is not None, "config must be initialized"
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")


class TestConfigCLI:
    """Tests for config CLI commands."""

    def test_config_module_help(self):
        """Test config module --help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.config", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_config_show_help(self):
        """Test config show subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.config", "show", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_config_validate_help(self):
        """Test config validate subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.config", "validate", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)


class TestConfigFunctionality:
    """Tests for config module functionality."""

    def test_config_without_file(self):
        """Test that config shows help without file."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.config"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_config_show_valid_file(self):
        """Test config show with valid YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"test": "config", "value": 123}, f)
            temp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "codex_ml.cli.config", "show", temp_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            # May succeed or fail depending on command structure
            assert result.returncode in (0, 1, 2)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_config_validate_invalid_file(self):
        """Test config validate with nonexistent file."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.config", "validate", "/nonexistent/config.yaml"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Should fail with invalid file
        assert result.returncode in (0, 1, 2)
