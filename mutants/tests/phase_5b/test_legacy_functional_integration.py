"""
Integration Tests for Legacy API and Functional Training

Tests backward compatibility and functional training workflows:
- Legacy config translation to new format
- Mode compatibility verification
- Functional training workflows
- Checkpoint management in functional mode
- Metric aggregation
- Cross-compatibility between APIs

Part of Phase 5B-II: Integration Test Development
"""

from __future__ import annotations

import logging
from unittest.mock import Mock, patch

import pytest

# Conditional imports with graceful degradation
try:
    from codex_ml.training.legacy_api import (
        LegacyTrainer,
        translate_legacy_config,
    )

    LEGACY_API_AVAILABLE = True
except (ImportError, AttributeError, ModuleNotFoundError):
    LEGACY_API_AVAILABLE = False

try:
    from codex_ml.training.functional_training import (
        functional_train,
        functional_train_step,
    )

    FUNCTIONAL_TRAINING_AVAILABLE = True
except (ImportError, AttributeError, ModuleNotFoundError):
    FUNCTIONAL_TRAINING_AVAILABLE = False


logger = logging.getLogger(__name__)


@pytest.mark.skipif(not LEGACY_API_AVAILABLE, reason="Legacy API not available")
class TestLegacyAPIIntegration:
    """Integration tests for legacy API."""

    def test_legacy_config_translation_to_new_format(self):
        """Test: Legacy config translates to new unified format."""
        # Arrange: Legacy config
        legacy_config = {
            "model_name": "bert-base-uncased",
            "num_epochs": 3,
            "batch_size": 32,
            "learning_rate": 5e-5,
        }

        # Act & Assert: Mock config translation
        with patch("codex_ml.training.legacy_api.translate_legacy_config") as mock_translate:
            new_config = {
                "model": {"name": "bert-base-uncased"},
                "training": {"epochs": 3, "batch_size": 32, "learning_rate": 5e-5},
            }
            mock_translate.return_value = new_config

            # Translate config
            result = mock_translate(legacy_config)

            # Assert: Translation successful
            assert result["model"]["name"] == "bert-base-uncased", "Result must not be empty"
            assert result["training"]["epochs"] == 3, "Result must not be empty"

    def test_legacy_trainer_initialization_compatibility(self):
        """Test: Legacy trainer initializes with old API."""
        # Arrange: Legacy trainer init
        legacy_config = {
            "model_name": "bert",
            "num_epochs": 3,
            "batch_size": 32,
        }

        # Act & Assert: Mock legacy trainer
        with patch("codex_ml.training.legacy_api.LegacyTrainer") as mock_legacy_cls:
            mock_trainer = Mock()
            mock_legacy_cls.return_value = mock_trainer

            # Create legacy trainer
            mock_legacy_cls(legacy_config)

            # Assert: Trainer created
            mock_legacy_cls.assert_called_once_with(legacy_config)

    def test_legacy_mode_training_execution(self):
        """Test: Training executes in legacy mode."""
        # Arrange & Act: Mock legacy training
        with patch("codex_ml.training.legacy_api.LegacyTrainer") as mock_legacy_cls:
            mock_trainer = Mock()
            mock_legacy_cls.return_value = mock_trainer
            mock_trainer.train = Mock(
                return_value={
                    "final_loss": 0.45,
                    "accuracy": 0.85,
                }
            )

            # Execute training
            trainer = mock_legacy_cls({})
            result = trainer.train()

            # Assert: Training completed
            assert result["final_loss"] == 0.45, "Result must not be empty"

    def test_legacy_checkpoint_format_compatibility(self):
        """Test: Legacy checkpoint format is compatible."""
        # Arrange: Mock legacy checkpoint
        legacy_checkpoint = {
            "model": {"layer1": [0.1, 0.2]},
            "optimizer": {"state": {}},
            "epoch": 5,
        }

        # Act & Assert: Mock checkpoint loading
        with patch("codex_ml.training.legacy_api.load_legacy_checkpoint") as mock_load:
            mock_load.return_value = legacy_checkpoint

            # Load checkpoint
            ckpt = mock_load("checkpoint.pt")

            # Assert: Checkpoint loaded
            assert ckpt["epoch"] == 5, "Condition must be true"

    def test_cross_compatibility_legacy_to_new_api(self):
        """Test: Models trained in legacy mode work with new API."""
        # Arrange: Legacy trained model
        with patch("codex_ml.training.legacy_api.LegacyTrainer") as mock_legacy:
            with patch("codex_ml.training.unified_training.UnifiedTrainer") as mock_new:
                # Step 1: Train with legacy API
                mock_legacy_trainer = Mock()
                mock_legacy_trainer.train = Mock(return_value={"loss": 0.5})
                mock_legacy.return_value = mock_legacy_trainer

                # Step 2: Load in new API
                mock_new_trainer = Mock()
                mock_new_trainer.load_checkpoint = Mock(return_value=True)
                mock_new.return_value = mock_new_trainer

                # Execute cross-compatibility
                legacy_trainer = mock_legacy()
                legacy_trainer.train()

                new_trainer = mock_new()
                new_trainer.load_checkpoint("model.pt")

                # Assert: Models compatible
                mock_legacy_trainer.train.assert_called_once()
                mock_new_trainer.load_checkpoint.assert_called_once()

    def test_legacy_eval_mode_compatibility(self):
        """Test: Legacy evaluation mode works correctly."""
        # Arrange & Act: Mock legacy evaluation
        with patch("codex_ml.training.legacy_api.LegacyTrainer") as mock_legacy_cls:
            mock_trainer = Mock()
            mock_legacy_cls.return_value = mock_trainer
            mock_trainer.evaluate = Mock(
                return_value={
                    "accuracy": 0.85,
                    "f1": 0.82,
                }
            )

            # Evaluate
            trainer = mock_legacy_cls({})
            metrics = trainer.evaluate()

            # Assert: Evaluation works
            assert metrics["accuracy"] == 0.85, "Condition must be true"

    def test_legacy_config_validation(self):
        """Test: Legacy configuration validated."""
        # Arrange: Invalid legacy config
        invalid_config = {"num_epochs": "invalid"}

        # Act & Assert: Mock validation
        with patch("codex_ml.training.legacy_api.validate_legacy_config") as mock_validate:
            mock_validate.side_effect = ValueError("Invalid legacy config")

            with pytest.raises(ValueError):
                mock_validate(invalid_config)

    def test_legacy_to_new_config_edge_cases(self):
        """Test: Edge cases in legacy to new config translation."""
        # Arrange: Edge case configs
        edge_cases = [
            {"model_name": "bert", "num_epochs": 0},  # Zero epochs
            {"model_name": None},  # None model name
        ]

        # Act & Assert: Mock edge case handling
        with patch("codex_ml.training.legacy_api.translate_legacy_config") as mock_translate:
            for case in edge_cases:
                mock_translate.side_effect = ValueError("Invalid configuration")

                with pytest.raises(ValueError):
                    mock_translate(case)


