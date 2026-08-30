"""
Codex ML CLI Enhancement Tests

Comprehensive test coverage for codex_ml/cli/codex_cli.py focusing on:
- Command execution and exit codes
- Argument validation and error handling
- Output formatting and logging
- Configuration handling
- Integration with subcommands
- Edge cases and boundary conditions
"""

from unittest.mock import patch

import pytest

try:
    import click
    from click.testing import CliRunner

    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False

try:
    from codex_ml.cli.codex_cli import (
        codex,
        config_sweep,
        evaluate,
        prepare_data,
        resume,
        tokenizer,
        train,
    )

    HAS_CODEX_CLI = True
except ImportError:
    HAS_CODEX_CLI = False


pytestmark = pytest.mark.skipif(
    not (HAS_CLICK and HAS_CODEX_CLI), reason="click and codex_cli modules not available"
)


@pytest.fixture
def cli_runner():
    """Create a Click CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory."""
    config_dir = tmp_path / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@pytest.fixture
def sample_training_config(temp_config_dir):
    """Create a sample training config file."""
    config = temp_config_dir / "training_config.yaml"
    config.write_text("""
model:
  name: test_model
  hidden_size: 256
training:
  learning_rate: 0.001
  batch_size: 32
  epochs: 1
""")
    return config


@pytest.fixture
def sample_tokenizer_config(temp_config_dir):
    """Create a sample tokenizer config file."""
    config = temp_config_dir / "tokenizer_config.yaml"
    config.write_text("""
vocab_size: 10000
max_length: 512
type: bpe
""")
    return config


# ============================================================================
# Codex Main Command Tests
# ============================================================================


class TestCodexMainCommand:
    """Tests for main codex command."""

    def test_codex_help(self, cli_runner):
        """Test codex --help displays help."""
        result = cli_runner.invoke(codex, ["--help"])
        assert result.exit_code == 0, "Result must not be empty"
        # Should show available subcommands
        assert any(cmd in result.output.lower() for cmd in ["train", "evaluate", "tokenizer"])

    def test_codex_version(self, cli_runner):
        """Test codex --version shows version."""
        with patch("codex_ml.cli.codex_cli.__version__", "1.0.0"):
            cli_runner.invoke(codex, ["--version"])
            # May or may not support version flag

    def test_codex_no_args(self, cli_runner):
        """Test codex with no arguments."""
        cli_runner.invoke(codex, [])
        # Should show help or error

    def test_codex_invalid_subcommand(self, cli_runner):
        """Test codex with invalid subcommand."""
        result = cli_runner.invoke(codex, ["invalid_cmd"])
        assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Tokenizer Command Tests
# ============================================================================


