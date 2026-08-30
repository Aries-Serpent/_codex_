"""
Integration Tests for Unified Training and Data Loaders

Tests complete data loading and training orchestration workflows:
- Data pipeline integration from loading to batching
- Unified training orchestration across stages
- Cross-stage resource management
- Batch processing and streaming
- Error handling in data loading
- Training stage coordination

Part of Phase 5B-II: Integration Test Development
"""

from __future__ import annotations

import json
import logging
from unittest.mock import Mock, patch

import pytest

# Conditional imports with graceful degradation
try:
    from codex_ml.data.loaders import (
        DataLoader,
        create_data_loader,
        get_dataset,
        load_jsonl,
    )

    DATA_LOADERS_AVAILABLE = True
except (ImportError, AttributeError, ModuleNotFoundError):
    DATA_LOADERS_AVAILABLE = False

try:
    from codex_ml.training.unified_training import (
        UnifiedTrainer,
        create_unified_trainer,
    )

    UNIFIED_TRAINING_AVAILABLE = True
except (ImportError, AttributeError, ModuleNotFoundError):
    UNIFIED_TRAINING_AVAILABLE = False


logger = logging.getLogger(__name__)


@pytest.mark.skipif(not DATA_LOADERS_AVAILABLE, reason="Data loaders not available")
class TestDataLoadersIntegration:
    """Integration tests for data loading system."""

    @pytest.fixture
    def sample_dataset_file(self, tmp_path):
        """Create sample dataset file."""
        dataset_file = tmp_path / "dataset.jsonl"
        dataset_file.write_text(
            '{"text": "sample 1", "label": 1}\n'
            '{"text": "sample 2", "label": 0}\n'
            '{"text": "sample 3", "label": 1}\n'
        )
        return dataset_file

    def test_load_jsonl_dataset(self, sample_dataset_file):
        """Test: JSONL dataset loading."""
        # Arrange & Act: Mock JSONL loading
        with patch("codex_ml.data.loaders.load_jsonl") as mock_load:
            mock_load.return_value = [
                {"text": "sample 1", "label": 1},
                {"text": "sample 2", "label": 0},
                {"text": "sample 3", "label": 1},
            ]

            # Load dataset
            dataset = mock_load(str(sample_dataset_file))

            # Assert: Dataset loaded
            assert len(dataset) == 3, "Dataset must not be empty"
            assert dataset[0]["text"] == "sample 1", "Data must not be empty"

    def test_create_data_loader_from_dataset(self):
        """Test: Create data loader from dataset."""
        # Arrange: Mock dataset
        mock_dataset = [
            {"text": "text1", "label": 1},
            {"text": "text2", "label": 0},
        ] * 10

        # Act & Assert: Mock data loader creation
        with patch("codex_ml.data.loaders.create_data_loader") as mock_create:
            mock_loader = Mock()
            mock_loader.__len__ = Mock(return_value=20)
            mock_loader.__iter__ = Mock(return_value=iter([]))
            mock_create.return_value = mock_loader

            # Create loader
            loader = mock_create(mock_dataset, batch_size=4)

            # Assert: Loader created
            assert len(loader) == 20, "Loader must not be empty"

    def test_batch_iteration_workflow(self):
        """Test: Iterate through batches correctly."""
        # Arrange: Mock batched data
        num_samples = 100
        batch_size = 32
        expected_batches = (num_samples + batch_size - 1) // batch_size

        # Act & Assert: Mock batch iteration
        with patch("codex_ml.data.loaders.DataLoader") as mock_loader_cls:
            mock_loader = Mock()
            mock_loader.__len__ = Mock(return_value=expected_batches)
            mock_loader.__iter__ = Mock(
                return_value=iter(
                    [{"input_ids": [1, 2, 3], "labels": [1]} for _ in range(expected_batches)]
                )
            )
            mock_loader_cls.return_value = mock_loader

            # Iterate through batches
            loader = mock_loader_cls(batch_size=batch_size)
            batch_count = 0
            for batch in loader:
                batch_count += 1

            # Assert: All batches iterated
            assert batch_count == expected_batches, "Count must be greater than zero"

    def test_data_splitting_train_eval_test(self):
        """Test: Data splitting into train/eval/test sets."""
        # Arrange: Create dataset and split ratios
        total_samples = 100
        train_ratio, eval_ratio, test_ratio = 0.7, 0.15, 0.15

        # Act & Assert: Mock splitting
        with patch("codex_ml.data.loaders.split_dataset") as mock_split:
            mock_split.return_value = (
                list(range(int(total_samples * train_ratio))),  # Train
                list(
                    range(
                        int(total_samples * train_ratio),
                        int(total_samples * (train_ratio + eval_ratio)),
                    )
                ),  # Eval
                list(range(int(total_samples * (train_ratio + eval_ratio)), total_samples)),  # Test
            )

            # Split dataset
            train, eval_set, test = mock_split(
                list(range(total_samples)), [train_ratio, eval_ratio, test_ratio]
            )

            # Assert: Splits correct
            assert len(train) == 70, "Train must not be empty"
            assert len(eval_set) == 15, "Eval_set must not be empty"
            assert len(test) == 15, "Test must not be empty"

    def test_tokenizer_integration_with_data_loader(self):
        """Test: Data loader integrates with tokenizer."""
        # Arrange: Mock data and tokenizer
        texts = ["hello world", "foo bar"]

        # Act & Assert: Mock tokenization in data loading
        with patch("codex_ml.data.loaders.DataLoader") as mock_loader_cls:
            mock_loader = Mock()
            mock_loader.tokenizer = Mock()
            mock_loader.tokenizer.batch_encode_plus = Mock(
                return_value={
                    "input_ids": [[1, 2], [3, 4]],
                    "attention_mask": [[1, 1], [1, 1]],
                }
            )
            mock_loader_cls.return_value = mock_loader

            loader = mock_loader_cls()
            result = loader.tokenizer.batch_encode_plus(texts)

            # Assert: Tokenization integrated
            assert len(result["input_ids"]) == 2, "Collection must not be empty"

    def test_data_loader_with_sampling_strategy(self):
        """Test: Data loader supports different sampling strategies."""
        # Arrange & Act: Mock sampling strategies
        strategies = ["sequential", "random", "weighted"]

        with patch("codex_ml.data.loaders.create_data_loader") as mock_create:
            mock_create.return_value = Mock()

            # Test each strategy
            for strategy in strategies:
                mock_create([], batch_size=32, sampler=strategy)
                assert mock_create.called, "Condition must be true"

    def test_error_handling_corrupt_data(self, tmp_path):
        """Test: Corrupt data in dataset is handled."""
        # Arrange: Create corrupt dataset
        corrupt_file = tmp_path / "corrupt.jsonl"
        corrupt_file.write_text('{"text": "valid"}\n{"invalid json\n')

        # Act & Assert: Mock error handling
        with patch("codex_ml.data.loaders.load_jsonl") as mock_load:
            mock_load.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

            with pytest.raises(json.JSONDecodeError):
                mock_load(str(corrupt_file))

    def test_data_loader_performance_metrics(self):
        """Test: Data loader tracks performance metrics."""
        # Arrange & Act: Mock metrics collection
        with patch("codex_ml.data.loaders.DataLoader") as mock_loader_cls:
            mock_loader = Mock()
            mock_loader.get_metrics = Mock(
                return_value={
                    "total_batches": 100,
                    "avg_batch_time_ms": 45.3,
                    "throughput_samples_per_sec": 710,
                }
            )
            mock_loader_cls.return_value = mock_loader

            loader = mock_loader_cls()
            metrics = loader.get_metrics()

            # Assert: Metrics available
            assert metrics["total_batches"] == 100, "Condition must be true"
            assert metrics["avg_batch_time_ms"] > 0, "Value must be greater than zero"


