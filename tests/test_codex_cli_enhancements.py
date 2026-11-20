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

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import click
import pytest
from click.testing import CliRunner

from codex_ml.cli.codex_cli import codex


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
  max_epochs: 1
""")
    return config


@pytest.fixture
def mock_training():
    """Patch the functional trainer the ``train``/``resume`` commands delegate to."""
    with patch("codex_ml.training.run_functional_training") as run:
        yield run


class _FakeTokenizerPipelineError(Exception):
    pass


@pytest.fixture
def fake_tokenizer_pipeline():
    """Replace the lazily-imported tokenizer pipeline with an in-memory fake."""
    pipeline = SimpleNamespace(
        TokenizerPipelineError=_FakeTokenizerPipelineError,
        run_train=MagicMock(return_value="out/tokenizer"),
        run_validate=MagicMock(return_value={"ok": True}),
        run_encode=MagicMock(return_value=[5, 6, 7]),
        run_decode=MagicMock(return_value="decoded text"),
    )
    with patch("codex_ml.cli.codex_cli._get_tokenizer_pipeline", return_value=pipeline):
        yield pipeline


def _fake_eval_cfg(tmp_path):
    return SimpleNamespace(
        evaluation=SimpleNamespace(seed=0, metrics_sink="ndjson", output_dir=str(tmp_path)),
        data=SimpleNamespace(),
    )


def _training_cfg_seen(run_mock):
    """Return the training config object passed to run_functional_training."""
    assert run_mock.call_count == 1, "run_functional_training must be called once"
    return run_mock.call_args.kwargs["config"]


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
        """The codex group exposes no --version flag; Click reports a usage error."""
        result = cli_runner.invoke(codex, ["--version"])
        assert result.exit_code == 2
        assert "No such option" in result.output

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
        result = cli_runner.invoke(codex, ["tokenizer", "--help"])
        assert result.exit_code == 0, result.output
        assert all(
            command in result.output for command in ("train", "validate", "encode", "decode")
        )

    def test_tokenizer_train_help(self, cli_runner):
        """Test tokenizer train --help."""
        result = cli_runner.invoke(codex, ["tokenizer", "train", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_tokenizer_train_missing_config(self, cli_runner):
        """A missing explicit tokenizer config is rejected before pipeline execution."""
        result = cli_runner.invoke(
            codex, ["tokenizer", "train", "--config", "missing-tokenizer-config.yaml"]
        )
        assert result.exit_code == 2

    def test_tokenizer_train_with_config(
        self, cli_runner, sample_tokenizer_config, fake_tokenizer_pipeline
    ):
        """Tokenizer train forwards the config and defaults to non-streaming mode."""
        result = cli_runner.invoke(
            codex,
            ["tokenizer", "train", "--config", str(sample_tokenizer_config)],
        )
        assert result.exit_code == 0, result.output
        assert "tokenizer artifacts written to out/tokenizer" in result.output
        fake_tokenizer_pipeline.run_train.assert_called_once_with(
            str(sample_tokenizer_config),
            streaming=None,
            stream_chunk_size=None,
            dry_run=False,
        )

    def test_tokenizer_validate_help(self, cli_runner):
        """Test tokenizer validate --help."""
        result = cli_runner.invoke(codex, ["tokenizer", "validate", "--help"])
        assert result.exit_code == 0, "Result must not be empty"

    def test_tokenizer_encode_missing_file(self, cli_runner, fake_tokenizer_pipeline):
        """Tokenizer load failures are presented as user-facing command errors."""
        fake_tokenizer_pipeline.run_encode.side_effect = _FakeTokenizerPipelineError(
            "tokenizer JSON file not found"
        )
        result = cli_runner.invoke(
            codex,
            ["tokenizer", "encode", "hello", "--tokenizer-path", "nonexistent.json"],
        )
        assert result.exit_code == 1
        assert "tokenizer JSON file not found" in result.output
        fake_tokenizer_pipeline.run_encode.assert_called_once_with("nonexistent.json", "hello")

    def test_tokenizer_decode_invalid_tokens(self, cli_runner, fake_tokenizer_pipeline):
        """Pipeline errors for out-of-vocabulary IDs surface as a Click error."""
        fake_tokenizer_pipeline.run_decode.side_effect = _FakeTokenizerPipelineError(
            "unknown token id 999999"
        )
        result = cli_runner.invoke(
            codex,
            ["tokenizer", "decode", "999999", "999998", "--tokenizer-path", "test.json"],
        )
        assert result.exit_code == 1
        assert "unknown token id 999999" in result.output
        fake_tokenizer_pipeline.run_decode.assert_called_once_with("test.json", (999999, 999998))


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

    def test_train_with_valid_config(self, cli_runner, sample_training_config, mock_training):
        """Test train with valid config delegates to the functional trainer."""
        result = cli_runner.invoke(codex, ["train", "--config", str(sample_training_config)])
        assert result.exit_code == 0, result.output
        assert "Training complete" in result.output
        cfg = _training_cfg_seen(mock_training)
        assert mock_training.call_args.kwargs["resume"] is False
        assert cfg.batch_size == 32

    def test_train_with_overrides(self, cli_runner, sample_training_config, mock_training):
        """Test train with positional Hydra-style overrides."""
        result = cli_runner.invoke(
            codex,
            ["train", "--config", str(sample_training_config), "training.batch_size=64"],
        )
        assert result.exit_code == 0, result.output
        assert _training_cfg_seen(mock_training).batch_size == 64

    def test_train_with_seed(self, cli_runner, sample_training_config, mock_training):
        """Test train with random seed override."""
        result = cli_runner.invoke(
            codex,
            ["train", "--config", str(sample_training_config), "--seed", "42"],
        )
        assert result.exit_code == 0, result.output
        assert _training_cfg_seen(mock_training).seed == 42

    def test_train_dry_run(self, cli_runner, sample_training_config, mock_training):
        """train has no --dry-run flag; it is rejected before any training runs."""
        result = cli_runner.invoke(
            codex,
            ["train", "--config", str(sample_training_config), "--dry-run"],
        )
        assert result.exit_code == 2
        mock_training.assert_not_called()


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

    def test_resume_with_valid_checkpoint(
        self, cli_runner, tmp_path, sample_training_config, mock_training
    ):
        """Test resume from a trainer manifest pointing at a checkpoint."""
        checkpoint_dir = tmp_path / "checkpoint"
        checkpoint_dir.mkdir()
        manifest = tmp_path / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "last_checkpoint": str(checkpoint_dir),
                    "config_path": str(sample_training_config),
                }
            )
        )

        result = cli_runner.invoke(codex, ["resume", str(manifest)])
        assert result.exit_code == 0, result.output
        assert f"resumed training from {checkpoint_dir}" in result.output
        assert mock_training.call_args.kwargs["resume"] is True

    def test_resume_manifest_without_checkpoint(self, cli_runner, tmp_path, mock_training):
        """A manifest lacking checkpoint information is rejected."""
        manifest = tmp_path / "manifest.json"
        manifest.write_text(json.dumps({"config_path": "unused.yaml"}))
        result = cli_runner.invoke(codex, ["resume", str(manifest)])
        assert result.exit_code == 1
        assert "manifest missing checkpoint information" in result.output
        mock_training.assert_not_called()


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
        """Test evaluate runs the evaluation runner and prints its JSON summary."""
        dataset_path = tmp_path / "dataset.ndjson"
        dataset_path.write_text('{"text": "test"}\n')
        summary = {"metrics": {"accuracy": 0.95}, "num_records": 1}

        with (
            patch(
                "codex_ml.cli.codex_cli.load_app_config",
                return_value=(_fake_eval_cfg(tmp_path), None),
            ) as load,
            patch("codex_ml.eval.runner.run_evaluation", return_value=summary) as run_eval,
        ):
            result = cli_runner.invoke(
                codex,
                ["evaluate", "--config", "eval.yaml", f"evaluation.dataset_path={dataset_path}"],
            )
        assert result.exit_code == 0, result.output
        load.assert_called_once_with("eval.yaml", (f"evaluation.dataset_path={dataset_path}",))
        run_eval.assert_called_once()
        assert json.loads(result.output) == summary

    def test_evaluate_output_format(self, cli_runner, tmp_path):
        """--metrics-only prints only the machine-readable metrics mapping."""
        summary = {"metrics": {"accuracy": 0.95, "loss": 0.05}, "num_records": 3}
        with (
            patch(
                "codex_ml.cli.codex_cli.load_app_config",
                return_value=(_fake_eval_cfg(tmp_path), None),
            ),
            patch("codex_ml.eval.runner.run_evaluation", return_value=summary),
        ):
            result = cli_runner.invoke(codex, ["evaluate", "--metrics-only"])
        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == summary["metrics"]


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
        """Test prepare-data delegates to the data loader and prints its result."""
        with patch(
            "codex_ml.data.loader.prepare_data_from_config", return_value={"train": 10}
        ) as prep:
            result = cli_runner.invoke(
                codex,
                ["prepare-data", "--config", str(sample_training_config)],
            )
        assert result.exit_code == 0, result.output
        prep.assert_called_once()
        assert json.loads(result.output) == {"train": 10}

    def test_prepare_data_with_seed(self, cli_runner, sample_training_config):
        """Test prepare-data forwards --seed as the shuffle seed."""
        with patch("codex_ml.data.loader.prepare_data_from_config", return_value={}) as prep:
            result = cli_runner.invoke(
                codex,
                ["prepare-data", "--config", str(sample_training_config), "--seed", "42"],
            )
        assert result.exit_code == 0, result.output
        assert prep.call_args.args[0].shuffle_seed == 42


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
        """Test config-sweep fails when the (default) base config does not exist."""
        with cli_runner.isolated_filesystem():
            result = cli_runner.invoke(codex, ["config-sweep"])
        assert result.exit_code != 0, "Result must not be empty"
        assert "base-config" in result.output

    def test_config_sweep_missing_param(self, cli_runner, sample_training_config):
        """Test config-sweep without sweep parameters."""
        cli_runner.invoke(
            codex,
            ["config-sweep", "--config", str(sample_training_config)],
        )
        # Should require sweep parameters

    def test_config_sweep_with_params(self, cli_runner, sample_training_config, tmp_path):
        """Test config-sweep writes a Hydra sweep file with the requested params."""
        import yaml

        output = tmp_path / "sweep.yaml"
        result = cli_runner.invoke(
            codex,
            [
                "config-sweep",
                "--base-config",
                str(sample_training_config),
                "--output",
                str(output),
                "--seeds",
                "1,2",
                "--param",
                "learning_rate=0.001,0.0001",
                "--param",
                "batch_size=32,64",
            ],
        )
        assert result.exit_code == 0, result.output
        payload = yaml.safe_load(output.read_text())
        params = payload["hydra"]["sweeper"]["params"]
        assert params == {
            "training.seed": "1,2",
            "learning_rate": "0.001,0.0001",
            "batch_size": "32,64",
        }
        assert payload["reproducibility"]["seeds"] == [1, 2]

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

    def test_missing_dependency_error(self, cli_runner, monkeypatch):
        """Test error handling for missing dependencies."""
        import sys

        import codex_ml.tokenization as tokenization_pkg
        from codex_ml.cli import codex_cli

        # ``from pkg import sub`` resolves an already-bound attribute first.
        monkeypatch.delattr(tokenization_pkg, "pipeline", raising=False)
        codex_cli._get_tokenizer_pipeline.cache_clear()
        try:
            with patch.dict(
                sys.modules, {"tokenizers": None, "codex_ml.tokenization.pipeline": None}
            ):
                sys.modules.pop("codex_ml.tokenization.pipeline")
                with pytest.raises(click.ClickException, match="optional 'tokenizers'"):
                    codex_cli._get_tokenizer_pipeline()
        finally:
            codex_cli._get_tokenizer_pipeline.cache_clear()

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
        with patch("codex_ml.training.run_functional_training", side_effect=KeyboardInterrupt):
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

    def test_json_output_format(self, cli_runner, tmp_path):
        """Evaluate output is parseable, key-sorted JSON."""
        summary = {"num_records": 2, "metrics": {"loss": 0.05, "accuracy": 0.95}}
        with (
            patch(
                "codex_ml.cli.codex_cli.load_app_config",
                return_value=(_fake_eval_cfg(tmp_path), None),
            ),
            patch("codex_ml.eval.runner.run_evaluation", return_value=summary),
        ):
            result = cli_runner.invoke(codex, ["evaluate"])
        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == summary
        assert result.output.index('"metrics"') < result.output.index('"num_records"')

    @pytest.mark.parametrize("flag", ["--verbose", "--quiet"])
    def test_unsupported_verbosity_flags(
        self, cli_runner, sample_training_config, mock_training, flag
    ):
        """train has no --verbose/--quiet flags; they are usage errors."""
        result = cli_runner.invoke(
            codex,
            ["train", "--config", str(sample_training_config), flag],
        )
        assert result.exit_code == 2
        assert "No such option" in result.output
        mock_training.assert_not_called()


# ============================================================================
# Integration Workflow Tests
# ============================================================================


class TestCodexCLIWorkflows:
    """Integration tests for complete workflows."""

    def test_data_prep_train_evaluate_workflow(self, cli_runner, tmp_path):
        """Test complete data→train→evaluate workflow."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("training:\n  max_epochs: 1")

        with patch("codex_ml.data.loader.prepare_data_from_config", return_value={}):
            with patch("codex_ml.training.run_functional_training"):
                if True:
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

    def test_tokenizer_train_encode_decode_workflow(
        self, cli_runner, tmp_path, fake_tokenizer_pipeline
    ):
        """Test tokenizer train→encode→decode workflow."""
        config_file = tmp_path / "tokenizer_config.yaml"
        config_file.write_text("vocab_size: 1000\ntype: bpe")

        trained = cli_runner.invoke(codex, ["tokenizer", "train", "--config", str(config_file)])
        assert trained.exit_code == 0, trained.output
        assert "tokenizer artifacts written to out/tokenizer" in trained.output

        encoded = cli_runner.invoke(
            codex, ["tokenizer", "encode", "hello", "--tokenizer-path", "tok.json"]
        )
        assert encoded.exit_code == 0, encoded.output
        assert encoded.output.strip() == "5 6 7"

        decoded = cli_runner.invoke(
            codex, ["tokenizer", "decode", "5", "6", "7", "--tokenizer-path", "tok.json"]
        )
        assert decoded.exit_code == 0, decoded.output
        assert decoded.output.strip() == "decoded text"
        fake_tokenizer_pipeline.run_decode.assert_called_once_with("tok.json", (5, 6, 7))


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

    def test_very_large_config_file(self, cli_runner, tmp_path, mock_training):
        """Test with large config file."""
        large_config = tmp_path / "large_config.yaml"
        large_config.write_text("\n".join([f"param_{i}: {i}" for i in range(10000)]))

        result = cli_runner.invoke(
            codex,
            ["train", "--config", str(large_config)],
        )
        assert result.exit_code == 0, result.output
        mock_training.assert_called_once()
        # Should handle large configs

    def test_special_characters_in_paths(self, cli_runner, tmp_path, mock_training):
        """Test with special characters in file paths."""
        special_dir = tmp_path / "dir with spaces & special-chars"
        special_dir.mkdir()
        config_file = special_dir / "config.yaml"
        config_file.write_text("test: config")

        result = cli_runner.invoke(
            codex,
            ["train", "--config", str(config_file)],
        )
        assert result.exit_code == 0, result.output
        mock_training.assert_called_once()
        # Should handle special characters in paths

    def test_unicode_in_config(self, cli_runner, tmp_path, mock_training):
        """Test with unicode characters in config."""
        unicode_config = tmp_path / "unicode_config.yaml"
        unicode_config.write_text("description: 'Testing with unicode 测试 🚀'\nmodel: test")

        result = cli_runner.invoke(
            codex,
            ["train", "--config", str(unicode_config)],
        )
        assert result.exit_code == 0, result.output
        mock_training.assert_called_once()
        # Should handle unicode in configs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