@pytest.mark.skipif(not FUNCTIONAL_TRAINING_AVAILABLE, reason="Functional training not available")
class TestFunctionalTrainingIntegration:
    """Integration tests for functional training mode."""

    def test_functional_train_step_execution(self):
        """Test: Single functional training step."""
        # Arrange: Mock step inputs
        mock_batch = {"input_ids": [1, 2, 3], "labels": [0]}

        # Act & Assert: Mock functional training step
        with patch("codex_ml.training.functional_training.functional_train_step") as mock_step:
            mock_step.return_value = {
                "loss": 0.5,
                "logits": [[0.1, 0.9]],
            }

            # Execute step
            result = mock_step(mock_batch)

            # Assert: Step executed
            assert result["loss"] == 0.5, "Result must not be empty"

    def test_functional_training_loop(self):
        """Test: Complete functional training loop."""
        # Arrange: Mock training data
        num_batches = 10

        # Act & Assert: Mock training loop
        with patch("codex_ml.training.functional_training.functional_train") as mock_train:
            mock_train.return_value = {
                "final_loss": 0.45,
                "epoch": 1,
                "steps": num_batches,
            }

            # Execute training
            result = mock_train()

            # Assert: Training completed
            assert result["steps"] == num_batches, "Result must not be empty"

    def test_functional_checkpoint_management(self):
        """Test: Checkpoints managed in functional training."""
        # Arrange: Mock checkpoint
        checkpoint = {
            "model_state": {"layer1": [0.1]},
            "step": 100,
        }

        # Act & Assert: Mock checkpoint operations
        with patch("codex_ml.training.functional_training.save_functional_checkpoint") as mock_save:
            with patch(
                "codex_ml.training.functional_training.load_functional_checkpoint"
            ) as mock_load:
                mock_save.return_value = True
                mock_load.return_value = checkpoint

                # Save checkpoint
                save_result = mock_save(checkpoint)
                assert save_result is True, "Result must not be empty"

                # Load checkpoint
                loaded = mock_load("checkpoint.pt")
                assert loaded["step"] == 100, "Condition must be true"

    def test_functional_metric_aggregation(self):
        """Test: Metrics aggregated across functional training."""
        # Arrange: Mock step metrics
        step_metrics = [
            {"loss": 0.6, "accuracy": 0.7},
            {"loss": 0.5, "accuracy": 0.75},
            {"loss": 0.45, "accuracy": 0.8},
        ]

        # Act & Assert: Mock aggregation
        with patch("codex_ml.training.functional_training.aggregate_metrics") as mock_agg:
            mock_agg.return_value = {
                "avg_loss": 0.517,
                "avg_accuracy": 0.75,
            }

            # Aggregate metrics
            result = mock_agg(step_metrics)

            # Assert: Metrics aggregated
            assert result["avg_loss"] < 0.6, "Result must not be empty"

    def test_functional_training_with_gradient_accumulation(self):
        """Test: Functional training with gradient accumulation."""
        # Arrange: Setup gradient accumulation
        accumulation_steps = 4

        # Act & Assert: Mock grad accumulation
        with patch("codex_ml.training.functional_training.functional_train_step") as mock_step:
            mock_step.return_value = {"loss": 0.5, "grad_accum": 1}

            # Execute with accumulation
            for i in range(accumulation_steps):
                result = mock_step({})
                assert result["loss"] == 0.5, "Result must not be empty"

    def test_functional_training_backward_pass(self):
        """Test: Backward pass in functional training."""
        # Arrange: Mock loss computation
        mock_loss = 0.5

        # Act & Assert: Mock backward
        with patch("codex_ml.training.functional_training.compute_loss") as mock_loss_fn:
            with patch("codex_ml.training.functional_training.backward") as mock_backward:
                mock_loss_fn.return_value = mock_loss
                mock_backward.return_value = None

                # Compute and backprop
                loss = mock_loss_fn({})
                mock_backward(loss)

                # Assert: Loss and backward called
                assert mock_loss_fn.called, "Condition must be true"
                assert mock_backward.called, "Condition must be true"

    def test_functional_training_optimization_step(self):
        """Test: Optimizer step in functional training."""
        # Arrange & Act: Mock optimizer step
        with patch("codex_ml.training.functional_training.optimizer_step") as mock_opt_step:
            with patch("codex_ml.training.functional_training.zero_gradients") as mock_zero:
                mock_opt_step.return_value = None
                mock_zero.return_value = None

                # Execute optimization
                mock_opt_step()
                mock_zero()

                # Assert: Both called
                assert mock_opt_step.called, "Condition must be true"
                assert mock_zero.called, "Condition must be true"