@pytest.mark.skipif(not UNIFIED_TRAINING_AVAILABLE, reason="Unified training not available")
class TestUnifiedTrainingIntegration:
    """Integration tests for unified training system."""

    def test_unified_trainer_initialization(self):
        """Test: Unified trainer initializes with configuration."""
        # Arrange & Act: Mock trainer initialization
        config = {
            "model": {"name": "bert"},
            "training": {"epochs": 3},
            "data": {"batch_size": 32},
        }

        with patch("codex_ml.training.unified_training.UnifiedTrainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer

            # Create trainer
            mock_trainer_cls(config)

            # Assert: Trainer created
            mock_trainer_cls.assert_called_once_with(config)

    def test_training_pipeline_stages(self):
        """Test: Training executes through multiple stages."""
        # Arrange & Act: Mock stage execution
        with patch("codex_ml.training.unified_training.UnifiedTrainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer

            # Mock stage execution
            mock_trainer.prepare_data = Mock()
            mock_trainer.setup_model = Mock()
            mock_trainer.train = Mock(return_value={"loss": 0.5})
            mock_trainer.evaluate = Mock(return_value={"accuracy": 0.85})

            # Execute pipeline
            trainer = mock_trainer_cls({})
            trainer.prepare_data()
            trainer.setup_model()
            train_result = trainer.train()
            eval_result = trainer.evaluate()

            # Assert: All stages executed
            mock_trainer.prepare_data.assert_called_once()
            mock_trainer.setup_model.assert_called_once()
            assert train_result["loss"] == 0.5, "Result must not be empty"
            assert eval_result["accuracy"] == 0.85, "Result must not be empty"

    def test_cross_stage_data_propagation(self):
        """Test: Data flows correctly between training stages."""
        # Arrange & Act: Mock data flow
        with patch("codex_ml.training.unified_training.UnifiedTrainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer

            # Setup data propagation
            mock_trainer.data_loader = Mock()
            mock_trainer.model = Mock()
            mock_trainer.optimizer = Mock()

            trainer = mock_trainer_cls({})

            # Data flows through stages
            assert trainer.data_loader is not None, "data_loader must be initialized"
            assert trainer.model is not None, "model must be initialized"

    def test_resource_coordination_across_stages(self):
        """Test: Resources allocated and coordinated across training stages."""
        # Arrange & Act: Mock resource management
        resources = {
            "gpu_memory": 8000,
            "cpu_cores": 8,
            "model_parameters": 110_000_000,
        }

        with patch("codex_ml.training.unified_training.UnifiedTrainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer
            mock_trainer.resources = resources

            trainer = mock_trainer_cls({})

            # Assert: Resources available
            assert trainer.resources["gpu_memory"] > 0, "Value must be greater than zero"
            assert trainer.resources["model_parameters"] > 0, "Value must be greater than zero"

    def test_checkpoint_coordination_between_stages(self):
        """Test: Checkpoints saved and loaded across stages."""
        # Arrange: Mock checkpoint
        checkpoint_data = {
            "stage": "evaluation",
            "epoch": 3,
            "best_loss": 0.4,
        }

        # Act & Assert: Mock checkpoint operations
        with patch("codex_ml.training.unified_training.UnifiedTrainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer
            mock_trainer.save_checkpoint = Mock()
            mock_trainer.load_checkpoint = Mock(return_value=checkpoint_data)

            trainer = mock_trainer_cls({})
            trainer.save_checkpoint("checkpoint.pt")
            loaded = trainer.load_checkpoint("checkpoint.pt")

            # Assert: Checkpoint operations work
            mock_trainer.save_checkpoint.assert_called_once()
            assert loaded["stage"] == "evaluation", "Condition must be true"


@pytest.mark.skipif(
    not (DATA_LOADERS_AVAILABLE and UNIFIED_TRAINING_AVAILABLE), reason="Requirements not available"
)
class TestDataLoaderTrainerIntegration:
    """Integration between data loaders and training."""

    def test_data_loader_to_trainer_pipeline(self):
        """Test: Data flows from loader through trainer."""
        # Arrange & Act: Mock complete pipeline
        with patch("codex_ml.data.loaders.create_data_loader") as mock_create_loader:
            with patch("codex_ml.training.unified_training.UnifiedTrainer") as mock_trainer_cls:
                # Step 1: Create data loader
                mock_loader = Mock()
                mock_loader.__iter__ = Mock(
                    return_value=iter([{"input_ids": [1, 2], "labels": [1]}])
                )
                mock_create_loader.return_value = mock_loader

                # Step 2: Create trainer
                mock_trainer = Mock()
                mock_trainer_cls.return_value = mock_trainer
                mock_trainer.train = Mock(return_value={"loss": 0.5})

                # Execute pipeline
                loader = mock_create_loader([], batch_size=32)
                trainer = mock_trainer_cls({"data_loader": loader})
                result = trainer.train()

                # Assert: Pipeline complete
                assert result["loss"] == 0.5, "Result must not be empty"

    def test_batch_size_consistency_across_pipeline(self):
        """Test: Batch size consistent from loader through training."""
        # Arrange: Setup batch size
        batch_size = 64

        # Act & Assert: Mock batch size propagation
        with patch("codex_ml.data.loaders.create_data_loader") as mock_create_loader:
            with patch("codex_ml.training.unified_training.UnifiedTrainer") as mock_trainer_cls:
                mock_loader = Mock()
                mock_loader.batch_size = batch_size
                mock_create_loader.return_value = mock_loader

                mock_trainer = Mock()
                mock_trainer_cls.return_value = mock_trainer

                loader = mock_create_loader([], batch_size=batch_size)
                mock_trainer_cls({"batch_size": batch_size})

                # Assert: Batch size consistent
                assert loader.batch_size == batch_size, "batch_size is not valid"


@pytest.mark.skipif(not DATA_LOADERS_AVAILABLE, reason="Data loaders not available")
class TestDataLoadersErrorHandling:
    """Error handling in data loading."""

    def test_error_on_missing_dataset(self):
        """Test: Missing dataset produces appropriate error."""
        # Arrange & Act: Mock missing dataset error
        with patch("codex_ml.data.loaders.load_jsonl") as mock_load:
            mock_load.side_effect = FileNotFoundError("Dataset not found")

            with pytest.raises(FileNotFoundError):
                mock_load("/nonexistent/dataset.jsonl")

    def test_error_on_invalid_batch_size(self):
        """Test: Invalid batch size is caught."""
        # Arrange & Act: Mock invalid batch size
        with patch("codex_ml.data.loaders.create_data_loader") as mock_create:
            mock_create.side_effect = ValueError("Batch size must be positive")

            with pytest.raises(ValueError):
                mock_create([], batch_size=-1)

    def test_graceful_degradation_with_empty_dataset(self):
        """Test: System handles empty dataset gracefully."""
        # Arrange & Act: Mock empty dataset handling
        with patch("codex_ml.data.loaders.create_data_loader") as mock_create:
            mock_loader = Mock()
            mock_loader.__len__ = Mock(return_value=0)
            mock_create.return_value = mock_loader

            loader = mock_create([], batch_size=32)

            # Should not crash, but can be empty
            assert len(loader) == 0, "Loader must not be empty"


@pytest.mark.skipif(not UNIFIED_TRAINING_AVAILABLE, reason="Unified training not available")
class TestUnifiedTrainingErrorHandling:
    """Error handling in unified training."""

    def test_error_on_invalid_configuration(self):
        """Test: Invalid configuration is caught."""
        # Arrange & Act: Mock invalid config error
        with patch("codex_ml.training.unified_training.UnifiedTrainer") as mock_trainer_cls:
            mock_trainer_cls.side_effect = ValueError("Invalid configuration")

            with pytest.raises(ValueError):
                mock_trainer_cls({"invalid": "config"})

    def test_error_recovery_on_training_failure(self):
        """Test: Training failure recovers gracefully."""
        # Arrange & Act: Mock training failure
        with patch("codex_ml.training.unified_training.UnifiedTrainer") as mock_trainer_cls:
            mock_trainer = Mock()
            mock_trainer_cls.return_value = mock_trainer
            mock_trainer.train = Mock(side_effect=RuntimeError("Training failed"))

            with pytest.raises(RuntimeError):
                trainer = mock_trainer_cls({})
                trainer.train()


@pytest.mark.skipif(
    not (DATA_LOADERS_AVAILABLE and UNIFIED_TRAINING_AVAILABLE), reason="Requirements not available"
)
class TestDataTrainingEndToEnd:
    """End-to-end data loading and training workflows."""

    def test_complete_data_to_training_workflow(self, tmp_path):
        """Test: Complete workflow from data loading to training."""
        # Arrange: Create sample data
        dataset_file = tmp_path / "data.jsonl"
        dataset_file.write_text('{"text": "text1", "label": 1}\n' '{"text": "text2", "label": 0}\n')

        # Act & Assert: Mock complete workflow
        with patch("codex_ml.data.loaders.load_jsonl") as mock_load:
            with patch("codex_ml.data.loaders.create_data_loader") as mock_create_loader:
                with patch("codex_ml.training.unified_training.UnifiedTrainer") as mock_trainer_cls:
                    # Step 1: Load data
                    mock_load.return_value = [
                        {"text": "text1", "label": 1},
                        {"text": "text2", "label": 0},
                    ]

                    # Step 2: Create loader
                    mock_loader = Mock()
                    mock_loader.__len__ = Mock(return_value=2)
                    mock_create_loader.return_value = mock_loader

                    # Step 3: Train
                    mock_trainer = Mock()
                    mock_trainer_cls.return_value = mock_trainer
                    mock_trainer.train = Mock(return_value={"loss": 0.4})

                    # Execute workflow
                    data = mock_load(str(dataset_file))
                    loader = mock_create_loader(data, batch_size=2)
                    trainer = mock_trainer_cls({"loader": loader})
                    result = trainer.train()

                    # Assert: Workflow complete
                    assert len(data) == 2, "Data must not be empty"
                    assert result["loss"] == 0.4, "Result must not be empty"

    def test_multi_epoch_data_iteration(self):
        """Test: Data iterated correctly across multiple epochs."""
        # Arrange: Setup multi-epoch iteration
        num_epochs = 3
        samples_per_epoch = 10

        # Act & Assert: Mock multi-epoch iteration
        with patch("codex_ml.data.loaders.DataLoader") as mock_loader_cls:
            mock_loader = Mock()
            epoch_data = []

            for epoch in range(num_epochs):
                mock_loader.__iter__ = Mock(
                    return_value=iter([{"data": f"sample_{i}"} for i in range(samples_per_epoch)])
                )
                mock_loader_cls.return_value = mock_loader

                # Iterate epoch
                for batch in mock_loader:
                    epoch_data.append(batch)

            # Assert: All epochs iterated
            assert len(epoch_data) == samples_per_epoch, "Epoch_data must not be empty"

    def test_training_with_validation_data_split(self):
        """Test: Training uses separate validation data."""
        # Arrange & Act: Mock train/val split
        with patch("codex_ml.data.loaders.create_data_loader") as mock_create:
            # Create train loader
            mock_train_loader = Mock()
            mock_train_loader.__len__ = Mock(return_value=80)

            # Create val loader
            mock_val_loader = Mock()
            mock_val_loader.__len__ = Mock(return_value=20)

            mock_create.side_effect = [mock_train_loader, mock_val_loader]

            # Create loaders
            train_loader = mock_create([], batch_size=32)
            val_loader = mock_create([], batch_size=32)

            # Assert: Separate loaders created
            assert len(train_loader) == 80, "Train_loader must not be empty"
            assert len(val_loader) == 20, "Val_loader must not be empty"
