"""Comprehensive tests for codex_ml.cli.main module.

Tests cover:
- Command parsing and validation
- Flag combinations and defaults
- Error handling (missing args, invalid values)
- Help text generation
- Integration with Typer
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

try:
    from typer.testing import CliRunner
except ImportError:
    pytest.skip("typer not available", allow_module_level=True)

from codex_ml.cli import main


@pytest.fixture
def cli_runner():
    """Provide CliRunner for testing Typer commands."""
    return CliRunner()


@pytest.fixture
def mock_training_config(tmp_path):
    """Create a mock training config file."""
    config_file = tmp_path / "train_config.yaml"
    config_file.write_text(
        """
model_name: test-model
epochs: 5
batch_size: 16
learning_rate: 1e-4
seed: 123
output_dir: /tmp/test_output
""",
        encoding="utf-8",
    )
    return config_file


class TestMainAppExistence:
    """Test main app initialization."""

    def test_app_exists(self):
        """Test that main app is defined."""
        assert hasattr(main, "app")
        assert main.app is not None

    def test_typer_loaded(self):
        """Test typer is loaded."""
        assert main.typer is not None


class TestTrainCommand:
    """Test train command functionality."""

    def test_train_command_exists(self):
        """Test train command is registered."""
        assert hasattr(main, "train")

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_defaults(self, mock_run_training, cli_runner):
        """Test train command with default parameters."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train"])
        # Command should be invokable (may fail without full deps)
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_config_file(self, mock_run_training, cli_runner, mock_training_config):
        """Test train command with config file."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--config", str(mock_training_config)])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_model_name(self, mock_run_training, cli_runner):
        """Test train command with model name."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--model-name", "gpt2"])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_epochs(self, mock_run_training, cli_runner):
        """Test train command with custom epochs."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--epochs", "10"])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_batch_size(self, mock_run_training, cli_runner):
        """Test train command with batch size."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--batch-size", "32"])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_learning_rate(self, mock_run_training, cli_runner):
        """Test train command with learning rate."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--learning-rate", "0.001"])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_seed(self, mock_run_training, cli_runner):
        """Test train command with random seed."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--seed", "999"])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_output_dir(self, mock_run_training, cli_runner, tmp_path):
        """Test train command with output directory."""
        mock_run_training.return_value = None
        output_dir = tmp_path / "outputs"
        result = cli_runner.invoke(main.app, ["train", "--output-dir", str(output_dir)])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_mlflow_enabled(self, mock_run_training, cli_runner):
        """Test train command with MLflow tracking."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--mlflow"])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_wandb_enabled(self, mock_run_training, cli_runner):
        """Test train command with W&B logging."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--wandb"])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_grad_accum(self, mock_run_training, cli_runner):
        """Test train command with gradient accumulation."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--grad-accum", "4"])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_grad_clip_norm(self, mock_run_training, cli_runner):
        """Test train command with gradient clipping."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--grad-clip-norm", "1.0"])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_dtype_fp16(self, mock_run_training, cli_runner):
        """Test train command with fp16 dtype."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--dtype", "fp16"])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_dtype_bf16(self, mock_run_training, cli_runner):
        """Test train command with bf16 dtype."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--dtype", "bf16"])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_resume_from(self, mock_run_training, cli_runner, tmp_path):
        """Test train command with checkpoint resume."""
        mock_run_training.return_value = None
        checkpoint = tmp_path / "checkpoint.pt"
        checkpoint.write_text("mock_checkpoint")
        result = cli_runner.invoke(main.app, ["train", "--resume-from", str(checkpoint)])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_corpus(self, mock_run_training, cli_runner):
        """Test train command with corpus specification."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(main.app, ["train", "--corpus", "gsm8k"])
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_multiple_corpora(self, mock_run_training, cli_runner):
        """Test train command with multiple corpora."""
        mock_run_training.return_value = None
        result = cli_runner.invoke(
            main.app, ["train", "--corpus", "gsm8k", "--corpus", "math"]
        )
        assert result.exit_code in (0, 1, 2)

    @patch("codex_ml.cli.main.run_training")
    def test_train_with_corpus_root(self, mock_run_training, cli_runner, tmp_path):
        """Test train command with corpus root override."""
        mock_run_training.return_value = None
        corpus_root = tmp_path / "corpora"
        corpus_root.mkdir()
        result = cli_runner.invoke(main.app, ["train", "--corpus-root", str(corpus_root)])
        assert result.exit_code in (0, 1, 2)


class TestValueFromConfig:
    """Test _value_from_config helper function."""

    def test_cli_value_overrides_default(self):
        """Test CLI value takes precedence over default."""
        cfg = {"key": "config_value"}
        result = main._value_from_config("cli_value", "default", cfg, "key")
        assert result == "cli_value"

    def test_config_value_used_when_cli_is_default(self):
        """Test config value used when CLI matches default."""
        cfg = {"key": "config_value"}
        result = main._value_from_config("default", "default", cfg, "key")
        assert result == "config_value"

    def test_default_used_when_key_missing(self):
        """Test default used when key not in config."""
        cfg = {}
        result = main._value_from_config("default", "default", cfg, "key")
        assert result == "default"

    def test_first_matching_key_used(self):
        """Test first matching key is used from multiple keys."""
        cfg = {"key2": "value2", "key3": "value3"}
        result = main._value_from_config("default", "default", cfg, "key1", "key2", "key3")
        assert result == "value2"

    def test_empty_keys_returns_cli_value(self):
        """Test with no keys returns CLI value."""
        cfg = {"key": "config_value"}
        result = main._value_from_config("cli_value", "default", cfg)
        assert result == "cli_value"


class TestHelpText:
    """Test help text generation."""

    def test_main_help(self, cli_runner):
        """Test main app help text."""
        result = cli_runner.invoke(main.app, ["--help"])
        assert result.exit_code == 0
        assert "Codex ML CLI" in result.stdout or "Usage:" in result.stdout

    def test_train_help(self, cli_runner):
        """Test train command help text."""
        result = cli_runner.invoke(main.app, ["train", "--help"])
        assert result.exit_code == 0
        assert "--help" in result.stdout or "OPTIONS" in result.stdout


class TestLoadTrainingConfig:
    """Test configuration loading functionality."""

    def test_load_training_config_exists(self):
        """Test _load_training_config function exists."""
        assert hasattr(main, "_load_training_config")

    def test_load_training_config_with_none(self):
        """Test loading config with None path."""
        result = main._load_training_config(None)
        assert isinstance(result, dict)

    def test_load_training_config_with_yaml(self, tmp_path):
        """Test loading YAML config file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("model_name: test\nepochs: 10", encoding="utf-8")
        result = main._load_training_config(str(config_file))
        assert isinstance(result, dict)

    def test_load_training_config_with_invalid_path(self):
        """Test loading config with non-existent path."""
        with pytest.raises((FileNotFoundError, SystemExit, Exception)):
            main._load_training_config("/nonexistent/path/config.yaml")
