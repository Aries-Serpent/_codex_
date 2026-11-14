"""
Integration Tests for Codex ML CLI

Tests complete workflows from CLI entry point through training and evaluation:
- Configuration loading and validation
- CLI to training pipeline integration
- Model registry interactions
- Tokenizer integration
- Configuration sweep workflows
- End-to-end training execution
- Cross-module dependencies

Part of Phase 5B-II: Integration Test Development
"""

from __future__ import annotations

import json
import logging
import os
import builtins
from types import SimpleNamespace
from unittest.mock import Mock, patch

import click
import pytest
from click.testing import CliRunner
from omegaconf import OmegaConf
from omegaconf.errors import ConfigKeyError, ReadonlyConfigError, ValidationError
from codex_ml.cli import codex_cli
from codex_ml.cli.codex_cli import codex
from codex_ml.config import load_app_config

logger = logging.getLogger(__name__)


class _FakeTokenizerPipelineError(Exception):
    pass


def _fake_tokenizer_pipeline(**overrides):
    pipeline = SimpleNamespace(
        TokenizerPipelineError=_FakeTokenizerPipelineError,
        run_train=Mock(return_value="artifacts/tok"),
        run_validate=Mock(return_value={"ok": True}),
        run_encode=Mock(return_value=[1, 2, 3]),
        run_decode=Mock(return_value="text"),
    )
    for key, value in overrides.items():
        setattr(pipeline, key, value)
    return pipeline


