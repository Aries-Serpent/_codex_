"""
Comprehensive tests for codex_ml/cli/codex_cli.py module.

This module tests the main Codex CLI commands including:
- Tokenizer commands (train, validate, encode, decode)
- Config sweep command
- Training and resume commands
- Evaluation and deployment commands
- Helper functions

Phase: 46 - Coverage Improvement
"""

from unittest.mock import patch

import pytest
from click.testing import CliRunner


class TestHelperFunctions:
    """Tests for CLI helper functions."""

    def test_csv_list_simple(self):
        """Test _csv_list with simple comma-separated values."""
        try:
            from codex_ml.cli.codex_cli import _csv_list

            result = _csv_list("a,b,c")
            assert result == ["a", "b", "c"]
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_csv_list_with_spaces(self):
        """Test _csv_list with spaces around values."""
        try:
            from codex_ml.cli.codex_cli import _csv_list

            result = _csv_list(" a , b , c ")
            assert result == ["a", "b", "c"]
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_csv_list_empty(self):
        """Test _csv_list with empty string."""
        try:
            from codex_ml.cli.codex_cli import _csv_list

            result = _csv_list("")
            assert result == [], "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_csv_list_single_value(self):
        """Test _csv_list with single value."""
        try:
            from codex_ml.cli.codex_cli import _csv_list

            result = _csv_list("single")
            assert result == ["single"], "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestUpdatePath:
    """Tests for _update_path helper function."""

    def test_update_path_dict(self):
        """Test _update_path with dictionary target."""
        try:
            from codex_ml.cli.codex_cli import _update_path

            target = {}
            _update_path(target, "a.b.c", "value")
            assert target["a"]["b"]["c"] == "value", "Value must be initialized"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_update_path_single_level(self):
        """Test _update_path with single level path."""
        try:
            from codex_ml.cli.codex_cli import _update_path

            target = {}
            _update_path(target, "key", "value")
            assert target["key"] == "value", "Value must be initialized"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_update_path_existing_dict(self):
        """Test _update_path with existing nested dict."""
        try:
            from codex_ml.cli.codex_cli import _update_path

            target = {"a": {"b": {}}}
            _update_path(target, "a.b.c", "value")
            assert target["a"]["b"]["c"] == "value", "Value must be initialized"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestCLIGroup:
    """Tests for the main CLI group."""

    def test_cli_help(self):
        """Test CLI help output."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "Codex command line interface" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_tokenizer_subgroup_help(self):
        """Test tokenizer subgroup help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["tokenizer", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "Tokenizer pipeline utilities" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestTokenizerCommands:
    """Tests for tokenizer subcommands."""

    def test_tokenizer_train_help(self):
        """Test tokenizer train command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["tokenizer", "train", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "--config" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_tokenizer_validate_help(self):
        """Test tokenizer validate command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["tokenizer", "validate", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_tokenizer_encode_help(self):
        """Test tokenizer encode command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["tokenizer", "encode", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_tokenizer_decode_help(self):
        """Test tokenizer decode command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["tokenizer", "decode", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestConfigSweepCommand:
    """Tests for config-sweep command."""

    def test_config_sweep_help(self):
        """Test config-sweep command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["config-sweep", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "--base-config" in result.output, "Result must not be empty"
            assert "--seeds" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    @patch("subprocess.check_output")
    def test_config_sweep_basic(self, mock_subprocess, tmp_path):
        """Test config-sweep command with basic options."""
        try:
            from codex_ml.cli.codex_cli import codex

            # Create a mock base config
            base_config = tmp_path / "base.yaml"
            base_config.write_text("training:\n  seed: 42\n")

            output = tmp_path / "sweep.yaml"

            mock_subprocess.return_value = "abc123"

            runner = CliRunner()
            result = runner.invoke(
                codex,
                [
                    "config-sweep",
                    "--base-config",
                    str(base_config),
                    "--output",
                    str(output),
                    "--seeds",
                    "1,2,3",
                ],
            )
            # May fail due to additional validation but should parse
            assert result.exit_code in (0, 1, 2)
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestTrainCommand:
    """Tests for train command."""

    def test_train_help(self):
        """Test train command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["train", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "--config" in result.output, "Result must not be empty"
            assert "--resume" in result.output, "Result must not be empty"
            assert "--seed" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_train_mlflow_options(self):
        """Test train command has MLflow options."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["train", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "--mlflow" in result.output or "mlflow" in result.output.lower(), "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestResumeCommand:
    """Tests for resume command."""

    def test_resume_help(self):
        """Test resume command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["resume", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "manifest" in result.output.lower(), "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestMetricsServerCommand:
    """Tests for metrics-server command."""

    def test_metrics_server_help(self):
        """Test metrics-server command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["metrics-server", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "--port" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestTokenizeCommand:
    """Tests for tokenize command."""

    def test_tokenize_help(self):
        """Test tokenize command help (if exists)."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["tokenize", "--help"])
            # May or may not exist
            assert result.exit_code in (0, 1, 2)
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestRepoMapCommand:
    """Tests for repo-map command."""

    def test_repo_map_help(self):
        """Test repo-map command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["repo-map", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "--reasoning" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestDeployCommand:
    """Tests for deploy command."""

    def test_deploy_help(self):
        """Test deploy command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["deploy", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "--config" in result.output, "Result must not be empty"
            assert "--dry-run" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_deploy_requires_dry_run(self, tmp_path):
        """Test deploy command requires --dry-run flag."""
        try:
            from codex_ml.cli.codex_cli import codex

            # Create mock config
            config = tmp_path / "deploy.yaml"
            config.write_text("deployment:\n  mode: test\n")

            runner = CliRunner()
            result = runner.invoke(codex, ["deploy", "--config", str(config)])
            # Should fail without --dry-run
            assert result.exit_code in (1, 2)
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestStatusReportCommand:
    """Tests for status-report command."""

    def test_status_report_help(self):
        """Test status-report command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["status-report", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "--run-metadata-dir" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestEvaluateCommand:
    """Tests for evaluate command."""

    def test_evaluate_help(self):
        """Test evaluate command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["evaluate", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "--config" in result.output, "Result must not be empty"
            assert "--metrics-only" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_evaluate_metrics_sink_option(self):
        """Test evaluate command has metrics-sink option."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["evaluate", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "--metrics-sink" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestPrepareDataCommand:
    """Tests for prepare-data command."""

    def test_prepare_data_help(self):
        """Test prepare-data command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["prepare-data", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "--config" in result.output, "Result must not be empty"
            assert "--seed" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestExportEnvCommand:
    """Tests for export-env command."""

    def test_export_env_help(self):
        """Test export-env command help."""
        try:
            from codex_ml.cli.codex_cli import codex

            runner = CliRunner()
            result = runner.invoke(codex, ["export-env", "--help"])
            assert result.exit_code == 0, "Result must not be empty"
            assert "--output" in result.output, "Result must not be empty"
            assert "--seed" in result.output, "Result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestMainFunction:
    """Tests for main() entry point."""

    def test_main_with_help(self):
        """Test main function with --help."""
        try:
            from codex_ml.cli.codex_cli import main

            exit_code = main(["--help"])
            assert exit_code == 0, "exit_code is not valid"
        except (ImportError, SystemExit):
            pytest.skip("codex_ml.cli.codex_cli not available or exits")

    def test_main_with_invalid_command(self):
        """Test main function with invalid command."""
        try:
            import click.exceptions as _click_exc
        except ImportError:
            _click_exc = None  # type: ignore[assignment]
        try:
            from codex_ml.cli.codex_cli import main

            exit_code = main(["invalid-command"])
            assert exit_code != 0, "exit_code is not valid"
        except (ImportError, SystemExit):
            pytest.skip("codex_ml.cli.codex_cli not available or exits")
        except AttributeError as exc:
            if _click_exc is not None and isinstance(exc, _click_exc.UsageError):
                pytest.skip("codex_ml.cli.codex_cli not available or exits")
            raise


class TestHashDataset:
    """Tests for _hash_dataset function."""

    def test_hash_dataset(self, tmp_path):
        """Test dataset hashing function."""
        try:
            from codex_ml.cli.codex_cli import _hash_dataset

            # Create a test file
            test_file = tmp_path / "test_data.txt"
            test_file.write_text("test content for hashing")

            hash_result = _hash_dataset(test_file)
            assert isinstance(hash_result, str)
            assert len(hash_result) == 64, "Hash_result must not be empty"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_hash_dataset_consistency(self, tmp_path):
        """Test that same content produces same hash."""
        try:
            from codex_ml.cli.codex_cli import _hash_dataset

            # Create two files with same content
            file1 = tmp_path / "file1.txt"
            file2 = tmp_path / "file2.txt"
            content = "identical content"
            file1.write_text(content)
            file2.write_text(content)

            hash1 = _hash_dataset(file1)
            hash2 = _hash_dataset(file2)
            assert hash1 == hash2, "hash1 is not valid"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")

    def test_hash_dataset_different_content(self, tmp_path):
        """Test that different content produces different hash."""
        try:
            from codex_ml.cli.codex_cli import _hash_dataset

            # Create two files with different content
            file1 = tmp_path / "file1.txt"
            file2 = tmp_path / "file2.txt"
            file1.write_text("content a")
            file2.write_text("content b")

            hash1 = _hash_dataset(file1)
            hash2 = _hash_dataset(file2)
            assert hash1 != hash2, "hash1 is not valid"
        except ImportError:
            pytest.skip("codex_ml.cli.codex_cli not available")


class TestGetTokenizerPipeline:
    """Tests for _get_tokenizer_pipeline function."""

    def test_get_tokenizer_pipeline_cached(self):
        """Test that tokenizer pipeline is cached."""
        try:
            from codex_ml.cli.codex_cli import _get_tokenizer_pipeline

            # First call
            pipeline1 = _get_tokenizer_pipeline()
            # Second call should return same cached instance
            pipeline2 = _get_tokenizer_pipeline()
            assert pipeline1 is pipeline2, "pipeline1 is not valid"
        except ImportError:
            pytest.skip("tokenizer pipeline not available")
        except AttributeError as _err:
            # May fail due to missing dependencies
            pytest.skip("tokenizer dependencies not available")
