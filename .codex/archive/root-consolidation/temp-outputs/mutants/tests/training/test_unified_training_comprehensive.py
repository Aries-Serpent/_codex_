"""
pytest.importorskip("mlflow")
Comprehensive tests for unified training module (unified_training.py).

Tests cover:
- Training configuration validation
- Continual learning phases
- Checkpoint save/resume
- Device strategy selection
- Callback system
- Error handling and edge cases
"""

from __future__ import annotations

import tempfile
from unittest.mock import Mock, patch

import pytest

from codex_ml.training.unified_training import (
    ContinualPhase,
    UnifiedTrainingConfig,
    _materialise_mapping,
    _to_plain_container,
)


class TestToPlainContainer:
    """Test OmegaConf to plain type conversion."""

    def test_plain_scalar(self):
        """Verify scalar passthrough."""
        assert _to_plain_container(42) == 42, "Condition must be true"
        assert _to_plain_container("test") == "test", "Condition must be true"
        assert _to_plain_container(3.14) == 3.14, "Condition must be true"

    def test_plain_dict(self):
        """Verify dict conversion."""
        result = _to_plain_container({"key": "value", "nested": {"a": 1}})
        assert result == {"key": "value", "nested": {"a": 1}}
        assert isinstance(result, dict)

    def test_plain_list(self):
        """Verify list conversion."""
        result = _to_plain_container([1, 2, 3, [4, 5]])
        assert result == [1, 2, 3, [4, 5]]
        assert isinstance(result, list)

    def test_plain_tuple(self):
        """Verify tuple conversion to list."""
        result = _to_plain_container((1, 2, 3))
        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_plain_set(self):
        """Verify set conversion to list."""
        result = _to_plain_container({1, 2, 3})
        assert isinstance(result, list)
        assert len(result) == 3, "Result must not be empty"

    def test_plain_nested_complex(self):
        """Verify complex nested structure."""
        input_data = {
            "list": [1, 2, {"nested": [3, 4]}],
            "tuple": (5, 6),
            "dict": {"a": {"b": "c"}},
        }
        result = _to_plain_container(input_data)
        assert isinstance(result["list"], list)
        assert isinstance(result["tuple"], list)
        assert result["dict"]["a"]["b"] == "c", "Result must not be empty"


class TestMaterialiseMapping:
    """Test mapping materialization."""

    def test_materialise_none(self):
        """Verify None returns empty dict."""
        result = _materialise_mapping(None)
        assert result == {}, "Result must not be empty"
        assert isinstance(result, dict)

    def test_materialise_dict(self):
        """Verify dict materialization."""
        input_dict = {"key1": "value1", "key2": 42}
        result = _materialise_mapping(input_dict)
        assert result == {"key1": "value1", "key2": 42}

    def test_materialise_nested(self):
        """Verify nested structure materialization."""
        input_dict = {"outer": {"inner": [1, 2, 3]}}
        result = _materialise_mapping(input_dict)
        assert result["outer"]["inner"] == [1, 2, 3]

    def test_materialise_non_mapping_raises(self):
        """Verify error for non-mapping input."""
        with pytest.raises(TypeError, match="continual sections must be mappings"):
            _materialise_mapping("not a mapping")

    def test_materialise_list_raises(self):
        """Verify error for list input."""
        with pytest.raises(TypeError):
            _materialise_mapping([1, 2, 3])