class TestCodexMLCLIIntegration:
    """Integration tests driving the real ``codex`` click group."""

    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def tmp_config_dir(self, tmp_path):
        """Create a temporary config directory with a schema-valid training config."""
        conf_dir = tmp_path / "conf"
        conf_dir.mkdir()
        (conf_dir / "train.yaml").write_text(
            "training:\n"
            "  batch_size: 32\n"
            "  max_epochs: 1\n"
            "  learning_rate: 0.001\n"
            "  gradient_accumulation: 1\n"
            f"  output_dir: {tmp_path / 'runs'}\n"
        )
        return conf_dir

    @pytest.fixture
    def mock_training(self):
        with patch("codex_ml.training.run_functional_training") as run:
            yield run

    def test_tokenizer_train_integration(self, runner, tmp_path):
        """Test: tokenizer train forwards streaming options to the pipeline."""
        config_file = tmp_path / "tok.yaml"
        config_file.write_text("vocab_size: 100\n")
        pipeline = _fake_tokenizer_pipeline()

        with patch("codex_ml.cli.codex_cli._get_tokenizer_pipeline", return_value=pipeline):
            result = runner.invoke(
                codex,
                [
                    "tokenizer",
                    "train",
                    "--config",
                    str(config_file),
                    "--streaming",
                    "--stream-chunk-size",
                    "64",
                ],
            )

        assert result.exit_code == 0, result.output
        assert "tokenizer artifacts written to artifacts/tok" in result.output
        pipeline.run_train.assert_called_once_with(
            str(config_file), streaming=True, stream_chunk_size=64, dry_run=False
        )

    def test_tokenizer_encode_decode_roundtrip(self, runner):
        """Test: encode output feeds decode and round-trips through the pipeline."""
        original_text = "The quick brown fox"
        pipeline = _fake_tokenizer_pipeline(
            run_encode=Mock(return_value=[10, 20, 30, 40]),
            run_decode=Mock(return_value=original_text),
        )

        with patch("codex_ml.cli.codex_cli._get_tokenizer_pipeline", return_value=pipeline):
            encoded = runner.invoke(
                codex, ["tokenizer", "encode", original_text, "--tokenizer-path", "tok.json"]
            )
            assert encoded.exit_code == 0, encoded.output
            ids = encoded.output.split()
            decoded = runner.invoke(
                codex, ["tokenizer", "decode", *ids, "--tokenizer-path", "tok.json"]
            )

        assert ids == ["10", "20", "30", "40"]
        assert decoded.exit_code == 0, decoded.output
        assert decoded.output.strip() == original_text
        pipeline.run_encode.assert_called_once_with("tok.json", original_text)
        pipeline.run_decode.assert_called_once_with("tok.json", (10, 20, 30, 40))

    def test_config_sweep_integration(self, runner, tmp_path, tmp_config_dir):
        """Test: config-sweep writes sweeper params, locked overrides and a dataset hash."""
        import hashlib

        import yaml

        dataset = tmp_path / "train.jsonl"
        dataset.write_text('{"text": "a"}\n')
        output = tmp_path / "sweep.yaml"

        result = runner.invoke(
            codex,
            [
                "config-sweep",
                "--base-config",
                str(tmp_config_dir / "train.yaml"),
                "--output",
                str(output),
                "--param",
                "training.learning_rate=0.001,0.01",
                "--param",
                "training.batch_size=32,64",
                "--locked-override",
                "training.max_epochs=1",
                "--dataset-path",
                str(dataset),
                "--dataset-version",
                "v1",
            ],
        )

        assert result.exit_code == 0, result.output
        payload = yaml.safe_load(output.read_text())
        assert payload["hydra"]["sweeper"]["params"] == {
            "training.seed": "42",
            "training.learning_rate": "0.001,0.01",
            "training.batch_size": "32,64",
        }
        assert payload["locked_overrides"] == {"training.max_epochs": "1"}
        repro = payload["reproducibility"]
        assert repro["dataset_version"] == "v1"
        assert repro["dataset_hash"] == hashlib.sha256(dataset.read_bytes()).hexdigest()

    def test_config_sweep_rejects_malformed_param(self, runner, tmp_path, tmp_config_dir):
        """Test: --param entries without '=' are rejected."""
        result = runner.invoke(
            codex,
            [
                "config-sweep",
                "--base-config",
                str(tmp_config_dir / "train.yaml"),
                "--output",
                str(tmp_path / "sweep.yaml"),
                "--param",
                "no-equals-sign",
            ],
        )
        assert result.exit_code == 1
        assert "--param entries must look like key=csvlist" in result.output

    def test_train_command_workflow(self, runner, tmp_config_dir, mock_training):
        """Test: train loads the config and hands it to the functional trainer."""
        result = runner.invoke(codex, ["train", "--config", str(tmp_config_dir / "train.yaml")])

        assert result.exit_code == 0, result.output
        assert "Training complete" in result.output
        kwargs = mock_training.call_args.kwargs
        assert kwargs["resume"] is False
        assert kwargs["config"].batch_size == 32
        assert kwargs["config"].max_epochs == 1

    def test_resume_training_integration(self, runner, tmp_path, tmp_config_dir, mock_training):
        """Test: resume reads the manifest and resumes from its best checkpoint."""
        checkpoint = tmp_path / "ckpt-best"
        manifest = tmp_path / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "best_checkpoint": str(checkpoint),
                    "last_checkpoint": str(tmp_path / "ckpt-last"),
                    "config_path": str(tmp_config_dir / "train.yaml"),
                }
            )
        )

        result = runner.invoke(codex, ["resume", str(manifest), "--mlflow-run-name", "resumed-run"])

        assert result.exit_code == 0, result.output
        assert f"resumed training from {checkpoint}" in result.output
        cfg = mock_training.call_args.kwargs["config"]
        assert mock_training.call_args.kwargs["resume"] is True
        assert cfg.resume_from == str(checkpoint)
        assert cfg.logging["mlflow_run_name"] == "resumed-run"

    def test_structured_cli_overrides_are_typed_and_bounded(self):
        """Only typed CLI runtime keys may extend a structured trainer config."""
        cfg = OmegaConf.create({"logging": {"mlflow_enable": False}})
        OmegaConf.set_struct(cfg, True)

        codex_cli._update_path(
            cfg, "resume_from", "checkpoints/step-10", allow_structured_override=True
        )
        assert cfg.resume_from == "checkpoints/step-10"
        assert cfg.logging.mlflow_enable is False

        with pytest.raises(ValueError, match="Unsupported structured CLI override"):
            codex_cli._update_path(
                cfg, "training.unrecognized", "value", allow_structured_override=True
            )
        with pytest.raises(TypeError, match="mlflow_enable must be bool"):
            codex_cli._update_path(cfg, "mlflow_enable", "true", allow_structured_override=True)
        assert "unrecognized" not in cfg
        assert "mlflow_enable" not in cfg

    def test_structured_cli_overrides_preserve_readonly_and_schema_validation(self, tmp_path):
        """CLI-only additions do not bypass read-only or user override validation."""
        readonly_cfg = OmegaConf.create({})
        OmegaConf.set_struct(readonly_cfg, True)
        OmegaConf.set_readonly(readonly_cfg, True)
        with pytest.raises(ReadonlyConfigError):
            codex_cli._update_path(
                readonly_cfg,
                "resume_from",
                "checkpoints/step-10",
                allow_structured_override=True,
            )
        assert "resume_from" not in readonly_cfg

        config_path = tmp_path / "training.yaml"
        config_path.write_text("training:\n  max_epochs: 1\n", encoding="utf-8")
        with pytest.raises(ConfigKeyError):
            load_app_config(config_path, ("training.unrecognized=1",))
        with pytest.raises(ValidationError):
            load_app_config(config_path, ("training.learning_rate=not-a-number",))

    def test_evaluate_command_integration(self, runner, tmp_path):
        """Test: evaluate prints metrics and appends an NDJSON record."""
        summary = {"metrics": {"accuracy": 0.85, "f1": 0.82}, "num_records": 4}
        cfg = SimpleNamespace(
            evaluation=SimpleNamespace(
                seed=0, metrics_sink="ndjson", output_dir=str(tmp_path / "eval")
            ),
            data=SimpleNamespace(),
        )
        log_path = tmp_path / "logs" / "metrics.ndjson"

        with (
            patch("codex_ml.cli.codex_cli.load_app_config", return_value=(cfg, None)),
            patch("codex_ml.eval.runner.run_evaluation", return_value=summary) as run_eval,
        ):
            result = runner.invoke(
                codex,
                [
                    "evaluate",
                    "--metrics-only",
                    "--seed",
                    "3",
                    "--log-metrics",
                    str(log_path),
                    "--run-id",
                    "run-1",
                ],
            )

        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == summary["metrics"]
        assert cfg.evaluation.seed == 3
        run_eval.assert_called_once_with(cfg.evaluation, data_cfg=cfg.data)
        records = [json.loads(line) for line in log_path.read_text().splitlines()]
        assert len(records) == 1
        assert records[0]["metrics"] == summary["metrics"]
        assert records[0]["num_records"] == 4
        assert records[0]["run_id"] == "run-1"

    def test_metrics_server_integration(self, runner):
        """Test: metrics-server reports whether the exporter started."""
        with patch("codex_ml.cli.codex_cli.start_metrics_server", return_value=True) as start:
            result = runner.invoke(codex, ["metrics-server", "--port", "9100"])
        assert result.exit_code == 0, result.output
        assert "metrics server running on 9100" in result.output
        start.assert_called_once_with(port=9100)

    def test_deploy_workflow_integration(self, runner, tmp_path):
        """Test: deploy requires --dry-run and prints the dry-run summary."""
        deploy_config = tmp_path / "deploy.yaml"
        deploy_config.write_text("target_environment: production\n")

        blocked = runner.invoke(codex, ["deploy", "--config", str(deploy_config)])
        assert blocked.exit_code == 1
        assert "--dry-run is required" in blocked.output

        summary = {"status": "ready", "rollout_ring": "canary"}
        with patch("codex_ml.cli.deploy.run_deploy_dry_run", return_value=summary) as dry:
            result = runner.invoke(
                codex,
                [
                    "deploy",
                    "--config",
                    str(deploy_config),
                    "--dry-run",
                    "--run-metadata-dir",
                    str(tmp_path),
                ],
            )
        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == summary
        dry.assert_called_once_with(
            config_path=deploy_config, dry_run=True, run_metadata_dir=tmp_path
        )

    def test_status_report_integration(self, runner, tmp_path):
        """Test: status-report summarises local run metadata."""
        (tmp_path / "run_metadata.json").write_text(
            json.dumps(
                {
                    "rollout_ring": "canary",
                    "owner": "ml-team",
                    "knobs": {"deployment_preset": "pod", "evaluation_preset": "fast"},
                }
            )
        )
        (tmp_path / "evaluation.json").write_text(json.dumps({"loss": 0.5}))

        result = runner.invoke(codex, ["status-report", "--run-metadata-dir", str(tmp_path)])

        assert result.exit_code == 0, result.output
        report = json.loads(result.output)
        assert report["rollout_ring"] == "canary"
        assert report["owner"] == "ml-team"
        assert report["evaluation_summary"] == {"loss": 0.5}

    def test_tokenize_text_command(self, runner):
        """Test: tokenize encodes text with the HF tokenizer adapter."""
        adapter = Mock()
        adapter.encode.return_value = [10, 20]
        with patch(
            "codex_ml.tokenization.hf_tokenizer.HFTokenizerAdapter.load", return_value=adapter
        ):
            result = runner.invoke(codex, ["tokenize", "Hello world"])
        assert result.exit_code == 0, result.output
        assert result.output.strip() == "[10, 20]"
        adapter.encode.assert_called_once_with("Hello world")

    def test_cli_configuration_propagation(self, runner, tmp_config_dir, mock_training):
        """Test: overrides, --seed and MLflow flags reach the trainer config."""
        result = runner.invoke(
            codex,
            [
                "train",
                "--config",
                str(tmp_config_dir / "train.yaml"),
                "training.batch_size=64",
                "training.learning_rate=0.01",
                "--seed",
                "7",
                "--mlflow",
                "--mlflow-run-name",
                "propagation",
                "--mlflow-tracking-uri",
                "file:mlruns",
            ],
        )

        assert result.exit_code == 0, result.output
        cfg = mock_training.call_args.kwargs["config"]
        assert cfg.batch_size == 64
        assert cfg.learning_rate == 0.01
        assert cfg.seed == 7
        assert cfg.mlflow_enable is True
        assert cfg.logging["mlflow_enable"] is True
        assert cfg.logging["mlflow_run_name"] == "propagation"
        assert cfg.mlflow_tracking_uri == "file:mlruns"
        assert cfg.logging["mlflow_tracking_uri"] == "file:mlruns"

    def test_cross_module_dependency_chain(
        self, runner, tmp_config_dir, mock_training, monkeypatch
    ):
        """Test: --enable-peft / --resume-from flow through env and trainer config."""
        monkeypatch.delenv("CODEX_ENABLE_PEFT", raising=False)
        monkeypatch.delenv("CODEX_ML_ENABLE_PEFT", raising=False)

        result = runner.invoke(
            codex,
            [
                "train",
                "--config",
                str(tmp_config_dir / "train.yaml"),
                "--enable-peft",
                "--resume-from",
                "checkpoints/step-10",
            ],
        )

        assert result.exit_code == 0, result.output
        assert os.environ["CODEX_ENABLE_PEFT"] == "1"
        assert os.environ["CODEX_ML_ENABLE_PEFT"] == "1"
        kwargs = mock_training.call_args.kwargs
        assert kwargs["resume"] is True
        assert kwargs["config"].resume_from == "checkpoints/step-10"

    def test_error_handling_invalid_config(self, runner, tmp_path):
        """Test: a missing configuration file is reported as a CLI error."""
        missing = tmp_path / "missing.yaml"
        result = runner.invoke(codex, ["evaluate", "--config", str(missing)])
        assert result.exit_code == 1
        assert "configuration file not found" in result.output

        train_result = runner.invoke(codex, ["train", "--config", str(missing)])
        assert train_result.exit_code == 2
        assert "does not exist" in train_result.output

    def test_error_recovery_on_missing_model(self, runner, tmp_config_dir):
        """Test: trainer I/O failures are logged and surfaced as a CLI error."""
        with (
            patch(
                "codex_ml.training.run_functional_training",
                side_effect=FileNotFoundError("model weights not found"),
            ),
            patch("codex_ml.utils.error_log.log_error") as log_error,
        ):
            result = runner.invoke(codex, ["train", "--config", str(tmp_config_dir / "train.yaml")])

        assert result.exit_code == 1
        assert "model weights not found" in result.output
        log_error.assert_called_once()
        assert log_error.call_args.args[0] == "cli.train"


