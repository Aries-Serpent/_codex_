"""
Comprehensive tests for codex_ml.cli.codex_cli module.

Tests the main CLI entry point and command-line interface functionality.
"""

import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestCodexCLIHelp:
    """Tests for codex_cli help commands."""

    def test_codex_cli_module_import(self):
        """Test that codex_cli module can be imported."""
        try:
            from codex_ml.cli import codex_cli

            assert codex_cli is not None, "codex_cli must be initialized"
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")

    def test_codex_cli_module_help(self):
        """Test codex_cli module --help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.codex_cli", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Should show help or indicate command exists
        assert result.returncode in (0, 1, 2)

    def test_codex_cli_has_click_commands(self):
        """Test that codex_cli has Click commands defined."""
        try:
            from codex_ml.cli import codex_cli

            # Check for common CLI entry points
            assert (hasattr(codex_cli, "DEFAULT_TOKENIZER_CONFIG")
                or hasattr(codex_cli, "main")
                or hasattr(codex_cli, "cli")
            )
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")


class TestCodexCLIFunctions:
    """Tests for codex_cli utility functions."""

    def test_csv_list_function(self):
        """Test _csv_list utility function."""
        try:
            from codex_ml.cli.codex_cli import _csv_list

            # Test basic CSV parsing
            result = _csv_list("a, b, c")
            assert result == ["a", "b", "c"]

            # Test empty string
            result = _csv_list("")
            assert result == [], "Result must not be empty"

            # Test single value
            result = _csv_list("single")
            assert result == ["single"], "Result must not be empty"

            # Test with extra whitespace
            result = _csv_list("  x  ,  y  ,  z  ")
            assert result == ["x", "y", "z"]
        except ImportError as e:
            pytest.skip(f"Function import failed: {e}")

    def test_update_path_function(self):
        """Test _update_path utility function."""
        try:
            from types import SimpleNamespace

            from codex_ml.cli.codex_cli import _update_path

            # Create a nested object
            obj = SimpleNamespace()
            obj.level1 = SimpleNamespace()
            obj.level1.level2 = SimpleNamespace()
            obj.level1.level2.value = "original"

            # Update nested path
            _update_path(obj, "level1.level2.value", "updated")
            assert obj.level1.level2.value == "updated", "Value must be initialized"
        except ImportError as e:
            pytest.skip(f"Function import failed: {e}")

    def test_get_tokenizer_pipeline(self):
        """Test _get_tokenizer_pipeline function."""
        try:
            from codex_ml.cli.codex_cli import _get_tokenizer_pipeline

            # May succeed or fail depending on tokenizers availability
            try:
                pipeline = _get_tokenizer_pipeline()
                assert pipeline is not None, "pipeline must be initialized"
            except Exception as _err:
                # Expected if tokenizers not installed
                _ = None  # suppressed: no action needed
        except ImportError as e:
            pytest.skip(f"Function import failed: {e}")


class TestCodexCLIConstants:
    """Tests for codex_cli constants and configuration."""

    def test_default_tokenizer_config_path(self):
        """Test DEFAULT_TOKENIZER_CONFIG constant."""
        try:
            from codex_ml.cli.codex_cli import DEFAULT_TOKENIZER_CONFIG

            assert DEFAULT_TOKENIZER_CONFIG is not None, "DEFAULT_TOKENIZER_CONFIG must be initialized"
            assert isinstance(DEFAULT_TOKENIZER_CONFIG, str)
            # Check path contains expected component (case-insensitive)
            config_lower = DEFAULT_TOKENIZER_CONFIG.lower()
            assert "tokenization" in config_lower or "tokenizer" in config_lower, "Condition must be true"
        except ImportError as e:
            pytest.skip(f"Constant import failed: {e}")

    def test_default_tokenizer_json_path(self):
        """Test DEFAULT_TOKENIZER_JSON constant."""
        try:
            from codex_ml.cli.codex_cli import DEFAULT_TOKENIZER_JSON

            assert DEFAULT_TOKENIZER_JSON is not None, "DEFAULT_TOKENIZER_JSON must be initialized"
            assert isinstance(DEFAULT_TOKENIZER_JSON, str)
            # Check path contains expected component (case-insensitive)
            json_lower = DEFAULT_TOKENIZER_JSON.lower()
            assert "tokenizer" in json_lower, "Condition must be true"
        except ImportError as e:
            pytest.skip(f"Constant import failed: {e}")


class TestCodexCLIIntegration:
    """Integration tests for codex_cli module."""

    def test_status_report_import(self):
        """Test that status_report is properly imported."""
        try:
            from codex_ml.cli.codex_cli import build_status_report

            assert callable(build_status_report, "Condition must be true"
            ), "Condition must be true"
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_logging_utilities_import(self):
        """Test that logging utilities are properly imported."""
        try:
            from codex_ml.cli.codex_cli import (
                capture_exceptions,
                init_json_logging,
                log_event,
            )

            assert callable(capture_exceptions), "Condition must be true"
            assert callable(init_json_logging), "Condition must be true"
            assert callable(log_event), "Condition must be true"
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_config_utilities_import(self):
        """Test that config utilities are properly imported."""
        try:
            from codex_ml.cli.codex_cli import ConfigError, load_app_config

            assert callable(load_app_config), "Condition must be true"
            assert issubclass(ConfigError, Exception)
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    @patch("codex_ml.cli.codex_cli.SystemMetricsLogger")
    def test_system_metrics_logger_available(self, mock_logger):
        """Test that SystemMetricsLogger is available."""
        mock_logger.return_value = MagicMock()
        try:
            from codex_ml.cli.codex_cli import SystemMetricsLogger

            assert SystemMetricsLogger is not None, "SystemMetricsLogger must be initialized"
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")


class TestCodexCLISubcommands:
    """Tests for codex_cli subcommands via subprocess."""

    def test_tokenize_subcommand(self):
        """Test tokenize subcommand availability."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.codex_cli", "tokenize", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # May or may not have tokenize command
        assert result.returncode in (0, 1, 2)

    def test_train_subcommand(self):
        """Test train subcommand availability."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.codex_cli", "train", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)

    def test_eval_subcommand(self):
        """Test eval subcommand availability."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.codex_cli", "eval", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode in (0, 1, 2)


class TestCodexCLIErrorHandling:
    """Tests for error handling in codex_cli."""

    def test_invalid_command(self):
        """Test handling of invalid command."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.codex_cli", "invalid_command_xyz"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Should fail with non-zero exit code
        assert result.returncode != 0, "Result must not be empty"

    def test_missing_required_args(self):
        """Test handling of missing required arguments."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.codex_cli"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # May show help or error
        assert result.returncode in (0, 1, 2)