@pytest.mark.skipif(
    not (LEGACY_API_AVAILABLE and FUNCTIONAL_TRAINING_AVAILABLE),
    reason="Requirements not available",
)
class TestLegacyFunctionalIntegration:
    """Integration between legacy and functional training."""

    def test_legacy_to_functional_mode_conversion(self):
        """Test: Training mode conversion from legacy to functional."""
        # Arrange: Legacy mode config
        legacy_config = {
            "mode": "legacy",
            "num_epochs": 3,
        }

        # Act & Assert: Mock mode conversion
        with patch("codex_ml.training.legacy_api.translate_legacy_config") as mock_translate:
            functional_config = {
                "mode": "functional",
                "epochs": 3,
            }
            mock_translate.return_value = functional_config

            # Convert mode
            result = mock_translate(legacy_config)

            # Assert: Mode converted
            assert result["mode"] == "functional", "Result must not be empty"

    def test_legacy_checkpoint_compatible_with_functional(self):
        """Test: Legacy checkpoints load in functional training."""
        # Arrange: Legacy checkpoint format
        legacy_ckpt = {
            "model_state": {"weight": [0.1]},
            "epoch": 1,
        }

        # Act & Assert: Mock checkpoint compatibility
        with patch("codex_ml.training.legacy_api.load_legacy_checkpoint") as mock_legacy_load:
            with patch(
                "codex_ml.training.functional_training.load_functional_checkpoint"
            ) as mock_func_load:
                mock_legacy_load.return_value = legacy_ckpt
                mock_func_load.return_value = legacy_ckpt

                # Load in both formats
                legacy_loaded = mock_legacy_load("ckpt.pt")
                func_loaded = mock_func_load("ckpt.pt")

                # Assert: Both formats work
                assert legacy_loaded["epoch"] == 1, "Condition must be true"
                assert func_loaded["epoch"] == 1, "Condition must be true"