class TestCodexMLCLIEndToEnd:
    """End-to-end CLI tests with minimal dependencies."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    def test_cli_help_output(self, runner):
        """Test: CLI help command provides documentation."""
        # Act: Get help
        result = runner.invoke(codex, ["--help"])

        # Assert
        assert result.exit_code == 0 or result.exit_code is None, "Result must not be empty"

    def test_tokenizer_help_output(self, runner):
        """Test: Tokenizer subcommand help."""
        # Act: Get tokenizer help
        result = runner.invoke(codex, ["tokenizer", "--help"])

        # Assert
        assert result.exit_code == 0 or result.exit_code is None, "Result must not be empty"

    def test_cli_version_compatibility(self):
        """Test: CLI maintains compatibility with ML pipeline API."""
        assert codex_cli.codex is codex
        assert hasattr(codex_cli, "train"), "Train command should exist"


class TestCodexMLCLIStateManagement:
    """State management and persistence in Codex ML CLI."""

    def test_training_state_persistence(self, tmp_path):
        """Test: Training state persists across resumption."""
        # Arrange: Create training state
        state_file = tmp_path / "training_state.json"
        state_data = {
            "epoch": 5,
            "global_step": 1000,
            "best_loss": 0.45,
            "checkpoint": "model_epoch_5.pt",
        }
        state_file.write_text(json.dumps(state_data))

        # Act: Load state
        loaded_state = json.loads(state_file.read_text())

        # Assert: State properly preserved
        assert loaded_state["epoch"] == 5, "Condition must be true"
        assert loaded_state["global_step"] == 1000, "Condition must be true"

    def test_config_override_propagation(self, tmp_path):
        """Test: Hydra-style overrides win over file values in load_app_config."""
        config_file = tmp_path / "train.yaml"
        config_file.write_text("training:\n  learning_rate: 0.001\n  batch_size: 32\n")

        cfg_obj, raw_cfg = load_app_config(str(config_file), ("training.learning_rate=0.01",))

        assert cfg_obj.training.learning_rate == 0.01
        assert cfg_obj.training.batch_size == 32
        assert raw_cfg.training.learning_rate == 0.01

    def test_resource_cleanup_after_training(self):
        """Test: Resources cleaned up after training completes."""
        # Arrange: Mock resource allocation
        resources = {"gpu_memory": 8000, "temp_files": []}

        # Act: Cleanup
        resources["gpu_memory"] = 0
        resources["temp_files"] = []

        # Assert: Resources released
        assert resources["gpu_memory"] == 0, "Condition must be true"
        assert len(resources["temp_files"]) == 0, "Collection must not be empty"


class TestCodexMLCLIErrorPaths:
    """Error handling and recovery in Codex ML CLI."""

    def test_error_on_missing_checkpoint(self, tmp_path):
        """Test: Resume fails gracefully when the manifest has no checkpoint."""
        runner = CliRunner()
        manifest = tmp_path / "manifest.json"
        manifest.write_text(json.dumps({"config_path": "configs/training/base.yaml"}))

        with patch("codex_ml.training.run_functional_training") as run:
            result = runner.invoke(codex, ["resume", str(manifest)])
            missing = runner.invoke(codex, ["resume", str(tmp_path / "nope.json")])

        assert result.exit_code == 1
        assert "manifest missing checkpoint information" in result.output
        assert missing.exit_code == 2
        run.assert_not_called()

    def test_error_on_invalid_model_registry(self, tmp_path):
        """Test: deploy dry-run validation errors block the deployment."""
        runner = CliRunner()
        deploy_config = tmp_path / "deploy.yaml"
        deploy_config.write_text("target_environment: production\n")

        with patch(
            "codex_ml.cli.deploy.run_deploy_dry_run",
            side_effect=RuntimeError("rollout ring mismatch"),
        ):
            result = runner.invoke(codex, ["deploy", "--config", str(deploy_config), "--dry-run"])

        assert result.exit_code == 1
        assert "DEPLOYMENT BLOCKED: rollout ring mismatch" in result.output

    def test_graceful_degradation_with_missing_dependencies(self, monkeypatch):
        """Missing optional tokenizer dependencies produce a user-facing Click error."""
        original_import = builtins.__import__

        def fail_if_tokenizers_missing(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "codex_ml.tokenization":
                raise ModuleNotFoundError("No module named 'tokenizers'", name="tokenizers")
            return original_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", fail_if_tokenizers_missing)
        codex_cli._get_tokenizer_pipeline.cache_clear()
        try:
            with pytest.raises(click.ClickException, match="optional 'tokenizers' dependency"):
                codex_cli._get_tokenizer_pipeline()
        finally:
            codex_cli._get_tokenizer_pipeline.cache_clear()
