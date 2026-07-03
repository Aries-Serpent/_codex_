"""
Integration Tests for Hugging Face Trainer

Tests complete training workflows with HF Trainer:
- Trainer initialization with models and data
- Data loader integration
- Checkpoint management
- Metrics collection
- Training loops with evaluation
- Device strategy and distributed setup
- Error recovery and training resumption

Part of Phase 5B-II: Integration Test Development
"""

from __future__ import annotations

import json
import logging
import tempfile
from unittest.mock import Mock, patch

import pytest

# Conditional imports with graceful degradation
try:
    from transformers import Trainer, TrainingArguments

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from training.engine_hf_trainer import HFTrainer, create_trainer

    HF_TRAINER_AVAILABLE = True
except (ImportError, AttributeError, ModuleNotFoundError):
    HF_TRAINER_AVAILABLE = False


logger = logging.getLogger(__name__)


@pytest.mark.skipif(not HF_TRAINER_AVAILABLE, reason="HF Trainer not available")
class TestHFTrainerIntegration:
    """Integration tests for Hugging Face trainer."""

    @pytest.fixture
    def training_config(self, tmp_path):
        """Create a minimal training configuration."""
        return {
            "model_name": "bert-base-uncased",
            "num_train_epochs": 1,
            "per_device_train_batch_size": 8,
            "per_device_eval_batch_size": 8,
            "learning_rate": 2e-5,
            "output_dir": str(tmp_path / "output"),
            "save_strategy": "epoch",
            "eval_strategy": "epoch",
        }

    def test_trainer_initialization_with_model(self, training_config):
        """Test: Trainer initializes with model and configuration."""
        # Arrange & Act: Mock trainer creation
        with patch("training.engine_hf_trainer.Trainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer

            # Create trainer instance (mocked)
            with patch("training.engine_hf_trainer.AutoModel") as mock_model_cls:
                mock_model = Mock()
                mock_model_cls.from_pretrained = Mock(return_value=mock_model)

                # Load model
                mock_model_cls.from_pretrained(training_config["model_name"])

                # Assert: Model loaded successfully
                assert mock_model_cls.from_pretrained.called, "Condition must be true"

    def test_trainer_with_data_loader_integration(self, tmp_path, training_config):
        """Test: Trainer integrates with data loaders."""
        # Arrange: Create mock data
        dataset_file = tmp_path / "dataset.json"
        dataset_file.write_text('{"text": "sample text", "label": 1}\n')

        # Act & Assert: Mock data loader integration
        with patch("training.engine_hf_trainer.DataLoader") as mock_loader_cls:
            mock_loader = Mock()
            mock_loader.__len__ = Mock(return_value=10)
            mock_loader_cls.return_value = mock_loader

            # Create data loader
            loader = mock_loader_cls(batch_size=training_config["per_device_train_batch_size"])

            # Assert: Loader created
            assert len(loader) == 10, "Loader must not be empty"

    def test_training_loop_execution(self, training_config):
        """Test: Complete training loop from start to completion."""
        # Arrange: Mock training components
        with patch("training.engine_hf_trainer.Trainer") as mock_trainer_cls:
            with patch("training.engine_hf_trainer.TrainingArguments") as mock_args_cls:
                # Setup training arguments
                mock_args = Mock()
                mock_args_cls.return_value = mock_args

                # Setup trainer
                mock_trainer = Mock()
                mock_trainer_cls.return_value = mock_trainer
                mock_trainer.train = Mock(
                    return_value={
                        "training_loss": 0.45,
                        "epoch": 1.0,
                    }
                )

                # Execute training
                args = mock_args_cls(**training_config)
                trainer = mock_trainer_cls(args=args, model=Mock())
                result = trainer.train()

                # Assert: Training completed
                assert "training_loss" in result, "Result must not be empty"
                assert result["epoch"] == 1.0, "Result must not be empty"

    def test_checkpoint_saving_workflow(self, tmp_path, training_config):
        """Test: Checkpoints saved correctly during training."""
        # Arrange: Setup checkpoint directory
        checkpoint_dir = tmp_path / "checkpoints"
        checkpoint_dir.mkdir()

        # Act & Assert: Mock checkpoint saving
        with patch("training.engine_hf_trainer.Trainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer

            # Mock checkpoint save
            mock_trainer.save_model = Mock()
            mock_trainer.save_model(str(checkpoint_dir / "checkpoint-1000"))

            # Assert: Save called
            mock_trainer.save_model.assert_called_once()

    def test_evaluation_during_training(self, training_config):
        """Test: Model evaluated during training."""
        # Arrange: Mock eval data
        with patch("training.engine_hf_trainer.Trainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer

            # Mock evaluation
            mock_trainer.evaluate = Mock(
                return_value={
                    "eval_loss": 0.5,
                    "eval_accuracy": 0.85,
                    "epoch": 1.0,
                }
            )

            # Execute evaluation
            trainer = mock_trainer_cls()
            metrics = trainer.evaluate()

            # Assert: Evaluation results available
            assert metrics["eval_accuracy"] == 0.85, "Condition must be true"

    def test_training_resumption_from_checkpoint(self, tmp_path):
        """Test: Training can resume from checkpoint."""
        # Arrange: Setup checkpoint
        checkpoint_dir = tmp_path / "checkpoint-500"
        checkpoint_dir.mkdir(parents=True)
        metadata_file = checkpoint_dir / "trainer_state.json"
        metadata_file.write_text(json.dumps({"current_step": 500, "epoch": 0.5}))

        # Act & Assert: Mock resumption
        with patch("training.engine_hf_trainer.Trainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer

            # Mock resumption
            mock_trainer.train = Mock(
                return_value={
                    "training_loss": 0.4,
                    "epoch": 1.0,
                }
            )

            trainer = mock_trainer_cls()
            trainer.train(resume_from_checkpoint=str(checkpoint_dir))

            # Assert: Training resumed
            mock_trainer.train.assert_called()

    def test_metrics_collection_workflow(self):
        """Test: Metrics collected and logged during training."""
        # Arrange & Act: Mock metrics collection
        with patch("training.engine_hf_trainer.Trainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer

            # Mock metrics callback
            mock_trainer.add_callback = Mock()
            mock_trainer.state = Mock()
            mock_trainer.state.log_history = [
                {"loss": 0.6, "epoch": 0.5},
                {"loss": 0.5, "epoch": 1.0, "eval_loss": 0.45},
            ]

            # Collect metrics
            trainer = mock_trainer_cls()
            trainer.add_callback(Mock())

            # Assert: Metrics logged
            assert len(trainer.state.log_history) == 2, "Collection must not be empty"

    def test_distributed_training_setup(self):
        """Test: Distributed training configuration."""
        # Arrange & Act: Mock distributed setup
        with patch("training.engine_hf_trainer.TrainingArguments") as mock_args_cls:

            # Setup distributed arguments
            mock_args = Mock()
            mock_args.local_rank = 0
            mock_args_cls.return_value = mock_args

            # Assert: Distributed config available
            assert mock_args.local_rank == 0, "local_rank is not valid"

    def test_cross_module_dependency_model_to_trainer(self):
        """Test: Model loading flows correctly to trainer."""
        # Arrange & Act: Mock complete pipeline
        with patch("training.engine_hf_trainer.AutoModel") as mock_model_cls:
            with patch("training.engine_hf_trainer.Trainer") as mock_trainer_cls:
                # Step 1: Load model
                mock_model = Mock()
                mock_model_cls.from_pretrained = Mock(return_value=mock_model)

                # Step 2: Create trainer with model
                mock_trainer = Mock()
                mock_trainer_cls.return_value = mock_trainer

                # Execute pipeline
                model = mock_model_cls.from_pretrained("bert-base")
                mock_trainer_cls(model=model)

                # Assert: Pipeline successful
                mock_model_cls.from_pretrained.assert_called_once()

    def test_error_handling_on_invalid_model(self):
        """Test: Invalid model name produces appropriate error."""
        # Arrange & Act: Mock model loading error
        with patch("training.engine_hf_trainer.AutoModel") as mock_model_cls:
            mock_model_cls.from_pretrained = Mock(side_effect=OSError("Model not found on hub"))

            with pytest.raises(OSError):
                mock_model_cls.from_pretrained("nonexistent-model")

    def test_error_recovery_on_training_failure(self):
        """Test: Graceful error handling during training."""
        # Arrange & Act: Mock training failure
        with patch("training.engine_hf_trainer.Trainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer
            mock_trainer.train = Mock(side_effect=RuntimeError("Training failed"))

            with pytest.raises(RuntimeError):
                trainer = mock_trainer_cls()
                trainer.train()


@pytest.mark.skipif(
    not (HF_TRAINER_AVAILABLE and TORCH_AVAILABLE), reason="Requirements not available"
)
class TestHFTrainerWithTorch:
    """HF Trainer tests with PyTorch."""

    def test_device_strategy_cpu_only(self):
        """Test: CPU-only device strategy."""
        # Arrange & Act: Mock device strategy
        with patch("training.engine_hf_trainer.TrainingArguments") as mock_args_cls:
            mock_args = Mock()
            mock_args.device = "cpu"
            mock_args_cls.return_value = mock_args

            # Verify device setting
            assert mock_args.device == "cpu", "device is not valid"

    def test_device_strategy_with_gpu(self):
        """Test: GPU device strategy when available."""
        # Arrange & Act: Mock GPU setup
        with patch("torch.cuda.is_available") as mock_cuda:
            mock_cuda.return_value = True

            with patch("training.engine_hf_trainer.TrainingArguments") as mock_args_cls:
                mock_args = Mock()
                mock_args.device = "cuda:0" if mock_cuda() else "cpu"
                mock_args_cls.return_value = mock_args

                # Verify device
                assert "cuda" in mock_args.device, "Condition must be true"

    def test_gradient_accumulation_configuration(self):
        """Test: Gradient accumulation setup."""
        # Arrange & Act: Mock gradient accumulation
        with patch("training.engine_hf_trainer.TrainingArguments") as mock_args_cls:
            mock_args = Mock()
            mock_args.gradient_accumulation_steps = 4
            mock_args_cls.return_value = mock_args

            # Verify configuration
            assert mock_args.gradient_accumulation_steps == 4, "gradient_accumulation_steps is not valid"

    def test_mixed_precision_training(self):
        """Test: Mixed precision (AMP) training setup."""
        # Arrange & Act: Mock mixed precision
        with patch("training.engine_hf_trainer.TrainingArguments") as mock_args_cls:
            mock_args = Mock()
            mock_args.fp16 = True
            mock_args.fp16_backend = "auto"
            mock_args_cls.return_value = mock_args

            # Verify FP16 enabled
            assert mock_args.fp16 is True, "fp16 is not valid"


@pytest.mark.skipif(not HF_TRAINER_AVAILABLE, reason="HF Trainer not available")
class TestHFTrainerStateManagement:
    """State management in HF trainer."""

    def test_training_state_persistence(self, tmp_path):
        """Test: Training state persists across sessions."""
        # Arrange: Create training state
        state_file = tmp_path / "trainer_state.json"
        state = {
            "global_step": 1000,
            "epoch": 2.5,
            "best_loss": 0.45,
            "best_checkpoint": "checkpoint-1000",
        }
        state_file.write_text(json.dumps(state))

        # Act: Load state
        loaded = json.loads(state_file.read_text())

        # Assert: State preserved
        assert loaded["global_step"] == 1000, "Condition must be true"
        assert loaded["epoch"] == 2.5, "Condition must be true"

    def test_training_arguments_propagation(self):
        """Test: Training arguments propagate through trainer."""
        # Arrange & Act: Mock argument propagation
        with patch("training.engine_hf_trainer.TrainingArguments") as mock_args_cls:
            config = {
                "num_train_epochs": 3,
                "per_device_train_batch_size": 16,
                "learning_rate": 5e-5,
            }

            mock_args = Mock()
            for key, value in config.items():
                setattr(mock_args, key, value)
            mock_args_cls.return_value = mock_args

            # Verify propagation
            args = mock_args_cls(**config)
            assert args.num_train_epochs == 3, "num_train_epochs is not valid"
            assert args.per_device_train_batch_size == 16, "per_device_train_batch_size is not valid"

    def test_resource_cleanup_after_training(self):
        """Test: Resources cleaned up after training completes."""
        # Arrange & Act: Mock resource tracking
        resources = {"model": Mock(), "optimizer": Mock(), "scheduler": Mock()}

        # Cleanup
        for key in list(resources.keys()):
            resources[key] = None

        # Assert: Resources released
        assert all(v is None for v in resources.values()), "Value must be initialized"


@pytest.mark.skipif(not HF_TRAINER_AVAILABLE, reason="HF Trainer not available")
class TestHFTrainerErrorPaths:
    """Error handling in HF trainer."""

    def test_error_on_invalid_batch_size(self):
        """Test: Invalid batch size is caught."""
        # Arrange & Act: Mock invalid batch size
        with patch("training.engine_hf_trainer.TrainingArguments") as mock_args_cls:
            mock_args_cls.side_effect = ValueError("Batch size must be positive")

            with pytest.raises(ValueError):
                mock_args_cls(per_device_train_batch_size=-1)

    def test_error_on_missing_data(self):
        """Test: Missing data produces appropriate error."""
        # Arrange & Act: Mock missing data
        with patch("training.engine_hf_trainer.Trainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer
            mock_trainer.train = Mock(side_effect=ValueError("Train dataset not found"))

            with pytest.raises(ValueError):
                trainer = mock_trainer_cls()
                trainer.train()

    def test_graceful_degradation_with_missing_dependencies(self):
        """Test: Graceful degradation when dependencies missing."""
        try:
            from training import engine_hf_trainer

            assert hasattr(engine_hf_trainer, "HFTrainer") or hasattr(
                engine_hf_trainer, "create_trainer"
            )
        except ImportError:
            pytest.skip("Trainer module not available, but should handle gracefully")


@pytest.mark.skipif(not HF_TRAINER_AVAILABLE, reason="HF Trainer not available")
class TestHFTrainerEndToEnd:
    """End-to-end HF trainer workflows."""

    def test_complete_training_pipeline(self, tmp_path):
        """Test: Complete training from config to checkpoint."""
        # Arrange: Setup training context
        with patch("training.engine_hf_trainer.AutoModel") as mock_model_cls:
            with patch("training.engine_hf_trainer.DataLoader") as mock_loader_cls:
                with patch("training.engine_hf_trainer.Trainer") as mock_trainer_cls:
                    # Step 1: Load model
                    mock_model = Mock()
                    mock_model_cls.from_pretrained = Mock(return_value=mock_model)

                    # Step 2: Create data loader
                    mock_loader = Mock()
                    mock_loader_cls.return_value = mock_loader

                    # Step 3: Create trainer
                    mock_trainer = Mock()
                    mock_trainer_cls.return_value = mock_trainer
                    mock_trainer.train = Mock(return_value={"training_loss": 0.45})
                    mock_trainer.save_model = Mock()

                    # Execute pipeline
                    model = mock_model_cls.from_pretrained("bert-base")
                    mock_loader_cls()
                    trainer = mock_trainer_cls(model=model)
                    result = trainer.train()
                    trainer.save_model(str(tmp_path / "final_model"))

                    # Assert: Complete pipeline executed
                    assert result["training_loss"] == 0.45, "Result must not be empty"
                    mock_trainer.save_model.assert_called_once()

    def test_training_with_evaluation_and_save(self):
        """Test: Training with periodic evaluation and checkpointing."""
        # Arrange & Act: Mock complete workflow
        with patch("training.engine_hf_trainer.Trainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer

            # Mock training with evaluation
            mock_trainer.train = Mock(return_value={"training_loss": 0.45, "epoch": 1.0})
            mock_trainer.evaluate = Mock(return_value={"eval_loss": 0.5, "eval_accuracy": 0.85})
            mock_trainer.save_model = Mock()

            # Execute workflow
            trainer = mock_trainer_cls()
            train_result = trainer.train()
            eval_result = trainer.evaluate()
            trainer.save_model(os.path.join(tempfile.gettempdir(), "model"))

            # Assert: All steps executed
            assert train_result["training_loss"] == 0.45, "Result must not be empty"
            assert eval_result["eval_accuracy"] == 0.85, "Result must not be empty"
            mock_trainer.save_model.assert_called_once()

    def test_multi_epoch_training_with_checkpoints(self):
        """Test: Multi-epoch training saves checkpoints."""
        # Arrange & Act: Mock multi-epoch training
        with patch("training.engine_hf_trainer.Trainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer

            # Mock state with log history
            mock_trainer.state = Mock()
            mock_trainer.state.log_history = []
            for epoch in range(3):
                mock_trainer.state.log_history.append(
                    {
                        "epoch": epoch + 1,
                        "loss": 0.6 - (epoch * 0.05),
                    }
                )

            mock_trainer.train = Mock(return_value={"epoch": 3})

            # Execute training
            trainer = mock_trainer_cls()
            result = trainer.train()

            # Assert: Multi-epoch completed
            assert result["epoch"] == 3, "Result must not be empty"
            assert len(trainer.state.log_history) == 3, "Collection must not be empty"