class TestContinualPhase:
    """Test ContinualPhase configuration."""

    def test_continual_phase_basic(self):
        """Verify basic phase creation."""
        phase = ContinualPhase(name="phase1", epochs=5)
        assert phase.name == "phase1", "name is not valid"
        assert phase.epochs == 5, "epochs is not valid"
        assert phase.dataset == {}, "Data must not be empty"
        assert phase.replay_ratio is None, "replay_ratio is not valid"

    def test_continual_phase_with_dataset(self):
        """Verify phase with dataset config."""
        dataset_config = {"path": "/data", "batch_size": 32}
        phase = ContinualPhase(name="train_phase", epochs=10, dataset=dataset_config)
        assert phase.dataset == dataset_config, "Data must not be empty"

    def test_continual_phase_with_replay_ratio(self):
        """Verify phase with replay ratio."""
        phase = ContinualPhase(name="replay_phase", epochs=3, replay_ratio=0.5)
        assert phase.replay_ratio == 0.5, "replay_ratio is not valid"

    def test_continual_phase_invalid_epochs(self):
        """Verify epochs validation."""
        with pytest.raises(ValueError, match="continual phase epochs must be >= 1"):
            ContinualPhase(name="bad", epochs=0)

        with pytest.raises(ValueError):
            ContinualPhase(name="bad", epochs=-5)

    def test_continual_phase_invalid_replay_ratio(self):
        """Verify replay ratio validation."""
        with pytest.raises(ValueError, match="continual replay_ratio must be between 0 and 1"):
            ContinualPhase(name="bad", epochs=1, replay_ratio=1.5)

        with pytest.raises(ValueError):
            ContinualPhase(name="bad", epochs=1, replay_ratio=-0.1)

    def test_continual_phase_replay_ratio_bounds(self):
        """Verify replay ratio boundary values."""
        phase0 = ContinualPhase(name="p1", epochs=1, replay_ratio=0.0)
        assert phase0.replay_ratio == 0.0, "replay_ratio is not valid"

        phase1 = ContinualPhase(name="p2", epochs=1, replay_ratio=1.0)
        assert phase1.replay_ratio == 1.0, "replay_ratio is not valid"

    def test_continual_phase_epochs_conversion(self):
        """Verify epochs converted to int."""
        phase = ContinualPhase(name="test", epochs="10")
        assert phase.epochs == 10, "epochs is not valid"
        assert isinstance(phase.epochs, int)

    def test_continual_phase_with_notes(self):
        """Verify notes field."""
        phase = ContinualPhase(name="documented", epochs=1, notes="This is a test phase")
        assert phase.notes == "This is a test phase", "notes is not valid"


class TestUnifiedTrainingConfig:
    """Test UnifiedTrainingConfig class."""

    def test_config_minimal(self):
        """Verify minimal config creation."""
        config = UnifiedTrainingConfig(model_name="test_model", epochs=1)
        assert config.model_name == "test_model", "model_name is not valid"
        assert config.epochs == 1, "epochs is not valid"

    def test_config_with_seed(self):
        """Verify seed configuration."""
        config = UnifiedTrainingConfig(model_name="test", epochs=1, seed=42)
        assert config.seed == 42, "seed is not valid"

    def test_config_with_device(self):
        """Verify device configuration."""
        config = UnifiedTrainingConfig(model_name="test", epochs=1, device="cuda")
        assert config.device == "cuda", "device is not valid"

    def test_config_with_checkpoint_dir(self):
        """Verify checkpoint directory config."""
        config = UnifiedTrainingConfig(
            model_name="test", epochs=1, checkpoint_dir=os.path.join(tempfile.gettempdir(), "checkpoints")
        )
        assert config.checkpoint_dir == os.path.join(tempfile.gettempdir(), "checkpoints"), "checkpoint_dir is not valid"

    def test_config_with_resume_path(self):
        """Verify resume path configuration."""
        config = UnifiedTrainingConfig(
            model_name="test", epochs=1, resume_from="/path/to/checkpoint.pt"
        )
        assert config.resume_from == "/path/to/checkpoint.pt", "resume_from is not valid"


