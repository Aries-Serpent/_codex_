"""Gap-fill tests for CLI pipeline functionality.

Tests for src/cli/pipeline.py to improve CLI module coverage.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.cli.pipeline import (
    PipelineValidationError,
    run_pipeline,
    validate_pipeline_config,
)


class TestPipelineValidationError:
    """Test PipelineValidationError exception."""

    def test_pipeline_validation_error_raised(self):
        """Test that PipelineValidationError can be raised."""
        with pytest.raises(PipelineValidationError):
            raise PipelineValidationError("Test error")

    def test_pipeline_validation_error_message(self):
        """Test PipelineValidationError with message."""
        msg = "Configuration invalid"
        try:
            raise PipelineValidationError(msg)
        except PipelineValidationError as e:
            assert str(e) == msg, "Condition must be true"


class TestValidatePipelineConfig:
    """Test pipeline configuration validation."""

    def test_validate_config_with_data_key(self):
        """Test validation passes with data key."""
        config = {"data": {}}
        validate_pipeline_config(config)  # Should not raise

    def test_validate_config_with_data_and_model(self):
        """Test validation with data and model keys."""
        config = {"data": {}, "model": {}}
        validate_pipeline_config(config)  # Should not raise

    def test_validate_config_missing_data_key(self):
        """Test validation fails when data key missing."""
        config = {}
        with pytest.raises(KeyError):
            validate_pipeline_config(config)

    def test_validate_config_missing_data_key_error_message(self):
        """Test error message for missing data key."""
        config = {}
        with pytest.raises(KeyError) as exc_info:
            validate_pipeline_config(config)
        assert "data configuration is required" in str(exc_info.value), "Data must not be empty"

    def test_validate_config_with_trainer_and_checkpoint_dict(self):
        """Test validation with trainer and checkpoint as dict."""
        config = {"data": {}, "trainer": {"checkpoint": {}}}
        validate_pipeline_config(config)  # Should not raise

    def test_validate_config_with_trainer_and_valid_checkpoint_path(self):
        """Test validation with valid checkpoint path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = Path(tmpdir) / "checkpoint.pt"
            checkpoint_path.write_text("checkpoint")

            config = {"data": {}, "trainer": {"checkpoint": str(checkpoint_path)}}
            validate_pipeline_config(config)  # Should not raise

    def test_validate_config_with_missing_checkpoint_path(self):
        """Test validation fails with missing checkpoint path."""
        config = {"data": {}, "trainer": {"checkpoint": "/nonexistent/checkpoint.pt"}}
        with pytest.raises(ValueError) as exc_info:
            validate_pipeline_config(config)
        assert "checkpoint file not found" in str(exc_info.value), "Value must be initialized"

    def test_validate_config_with_invalid_checkpoint_type(self):
        """Test validation fails with invalid checkpoint type."""
        config = {"data": {}, "trainer": {"checkpoint": 12345}}  # Invalid type
        with pytest.raises(ValueError) as exc_info:
            validate_pipeline_config(config)
        assert "checkpoint must be a dict or path string" in str(exc_info.value), "Value must be initialized"

    def test_validate_config_with_trainer_no_checkpoint(self):
        """Test validation with trainer config but no checkpoint."""
        config = {"data": {}, "trainer": {"epochs": 10}}
        validate_pipeline_config(config)  # Should not raise

    def test_validate_config_trainer_not_dict(self):
        """Test validation when trainer is not a dict."""
        config = {"data": {}, "trainer": "invalid"}
        validate_pipeline_config(config)  # Should not raise (trainer is not a dict)

    def test_validate_config_with_additional_keys(self):
        """Test validation with additional configuration keys."""
        config = {
            "data": {},
            "model": {},
            "trainer": {"epochs": 5},
            "optimizer": {"lr": 0.001},
        }
        validate_pipeline_config(config)  # Should not raise