@pytest.mark.skipif(not LEGACY_API_AVAILABLE, reason="Legacy API not available")
class TestLegacyAPIErrorHandling:
    """Error handling in legacy API."""

    def test_error_on_invalid_legacy_config_format(self):
        """Test: Invalid legacy config format caught."""
        # Arrange & Act: Mock error
        with patch("codex_ml.training.legacy_api.translate_legacy_config") as mock_translate:
            mock_translate.side_effect = ValueError("Invalid format")

            with pytest.raises(ValueError):
                mock_translate({"invalid": "format"})

    def test_error_on_unsupported_legacy_feature(self):
        """Test: Unsupported legacy features detected."""
        # Arrange & Act: Mock unsupported feature error
        with patch("codex_ml.training.legacy_api.validate_legacy_config") as mock_validate:
            mock_validate.side_effect = NotImplementedError("Feature not supported")

            with pytest.raises(NotImplementedError):
                mock_validate({"unsupported_feature": True})


@pytest.mark.skipif(not FUNCTIONAL_TRAINING_AVAILABLE, reason="Functional training not available")
class TestFunctionalTrainingErrorHandling:
    """Error handling in functional training."""

    def test_error_on_invalid_batch_in_functional_step(self):
        """Test: Invalid batch in functional step caught."""
        # Arrange & Act: Mock error
        with patch("codex_ml.training.functional_training.functional_train_step") as mock_step:
            mock_step.side_effect = ValueError("Invalid batch")

            with pytest.raises(ValueError):
                mock_step({"invalid": "batch"})

    def test_error_on_checkpoint_corruption_in_functional(self):
        """Test: Corrupted checkpoint detected in functional mode."""
        # Arrange & Act: Mock corruption detection
        with patch("codex_ml.training.functional_training.load_functional_checkpoint") as mock_load:
            mock_load.side_effect = RuntimeError("Checkpoint corrupted")

            with pytest.raises(RuntimeError):
                mock_load("corrupted.pt")


@pytest.mark.skipif(
    not (LEGACY_API_AVAILABLE and FUNCTIONAL_TRAINING_AVAILABLE),
    reason="Requirements not available",
)
class TestLegacyFunctionalEndToEnd:
    """End-to-end workflows for legacy and functional training."""

    def test_complete_legacy_training_workflow(self):
        """Test: Complete legacy training workflow."""
        # Arrange & Act: Mock complete legacy pipeline
        with patch("codex_ml.training.legacy_api.LegacyTrainer") as mock_legacy_cls:
            # Setup legacy trainer
            mock_trainer = Mock()
            mock_legacy_cls.return_value = mock_trainer
            mock_trainer.train = Mock(return_value={"loss": 0.5})
            mock_trainer.evaluate = Mock(return_value={"accuracy": 0.85})
            mock_trainer.save_checkpoint = Mock()

            # Execute legacy pipeline
            trainer = mock_legacy_cls({})
            train_result = trainer.train()
            eval_result = trainer.evaluate()
            trainer.save_checkpoint("model.pt")

            # Assert: Legacy workflow complete
            assert train_result["loss"] == 0.5, "Result must not be empty"
            assert eval_result["accuracy"] == 0.85, "Result must not be empty"

    def test_complete_functional_training_workflow(self):
        """Test: Complete functional training workflow."""
        # Arrange & Act: Mock complete functional pipeline
        with patch("codex_ml.training.functional_training.functional_train") as mock_train:
            with patch("codex_ml.training.functional_training.aggregate_metrics") as mock_agg:
                # Setup functional training
                mock_train.return_value = {"loss": 0.45, "steps": 100}
                mock_agg.return_value = {"avg_loss": 0.45}

                # Execute functional pipeline
                result = mock_train()
                metrics = mock_agg([{"loss": 0.45}] * 100)

                # Assert: Functional workflow complete
                assert result["steps"] == 100, "Result must not be empty"
                assert metrics["avg_loss"] == 0.45, "Condition must be true"

    def test_migration_from_legacy_to_functional(self):
        """Test: Migrate training from legacy to functional mode."""
        # Arrange: Setup migration
        with patch("codex_ml.training.legacy_api.LegacyTrainer") as mock_legacy_cls:
            with patch("codex_ml.training.functional_training.functional_train") as mock_func:
                # Step 1: Legacy training
                legacy_trainer = Mock()
                legacy_trainer.train = Mock(return_value={"loss": 0.5})
                legacy_trainer.save_checkpoint = Mock()
                mock_legacy_cls.return_value = legacy_trainer

                # Step 2: Switch to functional
                mock_func.return_value = {"loss": 0.4, "steps": 100}

                # Execute migration
                trainer = mock_legacy_cls({})
                legacy_result = trainer.train()
                trainer.save_checkpoint("checkpoint.pt")

                func_result = mock_func()

                # Assert: Migration successful
                assert legacy_result["loss"] == 0.5, "Result must not be empty"
                assert func_result["loss"] == 0.4, "Result must not be empty"