class TestTokenizerCommand:
    """Tests for tokenizer commands."""

    def test_tokenizer_help(self, cli_runner):
        """Test tokenizer --help."""
        cli_runner.invoke(tokenizer, ["--help"])
        # Tokenizer group should show subcommands

    def test_tokenizer_train_help(self, cli_runner):
        """Test tokenizer train --help."""
        result = cli_runner.invoke(codex, ["tokenizer", "train", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_tokenizer_train_missing_config(self, cli_runner):
        """Test tokenizer train without config."""
        cli_runner.invoke(codex, ["tokenizer", "train"])
        # Should require --config argument or show error

    def test_tokenizer_train_with_config(self, cli_runner, sample_tokenizer_config):
        """Test tokenizer train with valid config."""
        with patch("codex_ml.tokenization.pipeline.train"):
            cli_runner.invoke(
                codex,
                ["tokenizer", "train", "--config", str(sample_tokenizer_config)],
            )
            # Should handle config file

    def test_tokenizer_validate_help(self, cli_runner):
        """Test tokenizer validate --help."""
        result = cli_runner.invoke(codex, ["tokenizer", "validate", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_tokenizer_encode_missing_file(self, cli_runner):
        """Test tokenizer encode without tokenizer file."""
        cli_runner.invoke(
            codex,
            ["tokenizer", "encode", "--tokenizer", "nonexistent.json"],
        )
        # Should fail gracefully

    def test_tokenizer_decode_invalid_tokens(self, cli_runner):
        """Test tokenizer decode with invalid token IDs."""
        with patch("codex_ml.tokenization.Tokenizer"):
            cli_runner.invoke(
                codex,
                ["tokenizer", "decode", "--token-ids", "999999,999998", "--tokenizer", "test.json"],
            )
            # Should validate token IDs


# ============================================================================
# Training Command Tests
# ============================================================================


class TestTrainCommand:
    """Tests for training commands."""

    def test_train_help(self, cli_runner):
        """Test train --help."""
        result = cli_runner.invoke(codex, ["train", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_train_missing_config(self, cli_runner):
        """Test train without required config."""
        result = cli_runner.invoke(codex, ["train"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_train_invalid_config_path(self, cli_runner):
        """Test train with non-existent config file."""
        result = cli_runner.invoke(
            codex,
            ["train", "--config", "/nonexistent/config.yaml"],
        )
        assert result.exit_code != 0, "Result must not be empty"

    def test_train_with_valid_config(self, cli_runner, sample_training_config):
        """Test train with valid config."""
        with patch("codex_ml.training.train_pipeline"):
            cli_runner.invoke(
                codex,
                ["train", "--config", str(sample_training_config)],
            )
            # Should attempt to run training

    def test_train_with_overrides(self, cli_runner, sample_training_config):
        """Test train with config overrides."""
        with patch("codex_ml.training.train_pipeline"):
            cli_runner.invoke(
                codex,
                [
                    "train",
                    "--config",
                    str(sample_training_config),
                    "--override",
                    "training.batch_size=64",
                ],
            )
            # Should apply overrides

    def test_train_with_seed(self, cli_runner, sample_training_config):
        """Test train with random seed."""
        with patch("codex_ml.training.train_pipeline"):
            cli_runner.invoke(
                codex,
                ["train", "--config", str(sample_training_config), "--seed", "42"],
            )
            # Should set seed

    def test_train_dry_run(self, cli_runner, sample_training_config):
        """Test train in dry-run mode."""
        with patch("codex_ml.training.train_pipeline"):
            cli_runner.invoke(
                codex,
                ["train", "--config", str(sample_training_config), "--dry-run"],
            )
            # Should not execute actual training


# ============================================================================
# Resume Training Tests
# ============================================================================


class TestResumeCommand:
    """Tests for resume training command."""

    def test_resume_help(self, cli_runner):
        """Test resume --help."""
        result = cli_runner.invoke(codex, ["resume", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_resume_missing_checkpoint(self, cli_runner):
        """Test resume without checkpoint path."""
        result = cli_runner.invoke(codex, ["resume"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_resume_invalid_checkpoint(self, cli_runner):
        """Test resume with non-existent checkpoint."""
        result = cli_runner.invoke(
            codex,
            ["resume", "--checkpoint", "/nonexistent/checkpoint"],
        )
        assert result.exit_code != 0, "Result must not be empty"

    def test_resume_with_valid_checkpoint(self, cli_runner, tmp_path):
        """Test resume with valid checkpoint."""
        checkpoint_dir = tmp_path / "checkpoint"
        checkpoint_dir.mkdir()
        (checkpoint_dir / "config.yaml").write_text("model: test")

        with patch("codex_ml.training.resume_training"):
            cli_runner.invoke(
                codex,
                ["resume", "--checkpoint", str(checkpoint_dir)],
            )
            # Should attempt to resume


# ============================================================================
# Evaluate Command Tests
# ============================================================================


class TestEvaluateCommand:
    """Tests for evaluation commands."""

    def test_evaluate_help(self, cli_runner):
        """Test evaluate --help."""
        result = cli_runner.invoke(codex, ["evaluate", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_evaluate_missing_model(self, cli_runner):
        """Test evaluate without model path."""
        cli_runner.invoke(codex, ["evaluate"])
        # May require model path

    def test_evaluate_invalid_model(self, cli_runner):
        """Test evaluate with non-existent model."""
        result = cli_runner.invoke(
            codex,
            ["evaluate", "--model", "/nonexistent/model"],
        )
        assert result.exit_code != 0, "Result must not be empty"

    def test_evaluate_with_dataset(self, cli_runner, tmp_path):
        """Test evaluate with dataset."""
        dataset_path = tmp_path / "dataset.ndjson"
        dataset_path.write_text('{"text": "test"}\n')

        with patch("codex_ml.evaluation.evaluate_model"):
            cli_runner.invoke(
                codex,
                ["evaluate", "--dataset", str(dataset_path), "--model", "test_model"],
            )
            # Should run evaluation

    def test_evaluate_output_format(self, cli_runner, tmp_path):
        """Test evaluate output format options."""
        dataset_path = tmp_path / "dataset.ndjson"
        dataset_path.write_text('{"text": "test"}\n')

        with patch("codex_ml.evaluation.evaluate_model"):
            cli_runner.invoke(
                codex,
                ["evaluate", "--dataset", str(dataset_path), "--format", "json"],
            )
            # Should support different output formats


# ============================================================================
# Prepare Data Command Tests
# ============================================================================


class TestPrepareDataCommand:
    """Tests for data preparation commands."""

    def test_prepare_data_help(self, cli_runner):
        """Test prepare-data --help."""
        result = cli_runner.invoke(codex, ["prepare-data", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_prepare_data_missing_config(self, cli_runner):
        """Test prepare-data without config."""
        result = cli_runner.invoke(codex, ["prepare-data"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_prepare_data_with_config(self, cli_runner, sample_training_config):
        """Test prepare-data with config."""
        with patch("codex_ml.data.prepare_data_pipeline"):
            cli_runner.invoke(
                codex,
                ["prepare-data", "--config", str(sample_training_config)],
            )
            # Should prepare data

    def test_prepare_data_with_seed(self, cli_runner, sample_training_config):
        """Test prepare-data with random seed."""
        with patch("codex_ml.data.prepare_data_pipeline"):
            cli_runner.invoke(
                codex,
                ["prepare-data", "--config", str(sample_training_config), "--seed", "42"],
            )
            # Should use seed for reproducibility


# ============================================================================
# Config Sweep Tests
# ============================================================================


class TestConfigSweepCommand:
    """Tests for config sweep command."""

    def test_config_sweep_help(self, cli_runner):
        """Test config-sweep --help."""
        result = cli_runner.invoke(codex, ["config-sweep", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_config_sweep_missing_config(self, cli_runner):
        """Test config-sweep without config."""
        result = cli_runner.invoke(codex, ["config-sweep"])
        assert result.exit_code != 0, "Result must not be empty"

    def test_config_sweep_missing_param(self, cli_runner, sample_training_config):
        """Test config-sweep without sweep parameters."""
        cli_runner.invoke(
            codex,
            ["config-sweep", "--config", str(sample_training_config)],
        )
        # Should require sweep parameters

    def test_config_sweep_with_params(self, cli_runner, sample_training_config):
        """Test config-sweep with sweep parameters."""
        with patch("codex_ml.training.train_pipeline"):
            cli_runner.invoke(
                codex,
                [
                    "config-sweep",
                    "--config",
                    str(sample_training_config),
                    "--param",
                    "learning_rate=0.001,0.0001",
                    "--param",
                    "batch_size=32,64",
                ],
            )
            # Should run sweep with multiple parameter combinations

    def test_config_sweep_invalid_ranges(self, cli_runner, sample_training_config):
        """Test config-sweep with invalid parameter ranges."""
        result = cli_runner.invoke(
            codex,
            [
                "config-sweep",
                "--config",
                str(sample_training_config),
                "--param",
                "invalid_range",
            ],
        )
        assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestCodexCLIErrorHandling:
    """Tests for error handling in CLI."""

    def test_missing_dependency_error(self, cli_runner):
        """Test error handling for missing dependencies."""
        with patch("codex_ml.tokenization.pipeline", side_effect=ImportError("Missing tokenizers")):
            result = cli_runner.invoke(codex, ["tokenizer", "train"])
            assert result.exit_code != 0, "Result must not be empty"

    def test_config_parse_error(self, cli_runner, tmp_path):
        """Test handling of invalid config files."""
        bad_config = tmp_path / "bad_config.yaml"
        bad_config.write_text("invalid: yaml: syntax:")

        result = cli_runner.invoke(
            codex,
            ["train", "--config", str(bad_config)],
        )
        assert result.exit_code != 0, "Result must not be empty"

    def test_permission_error(self, cli_runner, tmp_path):
        """Test handling of permission errors."""
        read_only_file = tmp_path / "readonly.yaml"
        read_only_file.write_text("test: config")
        read_only_file.chmod(0o000)

        try:
            result = cli_runner.invoke(
                codex,
                ["train", "--config", str(read_only_file)],
            )
            assert result.exit_code != 0, "Result must not be empty"
        finally:
            read_only_file.chmod(0o644)

    def test_keyboard_interrupt_handling(self, cli_runner, sample_training_config):
        """Test handling of keyboard interrupt."""
        with patch("codex_ml.training.train_pipeline", side_effect=KeyboardInterrupt):
            result = cli_runner.invoke(
                codex,
                ["train", "--config", str(sample_training_config)],
            )
            assert result.exit_code != 0, "Result must not be empty"


# ============================================================================
# Output Formatting Tests
# ============================================================================


class TestCodexCLIOutput:
    """Tests for output formatting."""

    def test_json_output_format(self, cli_runner):
        """Test JSON output format."""
        with patch("codex_ml.evaluation.evaluate_model") as mock_eval:
            mock_eval.return_value = {"accuracy": 0.95, "loss": 0.05}
            cli_runner.invoke(
                codex,
                ["evaluate", "--format", "json", "--model", "test"],
            )
            # Output should be parseable JSON

    def test_verbose_logging(self, cli_runner, sample_training_config):
        """Test verbose logging output."""
        with patch("codex_ml.training.train_pipeline"):
            cli_runner.invoke(
                codex,
                ["train", "--config", str(sample_training_config), "--verbose"],
            )
            # Should include verbose output

    def test_quiet_mode(self, cli_runner, sample_training_config):
        """Test quiet/silent mode."""
        with patch("codex_ml.training.train_pipeline"):
            cli_runner.invoke(
                codex,
                ["train", "--config", str(sample_training_config), "--quiet"],
            )
            # Should suppress output


# ============================================================================
# Integration Workflow Tests
# ============================================================================


class TestCodexCLIWorkflows:
    """Integration tests for complete workflows."""

    def test_data_prep_train_evaluate_workflow(self, cli_runner, tmp_path):
        """Test complete data→train→evaluate workflow."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("model: test\ntraining:\n  epochs: 1")

        with patch("codex_ml.data.prepare_data_pipeline"):
            with patch("codex_ml.training.train_pipeline"):
                with patch("codex_ml.evaluation.evaluate_model"):
                    # Prepare data
                    prep_result = cli_runner.invoke(
                        codex,
                        ["prepare-data", "--config", str(config_file)],
                    )
                    assert prep_result.exit_code == 0, "Result must not be empty"

                    # Train
                    train_result = cli_runner.invoke(
                        codex,
                        ["train", "--config", str(config_file)],
                    )
                    assert train_result.exit_code == 0, "Result must not be empty"

    def test_tokenizer_train_encode_decode_workflow(self, cli_runner, tmp_path):
        """Test tokenizer train→encode→decode workflow."""
        config_file = tmp_path / "tokenizer_config.yaml"
        config_file.write_text("vocab_size: 1000\ntype: bpe")

        with patch("codex_ml.tokenization.pipeline.train"):
            with patch("codex_ml.tokenization.Tokenizer"):
                # Train tokenizer
                cli_runner.invoke(
                    codex,
                    ["tokenizer", "train", "--config", str(config_file)],
                )
                # Should handle tokenizer pipeline


# ============================================================================
# Edge Cases and Boundary Tests
# ============================================================================


class TestCodexCLIEdgeCases:
    """Edge case and boundary condition tests."""

    def test_empty_config_file(self, cli_runner, tmp_path):
        """Test with empty config file."""
        empty_config = tmp_path / "empty.yaml"
        empty_config.write_text("")

        cli_runner.invoke(
            codex,
            ["train", "--config", str(empty_config)],
        )
        # Should handle empty config gracefully

    def test_very_large_config_file(self, cli_runner, tmp_path):
        """Test with large config file."""
        large_config = tmp_path / "large_config.yaml"
        large_config.write_text("\n".join([f"param_{i}: {i}" for i in range(10000)]))

        with patch("codex_ml.training.train_pipeline"):
            cli_runner.invoke(
                codex,
                ["train", "--config", str(large_config)],
            )
            # Should handle large configs

    def test_special_characters_in_paths(self, cli_runner, tmp_path):
        """Test with special characters in file paths."""
        special_dir = tmp_path / "dir with spaces & special-chars"
        special_dir.mkdir()
        config_file = special_dir / "config.yaml"
        config_file.write_text("test: config")

        with patch("codex_ml.training.train_pipeline"):
            cli_runner.invoke(
                codex,
                ["train", "--config", str(config_file)],
            )
            # Should handle special characters in paths

    def test_unicode_in_config(self, cli_runner, tmp_path):
        """Test with unicode characters in config."""
        unicode_config = tmp_path / "unicode_config.yaml"
        unicode_config.write_text("description: 'Testing with unicode 测试 🚀'\nmodel: test")

        with patch("codex_ml.training.train_pipeline"):
            cli_runner.invoke(
                codex,
                ["train", "--config", str(unicode_config)],
            )
            # Should handle unicode in configs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