class TestRunPipeline:
    """Test pipeline execution."""

    def test_run_pipeline_requires_valid_config(self):
        """Test that run_pipeline validates config."""
        config = {}  # Missing data key
        with pytest.raises(KeyError):
            run_pipeline(None, None, None, None, config)

    def test_run_pipeline_with_valid_config(self):
        """Test run_pipeline with valid minimal config."""
        config = {"data": {}}
        with patch("src.cli.pipeline.TrainConfig") as mock_train_config:
            with patch("src.cli.pipeline.train") as mock_train:
                mock_train.return_value = {"loss": 0.5}
                mock_instance = Mock()
                mock_train_config.return_value = mock_instance

                result = run_pipeline(None, None, [], None, config)

                # Should attempt to import and call train
                assert result is not None, "result must be initialized"

    def test_run_pipeline_with_list_train_dataset(self):
        """Test run_pipeline with list training dataset."""
        config = {"data": {}}
        train_ds = ["text1", "text2", "text3"]

        with patch("src.cli.pipeline.TrainConfig") as mock_train_config:
            with patch("src.cli.pipeline.train") as mock_train:
                mock_train.return_value = {}
                mock_instance = Mock()
                mock_train_config.return_value = mock_instance

                result = run_pipeline(None, None, train_ds, None, config)
                assert result is not None, "result must be initialized"

    def test_run_pipeline_with_texts_attribute(self):
        """Test run_pipeline with dataset having texts attribute."""
        config = {"data": {}}

        # Create mock dataset with texts attribute
        mock_dataset = Mock()
        mock_dataset.texts = ["text1", "text2"]

        with patch("src.cli.pipeline.TrainConfig") as mock_train_config:
            with patch("src.cli.pipeline.train") as mock_train:
                mock_train.return_value = {}
                mock_instance = Mock()
                mock_train_config.return_value = mock_instance

                result = run_pipeline(None, None, mock_dataset, None, config)
                assert result is not None, "result must be initialized"

    def test_run_pipeline_with_iterable_train_dataset(self):
        """Test run_pipeline with iterable training dataset."""
        config = {"data": {}}

        # Create mock iterable dataset
        mock_dataset = iter(["text1", "text2"])

        with patch("src.cli.pipeline.TrainConfig") as mock_train_config:
            with patch("src.cli.pipeline.train") as mock_train:
                mock_train.return_value = {}
                mock_instance = Mock()
                mock_train_config.return_value = mock_instance

                result = run_pipeline(None, None, mock_dataset, None, config)
                assert result is not None, "result must be initialized"

    def test_run_pipeline_with_non_iterable_train_dataset(self):
        """Test run_pipeline raises with non-iterable training dataset."""
        config = {"data": {}}
        mock_dataset = Mock(spec=[])  # No iterable methods

        with pytest.raises(ValueError) as exc_info:
            run_pipeline(None, None, mock_dataset, None, config)
        assert "must be a list" in str(exc_info.value) or "iterable" in str(exc_info.value), "Value must be initialized"

    def test_run_pipeline_with_validation_dataset_list(self):
        """Test run_pipeline with validation dataset as list."""
        config = {"data": {}}
        train_ds = ["text1", "text2"]
        val_ds = ["val1", "val2"]

        with patch("src.cli.pipeline.TrainConfig") as mock_train_config:
            with patch("src.cli.pipeline.train") as mock_train:
                mock_train.return_value = {}
                mock_instance = Mock()
                mock_train_config.return_value = mock_instance

                result = run_pipeline(None, None, train_ds, val_ds, config)
                assert result is not None, "result must be initialized"

    def test_run_pipeline_with_validation_dataset_texts_attr(self):
        """Test run_pipeline with validation dataset having texts attribute."""
        config = {"data": {}}
        train_ds = ["text1"]

        mock_val_ds = Mock()
        mock_val_ds.texts = ["val1", "val2"]

        with patch("src.cli.pipeline.TrainConfig") as mock_train_config:
            with patch("src.cli.pipeline.train") as mock_train:
                mock_train.return_value = {}
                mock_instance = Mock()
                mock_train_config.return_value = mock_instance

                result = run_pipeline(None, None, train_ds, mock_val_ds, config)
                assert result is not None, "result must be initialized"

    def test_run_pipeline_with_trainer_config(self):
        """Test run_pipeline with trainer configuration."""
        config = {
            "data": {},
            "trainer": {
                "epochs": 10,
                "batch_size": 32,
                "lr": 0.001,
                "seed": 42,
                "gradient_accumulation_steps": 2,
                "checkpoint_dir": "/tmp",
            },
        }
        train_ds = ["text1"]

        with patch("src.cli.pipeline.TrainConfig") as mock_train_config:
            with patch("src.cli.pipeline.train") as mock_train:
                mock_train.return_value = {}
                mock_instance = Mock()
                mock_train_config.return_value = mock_instance

                result = run_pipeline(None, None, train_ds, None, config)
                assert result is not None, "result must be initialized"


class TestCLIPipelineErrorHandling:
    """Test CLI pipeline error handling."""

    def test_invalid_config_raises_key_error(self):
        """Test that invalid config raises KeyError."""
        config = {"model": {}}  # Missing data
        with pytest.raises(KeyError):
            validate_pipeline_config(config)

    def test_invalid_checkpoint_path_raises_value_error(self):
        """Test that invalid checkpoint path raises ValueError."""
        config = {"data": {}, "trainer": {"checkpoint": "/nonexistent/path.pt"}}
        with pytest.raises(ValueError):
            validate_pipeline_config(config)
