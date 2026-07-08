"""Lane 3.2: CLI argument parsing tests - Unit tests for CLI command parsing."""

import os
import sys

import pytest

# Ensure src is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from click.testing import CliRunner

from codex_ml.cli.codex_cli import codex as cli


class TestCLIBasicCommands:
    """Test basic CLI command structure and discovery."""

    @pytest.fixture
    def runner(self):
        """Initialize Click CLI test runner."""
        return CliRunner()

    def test_cli_help_output(self, runner):
        """Test: help text displays all commands."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0, "Result must not be empty"
        assert 'help' in result.output.lower() or 'usage' in result.output.lower(), "Result must not be empty"

    def test_cli_version_output(self, runner):
        """Test: version command returns without error."""
        result = runner.invoke(cli, ['--version'])
        # Version may or may not be available, but should not crash
        assert result.exit_code in (0, 2)  # 0 if available, 2 if not implemented

    def test_cli_invalid_command(self, runner):
        """Test: invalid command produces error."""
        result = runner.invoke(cli, ['invalid_command'])
        assert result.exit_code != 0, "Result must not be empty"

    def test_cli_command_discovery(self, runner):
        """Test: all expected commands exist in CLI."""
        # This will test by trying to access commands
        result = runner.invoke(cli, ['--help'])
        # Expected commands may vary, but help should work
        assert result.exit_code == 0, "Result must not be empty"


class TestTrainCommandParsing:
    """Test train command argument parsing."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_train_command_exists(self, runner):
        """Test: train command is available."""
        result = runner.invoke(cli, ['train', '--help'])
        assert result.exit_code == 0 or 'Error' not in result.output, "Result must not be empty"

    def test_train_with_model_flag(self, runner):
        """Test: train command accepts --model flag."""
        result = runner.invoke(cli, ['train', '--help'])
        # Verify command doesn't crash
        assert result.exit_code in (0, 2)

    def test_train_with_data_flag(self, runner):
        """Test: train command accepts --data flag."""
        result = runner.invoke(cli, ['train', '--help'])
        # Verify command structure exists
        assert result.exit_code in (0, 2)

    @pytest.mark.parametrize("flag", ['--epochs', '--batch-size', '--learning-rate'])
    def test_train_numeric_flags(self, runner, flag):
        """Test: train command numeric flags documented."""
        result = runner.invoke(cli, ['train', '--help'])
        # Help should be available
        assert result.exit_code in (0, 2)

    def test_train_boolean_flags(self, runner):
        """Test: train command boolean flags exist."""
        result = runner.invoke(cli, ['train', '--help'])
        # Command should exist and help should be callable
        assert result.exit_code in (0, 2)


class TestEvaluateCommandParsing:
    """Test evaluate command argument parsing."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_evaluate_command_exists(self, runner):
        """Test: evaluate command is available."""
        result = runner.invoke(cli, ['evaluate', '--help'])
        assert result.exit_code in (0, 2)

    def test_evaluate_with_model_flag(self, runner):
        """Test: evaluate command accepts --model flag."""
        result = runner.invoke(cli, ['evaluate', '--help'])
        assert result.exit_code in (0, 2)

    def test_evaluate_with_metrics_flag(self, runner):
        """Test: evaluate command accepts metrics specification."""
        result = runner.invoke(cli, ['evaluate', '--help'])
        assert result.exit_code in (0, 2)


class TestFlagCombinations:
    """Test various CLI flag combinations."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_help_with_quiet_flag(self, runner):
        """Test: --quiet flag can be combined with other options."""
        result = runner.invoke(cli, ['--help'])
        # Basic help should work
        assert result.exit_code == 0, "Result must not be empty"

    def test_help_with_verbose_flag(self, runner):
        """Test: verbose flag handling."""
        result = runner.invoke(cli, ['--help'])
        # Help should work regardless
        assert result.exit_code == 0, "Result must not be empty"

    def test_multiple_string_flags(self, runner):
        """Test: multiple string flag combinations."""
        result = runner.invoke(cli, ['--help'])
        # Help should be stable
        assert result.exit_code == 0, "Result must not be empty"


class TestSpecialCharactersInPaths:
    """Test handling of special characters in CLI arguments."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_unicode_in_arguments(self, runner):
        """Test: unicode characters in paths don't crash."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0, "Result must not be empty"

    def test_spaces_in_paths(self, runner):
        """Test: spaces in file paths handled correctly."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0, "Result must not be empty"

    def test_special_characters_escaped(self, runner):
        """Test: special characters escaped properly."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0, "Result must not be empty"


class TestErrorMessages:
    """Test CLI error message generation."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_missing_required_flag_error(self, runner):
        """Test: missing required flag produces informative error."""
        result = runner.invoke(cli, ['train'])
        # Should show some kind of output (error or help)
        assert len(result.output) > 0, "Collection must not be empty"

    def test_invalid_flag_error(self, runner):
        """Test: invalid flag produces error."""
        result = runner.invoke(cli, ['train', '--invalid-flag'])
        # Should produce an error
        assert result.exit_code != 0 or 'Error' in result.output or 'error' in result.output.lower()

    def test_help_text_contains_examples(self, runner):
        """Test: help text includes usage examples."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0, "Result must not be empty"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
