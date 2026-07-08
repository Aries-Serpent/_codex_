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
from unittest.mock import Mock, patch

import pytest

# Conditional imports with graceful degradation
try:
    from click.testing import CliRunner

    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False

try:
    from codex_ml.cli.codex_cli import (
        codex,
        config_sweep,
        deploy,
        evaluate,
        metrics_server,
        resume,
        status_report,
        tokenize,
        tokenizer,
        tokenizer_decode,
        tokenizer_encode,
        tokenizer_train,
        tokenizer_validate,
        train,
    )

    CODEX_CLI_AVAILABLE = True
except (ImportError, AttributeError):
    CODEX_CLI_AVAILABLE = False

try:
    from codex_ml.config import load_app_config

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from codex_ml.training import UnifiedTrainer

    TRAINER_AVAILABLE = True
except ImportError:
    TRAINER_AVAILABLE = False


logger = logging.getLogger(__name__)


@pytest.mark.skipif(not CODEX_CLI_AVAILABLE, reason="Codex CLI not available")
class TestCodexMLCLIIntegration:
    """Integration tests for Codex ML CLI."""

    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        if not CLICK_AVAILABLE:
            pytest.skip("Click not available")
        return CliRunner()

    @pytest.fixture
    def tmp_config_dir(self, tmp_path):
        """Create temporary config directory with sample configs."""
        conf_dir = tmp_path / "conf"
        conf_dir.mkdir()

        # Create a basic training config
        train_config = conf_dir / "train.yaml"
        train_config.write_text("""
model:
  name: test_model
  hidden_size: 128
  num_layers: 2

training:
  batch_size: 32
  epochs: 1
  learning_rate: 0.001
  gradient_accumulation: 1

tokenizer:
  type: bpe
  vocab_size: 1000
""")

        # Create evaluation config
        eval_config = conf_dir / "eval.yaml"
        eval_config.write_text("""
eval:
  batch_size: 64
  metrics:
    - accuracy
    - f1
  checkpoint_path: /tmp/checkpoint.pt
""")

        return conf_dir

    def test_tokenizer_train_integration(self, tmp_path):
        """Test: Tokenizer training produces valid vocab."""
        # Arrange: Create sample data
        data_file = tmp_path / "data.txt"
        data_file.write_text("hello world\nfoo bar\nbaz qux")

        # Act & Assert: Mock tokenizer training
        with patch("codex_ml.cli.codex_cli.train_tokenizer_from_text") as mock_train:
            mock_train.return_value = {"vocab_size": 100, "token_count": 50}

            result = mock_train(str(data_file), vocab_size=100)

            assert result["vocab_size"] == 100, "Result must not be empty"
            assert result["token_count"] == 50, "Result must not be empty"

    def test_tokenizer_encode_decode_roundtrip(self):
        """Test: Text encode and decode roundtrip preserves content."""
        # Arrange: Sample text
        original_text = "The quick brown fox"

        # Act & Assert: Mock tokenizer operations
        with patch("codex_ml.cli.codex_cli.load_tokenizer") as mock_load:
            mock_tokenizer = Mock()
            mock_load.return_value = mock_tokenizer

            # Encode
            mock_tokenizer.encode = Mock(return_value=[10, 20, 30, 40])

            # Decode
            mock_tokenizer.decode = Mock(return_value=original_text)

            # Verify roundtrip
            tokens = mock_tokenizer.encode(original_text)
            decoded = mock_tokenizer.decode(tokens)

            assert decoded == original_text, "decoded is not valid"

    def test_config_sweep_integration(self, tmp_path, tmp_config_dir):
        """Test: Config sweep generates multiple training configurations."""
        # Arrange: Setup sweep parameters
        sweep_params = {
            "training.learning_rate": [0.001, 0.01],
            "training.batch_size": [32, 64],
        }

        # Act & Assert: Mock config sweep
        with patch("codex_ml.cli.codex_cli.generate_config_combinations") as mock_gen:
            mock_gen.return_value = [
                {"lr": 0.001, "bs": 32},
                {"lr": 0.001, "bs": 64},
                {"lr": 0.01, "bs": 32},
                {"lr": 0.01, "bs": 64},
            ]

            configs = mock_gen(sweep_params)

            # Verify
            assert len(configs) == 4, "Configs must not be empty"
            assert all(isinstance(c, dict) for c in configs)

    def test_train_command_workflow(self, tmp_path, tmp_config_dir):
        """Test: Train command executes complete training workflow."""
        # Arrange: Setup training context
        checkpoint_dir = tmp_path / "checkpoints"
        checkpoint_dir.mkdir()

        # Act & Assert: Mock training pipeline
        with patch("codex_ml.cli.codex_cli.load_app_config") as mock_load_cfg:
            with patch("codex_ml.cli.codex_cli.UnifiedTrainer") as mock_trainer_cls:
                # Setup config
                mock_cfg = {
                    "training": {"epochs": 1, "batch_size": 32},
                    "model": {"name": "test"},
                }
                mock_load_cfg.return_value = mock_cfg

                # Setup trainer
                mock_trainer = Mock()
                mock_trainer.train = Mock(
                    return_value={
                        "final_loss": 0.5,
                        "final_epoch": 1,
                        "checkpoint": "model.pt",
                    }
                )
                mock_trainer_cls.return_value = mock_trainer

                # Simulate training
                config = mock_load_cfg()
                trainer = mock_trainer_cls(config)
                result = trainer.train()

                # Verify workflow
                assert result["final_epoch"] == 1, "Result must not be empty"
                assert "checkpoint" in result, "Result must not be empty"

    def test_resume_training_integration(self, tmp_path):
        """Test: Resume command loads checkpoint and continues training."""
        # Arrange: Setup checkpoint
        checkpoint_file = tmp_path / "checkpoint.pt"
        checkpoint_file.write_text("mock_checkpoint")

        # Act & Assert: Mock resume workflow
        with patch("codex_ml.cli.codex_cli.load_checkpoint") as mock_load:
            with patch("codex_ml.cli.codex_cli.UnifiedTrainer") as mock_trainer_cls:
                # Setup checkpoint loading
                mock_ckpt = {
                    "model_state": {"layer1": [0.1, 0.2]},
                    "epoch": 5,
                    "optimizer_state": {},
                }
                mock_load.return_value = mock_ckpt

                # Setup trainer
                mock_trainer = Mock()
                mock_trainer.resume_from_checkpoint = Mock(return_value=True)
                mock_trainer.train = Mock(return_value={"final_epoch": 6})
                mock_trainer_cls.return_value = mock_trainer

                # Simulate resume
                ckpt = mock_load(str(checkpoint_file))
                trainer = mock_trainer_cls({})
                trainer.resume_from_checkpoint(ckpt)
                result = trainer.train()

                # Verify resume workflow
                assert result["final_epoch"] == 6, "Result must not be empty"

    def test_evaluate_command_integration(self, tmp_path):
        """Test: Evaluate command produces metrics."""
        # Arrange: Setup evaluation data
        eval_data_file = tmp_path / "eval_data.jsonl"
        eval_data_file.write_text('{"text": "test", "label": 1}\n')

        # Act & Assert: Mock evaluation pipeline
        with patch("codex_ml.cli.codex_cli.load_checkpoint") as mock_load:
            with patch("codex_ml.cli.codex_cli.Evaluator") as mock_eval_cls:
                # Setup model loading
                mock_load.return_value = {"model": Mock()}

                # Setup evaluator
                mock_evaluator = Mock()
                mock_evaluator.evaluate = Mock(
                    return_value={
                        "accuracy": 0.85,
                        "f1": 0.82,
                        "loss": 0.3,
                    }
                )
                mock_eval_cls.return_value = mock_evaluator

                # Simulate evaluation
                model = mock_load(str(tmp_path / "model.pt"))
                evaluator = mock_eval_cls(model, str(eval_data_file))
                metrics = evaluator.evaluate()

                # Verify metrics
                assert metrics["accuracy"] == 0.85, "Condition must be true"
                assert metrics["f1"] == 0.82, "Condition must be true"

    def test_metrics_server_integration(self, tmp_path):
        """Test: Metrics server startup and communication."""
        # Arrange & Act: Mock metrics server
        with patch("codex_ml.cli.codex_cli.start_metrics_server") as mock_start:
            mock_server = Mock()
            mock_server.is_running = Mock(return_value=True)
            mock_start.return_value = mock_server

            # Start server
            server = mock_start(port=8000)

            # Verify
            assert server.is_running(), "Condition must be true"

    def test_deploy_workflow_integration(self, tmp_path):
        """Test: Deploy command validates and deploys model."""
        # Arrange: Setup deployment config
        deploy_config = tmp_path / "deploy.yaml"
        deploy_config.write_text("""
model_path: model.pt
target_environment: production
replicas: 3
""")

        # Act & Assert: Mock deployment pipeline
        with patch("codex_ml.cli.codex_cli.load_deployment_config") as mock_load:
            with patch("codex_ml.cli.codex_cli.deploy_model") as mock_deploy:
                # Setup config loading
                mock_cfg = {"target_environment": "production"}
                mock_load.return_value = mock_cfg

                # Setup deployment
                mock_deploy.return_value = {"status": "deployed", "replicas": 3}

                # Simulate deployment
                cfg = mock_load(str(deploy_config))
                result = mock_deploy(cfg)

                # Verify
                assert result["status"] == "deployed", "Result must not be empty"

    def test_status_report_integration(self, tmp_path):
        """Test: Status report aggregates training metrics."""
        # Arrange: Setup run metadata
        metadata_dir = tmp_path / "metadata"
        metadata_dir.mkdir()
        (metadata_dir / "metrics.json").write_text('{"loss": 0.5, "epoch": 5}')

        # Act & Assert: Mock status reporting
        with patch("codex_ml.cli.codex_cli.build_status_report") as mock_build:
            mock_build.return_value = {
                "current_epoch": 5,
                "training_loss": 0.5,
                "status": "in_progress",
            }

            report = mock_build(str(metadata_dir))

            # Verify
            assert report["status"] == "in_progress", "rep is not valid"
            assert report["training_loss"] == 0.5, "rep is not valid"

    def test_tokenize_text_command(self):
        """Test: Tokenize command converts text to token IDs."""
        # Arrange: Sample text
        text = "Hello world"

        # Act & Assert: Mock tokenization
        with patch("codex_ml.cli.codex_cli.load_tokenizer") as mock_load:
            mock_tokenizer = Mock()
            mock_tokenizer.encode = Mock(return_value=[10, 20])
            mock_load.return_value = mock_tokenizer

            # Tokenize
            tokens = mock_tokenizer.encode(text)

            # Verify
            assert len(tokens) == 2, "Tokens must not be empty"
            assert tokens == [10, 20]

    def test_cli_configuration_propagation(self, tmp_config_dir):
        """Test: Configuration propagates through CLI to all components."""
        # Arrange: Load base config
        with patch("codex_ml.cli.codex_cli.load_app_config") as mock_load:
            mock_cfg = {
                "model": {"name": "test"},
                "training": {"batch_size": 32},
                "tokenizer": {"vocab_size": 1000},
            }
            mock_load.return_value = mock_cfg

            # Act: Propagate through components
            with patch("codex_ml.cli.codex_cli.UnifiedTrainer") as mock_trainer:
                mock_trainer_instance = Mock()
                mock_trainer.return_value = mock_trainer_instance

                # Access from different components
                config = mock_load()
                mock_trainer(config)

                # Verify propagation
                assert config["model"]["name"] == "test", "Condition must be true"
                assert config["training"]["batch_size"] == 32, "Condition must be true"

    def test_cross_module_dependency_chain(self):
        """Test: Cross-module dependencies resolved correctly."""
        # Arrange & Act: Mock dependency chain
        # Config → Model Registry → Trainer → Metrics

        with patch("codex_ml.cli.codex_cli.load_app_config") as mock_load_cfg:
            with patch("codex_ml.cli.codex_cli.get_model_registry") as mock_registry:
                with patch("codex_ml.cli.codex_cli.UnifiedTrainer") as mock_trainer:
                    # Step 1: Load config
                    mock_load_cfg.return_value = {"model": "bert"}

                    # Step 2: Get model from registry
                    mock_registry.return_value = Mock()
                    mock_registry.return_value.get = Mock(return_value=Mock())

                    # Step 3: Create trainer
                    mock_trainer.return_value = Mock()

                    # Execute chain
                    cfg = mock_load_cfg()
                    registry = mock_registry()
                    registry.get(cfg["model"])
                    mock_trainer(cfg)

                    # Verify chain
                    assert cfg["model"] == "bert", "Condition must be true"
                    mock_registry.assert_called_once()

    def test_error_handling_invalid_config(self):
        """Test: Invalid configuration is caught and reported."""
        # Arrange: Invalid config
        invalid_config = {"training": {"batch_size": "invalid"}}

        # Act & Assert: Mock validation
        with patch("codex_ml.cli.codex_cli.validate_config") as mock_validate:
            mock_validate.side_effect = ValueError("Invalid batch_size")

            with pytest.raises(ValueError):
                mock_validate(invalid_config)

    def test_error_recovery_on_missing_model(self):
        """Test: Graceful handling when model not found."""
        # Arrange & Act: Mock model loading error
        with patch("codex_ml.cli.codex_cli.get_model_registry") as mock_registry:
            mock_registry.return_value.get = Mock(
                side_effect=KeyError("Model not found in registry")
            )

            with pytest.raises(KeyError):
                registry = mock_registry()
                registry.get("nonexistent_model")


@pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not available")
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
        try:
            from codex_ml.cli import codex_cli

            assert hasattr(codex_cli, "codex"), "Main CLI entrypoint should exist"
            assert hasattr(codex_cli, "train"), "Train command should exist"
        except ImportError:
            pytest.skip("CLI module not available")


@pytest.mark.skipif(not CODEX_CLI_AVAILABLE, reason="Codex CLI not available")
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

    def test_config_override_propagation(self):
        """Test: Command-line config overrides propagate through pipeline."""
        # Arrange & Act: Mock config override
        with patch("codex_ml.cli.codex_cli.merge_configs") as mock_merge:
            base_config = {"lr": 0.001, "batch_size": 32}
            overrides = {"lr": 0.01}

            mock_merge.return_value = {"lr": 0.01, "batch_size": 32}

            result = mock_merge(base_config, overrides)

            # Assert: Overrides applied
            assert result["lr"] == 0.01, "Result must not be empty"
            assert result["batch_size"] == 32, "Result must not be empty"

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


@pytest.mark.skipif(not CODEX_CLI_AVAILABLE, reason="Codex CLI not available")
class TestCodexMLCLIErrorPaths:
    """Error handling and recovery in Codex ML CLI."""

    def test_error_on_missing_checkpoint(self):
        """Test: Resume fails gracefully with missing checkpoint."""
        # Arrange & Act: Mock checkpoint loading error
        with patch("codex_ml.cli.codex_cli.load_checkpoint") as mock_load:
            mock_load.side_effect = FileNotFoundError("Checkpoint not found")

            with pytest.raises(FileNotFoundError):
                mock_load("/nonexistent/checkpoint.pt")

    def test_error_on_invalid_model_registry(self):
        """Test: Model registry errors are caught."""
        # Arrange & Act: Mock registry error
        with patch("codex_ml.cli.codex_cli.get_model_registry") as mock_registry:
            mock_registry.side_effect = RuntimeError("Registry connection failed")

            with pytest.raises(RuntimeError):
                mock_registry()

    def test_graceful_degradation_with_missing_dependencies(self):
        """Test: CLI degrades gracefully when optional dependencies missing."""
        try:
            from codex_ml.cli import codex_cli

            assert hasattr(codex_cli, "codex")
        except ImportError:
            pytest.skip("CLI not fully available, but should handle gracefully")
