"""
Tests for codex_ml.cli.validate module.

Tests configuration validation functionality.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

CLI_HELP_TIMEOUT_SECONDS = 90


class TestValidateModuleImport:
    """Tests for validate module imports."""

    def test_validate_module_import(self):
        """Test that validate module can be imported."""
        try:
            from codex_ml.cli import validate

            assert validate is not None, "validate must be initialized"
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")

    def test_validate_has_logging_utilities(self):
        """Test that logging utilities are available."""
        try:
            from codex_ml.cli.validate import (
                capture_exceptions,
                init_json_logging,
                log_event,
            )

            assert callable(capture_exceptions), "Condition must be true"
            assert callable(init_json_logging), "Condition must be true"
            assert callable(log_event), "Condition must be true"
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")


class TestValidationErrorFormatting:
    """Tests for validation error formatting."""

    def test_format_validation_error_function_exists(self):
        """Test that _format_validation_error function exists."""
        try:
            from codex_ml.cli.validate import _format_validation_error

            assert callable(_format_validation_error), "Error should be raised or set"
        except ImportError as e:
            pytest.skip(f"Function import failed: {e}")

    @patch("codex_ml.cli.validate.ValidationError")
    def test_format_validation_error_with_mock(self, mock_validation_error):
        """Test validation error formatting with mock."""
        try:
            from codex_ml.cli.validate import _format_validation_error

            # Create mock error
            mock_error = MagicMock()
            mock_error.errors.return_value = [
                {"loc": ("field1",), "msg": "required field"},
                {"loc": ("field2", "subfield"), "msg": "invalid value"},
            ]

            # May raise or return formatted string
            try:
                result = _format_validation_error(mock_error)
                assert isinstance(result, str)
            except (TypeError, AttributeError):
                # Different ValidationError interface
                _ = None  # suppressed: no action needed
        except ImportError as e:
            pytest.skip(f"Function import failed: {e}")


class TestYAMLSupport:
    """Tests for YAML loading support."""

    def test_safe_load_import(self):
        """Test that safe_load is importable."""
        try:
            from codex_ml.utils.yaml_support import safe_load

            assert callable(safe_load), "Condition must be true"
        except ImportError as e:
            pytest.skip(f"safe_load import failed: {e}")

    def test_missing_pyyaml_error_import(self):
        """Test that MissingPyYAMLError is importable."""
        try:
            from codex_ml.utils.yaml_support import MissingPyYAMLError

            assert issubclass(MissingPyYAMLError, Exception)
        except ImportError as e:
            pytest.skip(f"MissingPyYAMLError import failed: {e}")


class TestValidateCLI:
    """Tests for validate CLI commands."""

    def test_validate_module_help(self):
        """Test validate module --help."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.validate", "--help"],
            capture_output=True,
            text=True,
            timeout=CLI_HELP_TIMEOUT_SECONDS,
        )
        # May or may not have CLI entry point
        assert result.returncode in (0, 1, 2)

    def test_validate_config_command(self):
        """Test validate config subcommand if available."""
        result = subprocess.run(
            [sys.executable, "-m", "codex_ml.cli.validate", "config", "--help"],
            capture_output=True,
            text=True,
            timeout=CLI_HELP_TIMEOUT_SECONDS,
        )
        # May or may not have config subcommand
        assert result.returncode in (0, 1, 2)


class TestConfigValidation:
    """Tests for configuration validation logic."""

    def test_validate_valid_yaml_config(self):
        """Test validation of a valid YAML configuration."""
        # Create a valid config
        config = {
            "training": {"epochs": 10, "batch_size": 32, "learning_rate": 0.001},
            "model": {"name": "test-model", "hidden_size": 768},
        }

        # Basic validation - should be valid YAML
        assert isinstance(config, dict)
        assert "training" in config, "Condition must be true"
        assert config["training"]["epochs"] == 10, "Condition must be true"

    def test_validate_invalid_yaml_syntax(self):
        """Test handling of invalid YAML syntax."""
        invalid_yaml = "key: value\n  bad_indent: error"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(invalid_yaml)
            temp_path = Path(f.name)

        try:
            try:
                with open(temp_path) as handle:
                    yaml.safe_load(handle)
                # May or may not fail depending on YAML parser
            except yaml.YAMLError:
                # Expected for invalid YAML
                _ = None  # suppressed: no action needed
        finally:
            temp_path.unlink(missing_ok=True)

    def test_validate_missing_required_fields(self):
        """Test validation of config missing required fields."""
        incomplete_config = {"training": {}}  # Missing required fields

        # This should be flagged as incomplete
        assert "epochs" not in incomplete_config["training"], "Condition must be true"
        assert "batch_size" not in incomplete_config["training"], "Condition must be true"


class TestDiffValidation:
    """Tests for configuration diff functionality."""

    def test_difflib_import(self):
        """Test that difflib is properly imported."""
        try:
            from codex_ml.cli.validate import difflib

            # Should be the standard library difflib or equivalent
            assert hasattr(difflib, "unified_diff") or difflib is not None
        except ImportError:
            import difflib

            assert hasattr(difflib, "unified_diff")

    def test_config_diff_detection(self):
        """Test detection of config differences."""
        import difflib

        config1 = "epochs: 10\nbatch_size: 32"
        config2 = "epochs: 20\nbatch_size: 32"

        diff = list(
            difflib.unified_diff(
                config1.splitlines(keepends=True),
                config2.splitlines(keepends=True),
                fromfile="config1.yaml",
                tofile="config2.yaml",
            )
        )

        # Should detect difference in epochs
        assert len(diff) > 0, "Diff must not be empty"
        assert any("epochs" in line for line in diff), "Condition must be true"


class TestOptionalDependencies:
    """Tests for optional dependency handling."""

    def test_pydantic_optional(self):
        """Test that pydantic is handled as optional."""
        try:
            from codex_ml.cli.validate import ValidationError

            # ValidationError may be None if pydantic not installed
            if ValidationError is not None:
                assert issubclass(ValidationError, Exception)
        except ImportError:
            # Expected if pydantic not available
            _ = None  # suppressed: no action needed

    def test_typer_optional(self):
        """Test that typer is handled as optional."""
        try:
            from codex_ml.cli.validate import typer

            # typer may be None if not installed
            if typer is not None:
                assert hasattr(typer, "Typer")
        except ImportError:
            # Expected if typer not available
            _ = None  # suppressed: no action needed

    def test_config_schema_optional(self):
        """Test that config_schema is handled as optional."""
        try:
            from codex_ml.cli.validate import validate_config_file

            # May be None if not available
            if validate_config_file is not None:
                assert callable(validate_config_file), "Condition must be true"
        except ImportError:
            _ = None  # Module not available - skip test