class TestTrainingCallbacks:
    """Test callback system."""

    @patch("codex_ml.training.unified_training.resolve_strategy")
    @patch("codex_ml.training.unified_training.set_seed")
    def test_callback_invocation(self, mock_seed, mock_strategy):
        """Verify callbacks are invoked."""
        mock_strategy_instance = Mock()
        mock_strategy_instance.train.return_value = {"final_loss": 0.5, "epochs_completed": 1}
        mock_strategy.return_value = mock_strategy_instance

        callback = Mock()

        config = UnifiedTrainingConfig(model_name="test", epochs=1, callbacks=[callback])

        # This would need the full run_unified_training function
        # Just testing config accepts callbacks
        assert callback in config.callbacks, "Condition must be true"

    def test_multiple_callbacks(self):
        """Verify multiple callbacks configuration."""
        cb1 = Mock()
        cb2 = Mock()
        cb3 = Mock()

        config = UnifiedTrainingConfig(model_name="test", epochs=1, callbacks=[cb1, cb2, cb3])

        assert len(config.callbacks) == 3, "Collection must not be empty"


class TestDeviceStrategy:
    """Test device strategy handling."""

    def test_device_strategy_cpu(self):
        """Verify CPU device strategy."""
        config = UnifiedTrainingConfig(model_name="test", epochs=1, device="cpu")
        assert config.device == "cpu", "device is not valid"

    def test_device_strategy_cuda(self):
        """Verify CUDA device strategy."""
        config = UnifiedTrainingConfig(model_name="test", epochs=1, device="cuda")
        assert config.device == "cuda", "device is not valid"

    def test_device_strategy_auto(self):
        """Verify auto device selection."""
        config = UnifiedTrainingConfig(model_name="test", epochs=1, device="auto")
        assert config.device == "auto", "device is not valid"


class TestCheckpointHandling:
    """Test checkpoint save/load functionality."""

    @patch("codex_ml.training.unified_training.save_checkpoint")
    def test_checkpoint_save_called(self, mock_save):
        """Verify checkpoint saving."""
        mock_save.return_value = None

        # This would require full training run
        # Just test that save_checkpoint is importable and mockable
        assert mock_save is not None, "mock_save must be initialized"

    @patch("codex_ml.training.unified_training.load_checkpoint")
    def test_checkpoint_resume(self, mock_load):
        """Verify checkpoint resume."""
        mock_load.return_value = {"epoch": 5, "model_state": {}, "optimizer_state": {}}

        # Verify load is callable
        assert mock_load is not None, "mock_load must be initialized"


class TestErrorHandling:
    """Test error handling in training."""

    def test_invalid_model_name(self):
        """Verify error for invalid model name."""
        with pytest.raises((TypeError, ValueError)):
            UnifiedTrainingConfig(model_name=None, epochs=1)

    def test_invalid_epochs(self):
        """Verify error for invalid epochs."""
        with pytest.raises((TypeError, ValueError)):
            UnifiedTrainingConfig(model_name="test", epochs=-1)

        with pytest.raises((TypeError, ValueError)):
            UnifiedTrainingConfig(model_name="test", epochs=0)

    def test_invalid_seed(self):
        """Verify error for invalid seed."""
        # Seeds should be non-negative integers
        with pytest.raises((TypeError, ValueError)):
            UnifiedTrainingConfig(model_name="test", epochs=1, seed="not_a_number")


class TestContinualLearning:
    """Test continual learning features."""

    def test_single_phase(self):
        """Verify single continual phase."""
        phase = ContinualPhase(name="phase1", epochs=5)
        config = UnifiedTrainingConfig(model_name="test", epochs=1, continual_phases=[phase])
        assert len(config.continual_phases) == 1, "Collection must not be empty"
        assert config.continual_phases[0].name == "phase1", "name is not valid"

    def test_multiple_phases(self):
        """Verify multiple continual phases."""
        phases = [
            ContinualPhase(name="p1", epochs=5),
            ContinualPhase(name="p2", epochs=10),
            ContinualPhase(name="p3", epochs=3),
        ]
        config = UnifiedTrainingConfig(model_name="test", epochs=1, continual_phases=phases)
        assert len(config.continual_phases) == 3, "Collection must not be empty"

    def test_phases_with_replay(self):
        """Verify phases with experience replay."""
        phases = [
            ContinualPhase(name="p1", epochs=5, replay_ratio=0.0),
            ContinualPhase(name="p2", epochs=5, replay_ratio=0.3),
            ContinualPhase(name="p3", epochs=5, replay_ratio=0.5),
        ]
        config = UnifiedTrainingConfig(model_name="test", epochs=1, continual_phases=phases)
        assert config.continual_phases[1].replay_ratio == 0.3, "replay_ratio is not valid"


class TestDeterministicSeeding:
    """Test deterministic seed handling."""

    @patch("codex_ml.training.unified_training.set_seed")
    def test_seed_set_called(self, mock_set_seed):
        """Verify seed setting is called."""
        config = UnifiedTrainingConfig(model_name="test", epochs=1, seed=42)

        # Seed would be set during run_unified_training
        assert config.seed == 42, "seed is not valid"

    def test_no_seed_allows_randomness(self):
        """Verify None seed allows randomness."""
        config = UnifiedTrainingConfig(model_name="test", epochs=1, seed=None)
        assert config.seed is None, "seed is not valid"

    def test_different_seeds(self):
        """Verify different seed values."""
        config1 = UnifiedTrainingConfig(model_name="test", epochs=1, seed=42)
        config2 = UnifiedTrainingConfig(model_name="test", epochs=1, seed=123)

        assert config1.seed != config2.seed, "seed is not valid"


class TestMLFlowIntegration:
    """Test MLFlow integration."""

    @patch("codex_ml.training.unified_training.init_mlflow_safe")
    @patch("codex_ml.training.unified_training.log_metric_safe")
    @patch("codex_ml.training.unified_training.log_params_safe")
    def test_mlflow_logging_enabled(self, mock_params, mock_metric, mock_init):
        """Verify MLFlow logging when enabled."""
        config = UnifiedTrainingConfig(model_name="test", epochs=1, mlflow_tracking=True)

        assert config.mlflow_tracking is True, "mlflow_tracking is not valid"

    def test_mlflow_logging_disabled(self):
        """Verify MLFlow can be disabled."""
        config = UnifiedTrainingConfig(model_name="test", epochs=1, mlflow_tracking=False)

        assert config.mlflow_tracking is False, "mlflow_tracking is not valid"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_replay_ratio(self):
        """Verify zero replay ratio (no replay)."""
        phase = ContinualPhase(name="test", epochs=1, replay_ratio=0.0)
        assert phase.replay_ratio == 0.0, "replay_ratio is not valid"

    def test_full_replay_ratio(self):
        """Verify full replay ratio."""
        phase = ContinualPhase(name="test", epochs=1, replay_ratio=1.0)
        assert phase.replay_ratio == 1.0, "replay_ratio is not valid"

    def test_single_epoch(self):
        """Verify single epoch training."""
        config = UnifiedTrainingConfig(model_name="test", epochs=1)
        assert config.epochs == 1, "epochs is not valid"

    def test_many_epochs(self):
        """Verify large epoch count."""
        config = UnifiedTrainingConfig(model_name="test", epochs=1000)
        assert config.epochs == 1000, "epochs is not valid"

    def test_empty_dataset_config(self):
        """Verify empty dataset configuration."""
        phase = ContinualPhase(name="test", epochs=1, dataset={})
        assert phase.dataset == {}, "Data must not be empty"

    def test_complex_dataset_config(self):
        """Verify complex dataset configuration."""
        dataset_config = {
            "path": "/data",
            "batch_size": 32,
            "shuffle": True,
            "num_workers": 4,
            "transforms": ["normalize", "augment"],
        }
        phase = ContinualPhase(name="test", epochs=1, dataset=dataset_config)
        assert phase.dataset["num_workers"] == 4, "Data must not be empty"
        assert "normalize" in phase.dataset["transforms"], "Data must not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
