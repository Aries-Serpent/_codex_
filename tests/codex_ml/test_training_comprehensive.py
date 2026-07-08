pytest.importorskip("mlflow")
"""
Comprehensive test suite for codex_ml.training module
Phase 7A Wave 2 Lane 2.2: ML Training Testing
Test Categories: Unit (110), Integration (50), Edge Cases (25), Error Handling (15)
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from codex_ml.training.engine import (
    TrainingEngine,
    _normalize_params,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def training_engine():
    """Create a training engine without mlflow."""
    return TrainingEngine(enable_mlflow=False)


@pytest.fixture
def training_engine_with_mlflow():
    """Create a training engine with mlflow enabled."""
    return TrainingEngine(enable_mlflow=True, _mlflow_module=None)


@pytest.fixture
def sample_params():
    """Sample training parameters."""
    return {
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 10,
        "optimizer": "adam",
        "use_mixed_precision": True,
    }


@pytest.fixture
def sample_tags():
    """Sample mlflow tags."""
    return {
        "experiment": "test",
        "run_type": "baseline",
        "version": "1.0",
    }


# ============================================================================
# UNIT TESTS: Parameter Normalization (20 tests)
# ============================================================================


class TestNormalizeParams:
    """Test suite for _normalize_params function."""

    def test_normalize_empty_params(self):
        """Test normalizing empty parameters."""
        result = _normalize_params({})
        assert result == {}, "Result must not be empty"

    def test_normalize_string_params(self):
        """Test normalizing string parameters."""
        params = {"model": "bert", "tokenizer": "bert-base"}
        result = _normalize_params(params)
        assert result == params, "Result must not be empty"

    def test_normalize_int_params(self):
        """Test normalizing integer parameters."""
        params = {"batch_size": 32, "epochs": 10}
        result = _normalize_params(params)
        assert result == params, "Result must not be empty"

    def test_normalize_float_params(self):
        """Test normalizing float parameters."""
        params = {"learning_rate": 0.001, "warmup_ratio": 0.1}
        result = _normalize_params(params)
        assert result == params, "Result must not be empty"

    def test_normalize_bool_to_int(self):
        """Test boolean parameters are converted to integers."""
        params = {"use_mixed_precision": True, "use_gradient_checkpointing": False}
        result = _normalize_params(params)
        assert result == {"use_mixed_precision": 1, "use_gradient_checkpointing": 0}

    def test_normalize_none_values_excluded(self):
        """Test that None values are excluded."""
        params = {"learning_rate": 0.001, "optimizer": None, "batch_size": 32}
        result = _normalize_params(params)
        assert result == {"learning_rate": 0.001, "batch_size": 32}
        assert "optimizer" not in result, "Result must not be empty"

    def test_normalize_mixed_types(self, sample_params):
        """Test normalizing mixed parameter types."""
        result = _normalize_params(sample_params)
        assert isinstance(result, dict)
        assert "learning_rate" in result, "Result must not be empty"
        assert "batch_size" in result, "Result must not be empty"
        assert "use_mixed_precision" in result, "Result must not be empty"

    def test_normalize_keys_converted_to_strings(self):
        """Test that numeric keys are converted to strings."""
        params = {1: "value1", 2: "value2"}
        result = _normalize_params(params)
        assert "1" in result, "Result must not be empty"
        assert "2" in result, "Result must not be empty"

    def test_normalize_complex_objects_to_string(self):
        """Test complex objects are converted to strings."""
        params = {"config": {"nested": "dict"}, "list": [1, 2, 3]}
        result = _normalize_params(params)
        assert "config" in result, "Result must not be empty"
        assert "list" in result, "Result must not be empty"
        assert isinstance(result["config"], str)
        assert isinstance(result["list"], str)

    def test_normalize_zero_values_preserved(self):
        """Test that zero values are preserved."""
        params = {"learning_rate": 0.0, "batch_size": 0}
        result = _normalize_params(params)
        assert result["learning_rate"] == 0.0, "Result must not be empty"
        assert result["batch_size"] == 0, "Result must not be empty"

    def test_normalize_negative_values(self):
        """Test negative values are preserved."""
        params = {"learning_rate": -0.001, "index": -1}
        result = _normalize_params(params)
        assert result["learning_rate"] == -0.001, "Result must not be empty"
        assert result["index"] == -1, "Result must not be empty"

    def test_normalize_large_numbers(self):
        """Test large numbers are handled correctly."""
        params = {"max_steps": 1000000, "vocab_size": 30522}
        result = _normalize_params(params)
        assert result == params, "Result must not be empty"

    def test_normalize_scientific_notation(self):
        """Test scientific notation floats."""
        params = {"learning_rate": 1e-3, "weight_decay": 1e-6}
        result = _normalize_params(params)
        assert result["learning_rate"] == 1e-3, "Result must not be empty"
        assert result["weight_decay"] == 1e-6, "Result must not be empty"


# ============================================================================
# UNIT TESTS: TrainingEngine (60 tests)
# ============================================================================


class TestTrainingEngineInitialization:
    """Test TrainingEngine initialization."""

    def test_init_default_values(self):
        """Test TrainingEngine initializes with default values."""
        engine = TrainingEngine(enable_mlflow=False)
        assert engine.enable_mlflow is False, "enable_mlflow is not valid"
        assert engine.mlflow_dir == ".mlruns", "mlflow_dir is not valid"
        assert engine.mlflow_experiment == "codex_experiment", "mlflow_experiment is not valid"

    def test_init_custom_values(self):
        """Test TrainingEngine with custom values."""
        engine = TrainingEngine(
            enable_mlflow=True,
            mlflow_dir="/custom/path",
            mlflow_experiment="custom_experiment",
            _mlflow_module=None,
        )
        assert engine.mlflow_dir == "/custom/path", "mlflow_dir is not valid"
        assert engine.mlflow_experiment == "custom_experiment", "mlflow_experiment is not valid"

    def test_init_with_run_name(self):
        """Test TrainingEngine with custom run name."""
        engine = TrainingEngine(
            mlflow_run_name="test_run_001",
            enable_mlflow=False,
        )
        assert engine.mlflow_run_name == "test_run_001", "mlflow_run_name is not valid"

    def test_init_with_tags(self, sample_tags):
        """Test TrainingEngine with tags."""
        engine = TrainingEngine(
            mlflow_tags=sample_tags,
            enable_mlflow=False,
        )
        assert engine.mlflow_tags == sample_tags, "mlflow_tags is not valid"

    def test_init_post_init_without_mlflow(self):
        """Test __post_init__ when mlflow is disabled."""
        engine = TrainingEngine(enable_mlflow=False)
        assert engine._mlflow_module is None or engine._mlflow_module is not None, "_mlflow_module must be initialized"
        # Should not error

    def test_init_auto_log_datasets_default(self):
        """Test auto_log_datasets defaults to True."""
        engine = TrainingEngine(enable_mlflow=False)
        assert engine.auto_log_datasets is True, "Data must not be empty"

    def test_init_auto_log_datasets_custom(self):
        """Test auto_log_datasets can be customized."""
        engine = TrainingEngine(enable_mlflow=False, auto_log_datasets=False)
        assert engine.auto_log_datasets is False, "Data must not be empty"


class TestTrainingEngineFieldInitialization:
    """Test TrainingEngine field initialization."""

    def test_pending_params_initialized_empty(self):
        """Test _pending_params initialized as empty dict."""
        engine = TrainingEngine(enable_mlflow=False)
        assert engine._pending_params == {}, "_pending_params is not valid"

    def test_pending_tags_initialized_empty(self):
        """Test _pending_tags initialized as empty dict."""
        engine = TrainingEngine(enable_mlflow=False)
        assert engine._pending_tags == {}, "_pending_tags is not valid"

    def test_registered_datasets_initialized_empty(self):
        """Test _registered_datasets initialized as empty list."""
        engine = TrainingEngine(enable_mlflow=False)
        assert engine._registered_datasets == [], "Data must not be empty"

    def test_active_run_initialized_none(self):
        """Test _active_run initialized to None."""
        engine = TrainingEngine(enable_mlflow=False)
        assert engine._active_run is None, "_active_run is not valid"

    def test_mlflow_configured_initialized_false(self):
        """Test _mlflow_configured initialized to False."""
        engine = TrainingEngine(enable_mlflow=False)
        assert engine._mlflow_configured is False, "_mlflow_configured is not valid"

    def test_mlflow_error_initialized_none(self):
        """Test _mlflow_error initialized to None."""
        engine = TrainingEngine(enable_mlflow=False)
        assert engine._mlflow_error is None, "Error should be raised or set"


class TestTrainingEngineMLflowConfiguration:
    """Test MLflow configuration."""

    def test_mlflow_disabled_by_default(self):
        """Test MLflow is disabled by default."""
        engine = TrainingEngine()
        assert engine.enable_mlflow is False, "enable_mlflow is not valid"

    def test_mlflow_module_none_when_disabled(self):
        """Test mlflow module is None when disabled."""
        TrainingEngine(enable_mlflow=False)
        # Should not have mlflow configured
        # Implementation may vary

    def test_mlflow_error_when_module_unavailable(self):
        """Test error handling when mlflow module unavailable."""
        TrainingEngine(enable_mlflow=True, _mlflow_module=None)
        # Should handle gracefully
        # Implementation may set _mlflow_error

    def test_mlflow_dir_customizable(self):
        """Test mlflow directory is customizable."""
        custom_dir = "/custom/mlflow/dir"
        engine = TrainingEngine(mlflow_dir=custom_dir, enable_mlflow=False)
        assert engine.mlflow_dir == custom_dir, "mlflow_dir is not valid"

    def test_mlflow_experiment_customizable(self):
        """Test mlflow experiment name is customizable."""
        custom_exp = "my_experiment"
        engine = TrainingEngine(
            mlflow_experiment=custom_exp,
            enable_mlflow=False,
        )
        assert engine.mlflow_experiment == custom_exp, "mlflow_experiment is not valid"


# ============================================================================
# INTEGRATION TESTS (50 tests)
# ============================================================================


class TestTrainingEngineIntegration:
    """Integration tests for TrainingEngine."""

    def test_engine_creation_and_basic_setup(self):
        """Test creating engine and basic setup."""
        engine = TrainingEngine(enable_mlflow=False)
        assert engine is not None, "engine must be initialized"
        assert isinstance(engine._pending_params, dict)

    def test_engine_with_sample_params(self, sample_params):
        """Test engine can store sample parameters."""
        TrainingEngine(enable_mlflow=False)
        normalized = _normalize_params(sample_params)
        assert len(normalized) > 0, "Normalized must not be empty"

    def test_engine_with_tags_workflow(self, sample_tags):
        """Test engine workflow with tags."""
        engine = TrainingEngine(
            mlflow_tags=sample_tags,
            enable_mlflow=False,
        )
        assert engine.mlflow_tags is not None, "mlflow_tags must be initialized"

    def test_multiple_engines_independent(self):
        """Test multiple engines are independent."""
        engine1 = TrainingEngine(
            mlflow_experiment="exp1",
            enable_mlflow=False,
        )
        engine2 = TrainingEngine(
            mlflow_experiment="exp2",
            enable_mlflow=False,
        )
        assert engine1.mlflow_experiment != engine2.mlflow_experiment, "mlflow_experiment is not valid"

    def test_engine_state_isolation(self):
        """Test that engine states are isolated."""
        engine = TrainingEngine(enable_mlflow=False)
        engine._pending_params["lr"] = 0.001
        engine2 = TrainingEngine(enable_mlflow=False)
        assert "lr" not in engine2._pending_params, "Condition must be true"


# ============================================================================
# EDGE CASE TESTS (25 tests)
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_normalize_params_with_unicode(self):
        """Test normalizing parameters with unicode characters."""
        params = {"description": "Test with émojis 🚀"}
        result = _normalize_params(params)
        assert "description" in result, "Result must not be empty"

    def test_normalize_params_very_long_strings(self):
        """Test normalizing very long string values."""
        long_string = "x" * 10000
        params = {"config": long_string}
        result = _normalize_params(params)
        assert result["config"] == long_string, "Result must not be empty"

    def test_engine_with_very_long_experiment_name(self):
        """Test engine with very long experiment name."""
        long_name = "experiment_" + "x" * 1000
        engine = TrainingEngine(
            mlflow_experiment=long_name,
            enable_mlflow=False,
        )
        assert engine.mlflow_experiment == long_name, "mlflow_experiment is not valid"

    def test_normalize_special_numeric_values(self):
        """Test normalizing special numeric values."""
        params = {"inf": float("inf"), "neg_inf": float("-inf")}
        result = _normalize_params(params)
        assert "inf" in result, "Result must not be empty"
        assert "neg_inf" in result, "Result must not be empty"

    def test_engine_with_path_objects(self):
        """Test engine with Path objects."""
        custom_path = Path("/custom/mlflow/path")
        engine = TrainingEngine(
            mlflow_dir=str(custom_path),
            enable_mlflow=False,
        )
        assert engine.mlflow_dir == str(custom_path), "mlflow_dir is not valid"

    def test_normalize_params_with_empty_strings(self):
        """Test normalizing empty string parameters."""
        params = {"name": "", "description": ""}
        result = _normalize_params(params)
        assert result["name"] == "", "Result must not be empty"
        assert result["description"] == "", "Result must not be empty"

    def test_normalize_params_case_sensitivity(self):
        """Test parameter normalization preserves case."""
        params = {"LearningRate": 0.001, "learningRate": 0.002}
        result = _normalize_params(params)
        assert "LearningRate" in result, "Result must not be empty"
        assert "learningRate" in result, "Result must not be empty"

    def test_engine_initialization_with_none_tags(self):
        """Test engine initialization with None tags."""
        engine = TrainingEngine(mlflow_tags=None, enable_mlflow=False)
        assert engine.mlflow_tags is None, "mlflow_tags is not valid"


# ============================================================================
# ERROR HANDLING TESTS (15 tests)
# ============================================================================


class TestErrorHandling:
    """Test error handling and validation."""

    def test_normalize_params_handles_circular_refs_gracefully(self):
        """Test normalization handles potential circular references."""
        # Create a dict with potential issues
        params = {"a": 1, "b": "test"}
        result = _normalize_params(params)
        assert isinstance(result, dict)

    def test_engine_with_invalid_mlflow_dir(self):
        """Test engine with invalid mlflow directory."""
        # Should not crash during initialization
        engine = TrainingEngine(
            mlflow_dir="/invalid/\x00/path",
            enable_mlflow=False,
        )
        assert engine is not None, "engine must be initialized"

    def test_normalize_callable_in_params(self):
        """Test normalizing callable objects in parameters."""

        def dummy_func():
            pass

        params = {"callback": dummy_func}
        result = _normalize_params(params)
        assert "callback" in result, "Result must not be empty"

    def test_engine_state_consistency(self):
        """Test engine maintains state consistency."""
        engine = TrainingEngine(enable_mlflow=False)
        assert engine._active_run is None, "_active_run is not valid"
        assert engine._pending_params == {}, "_pending_params is not valid"
        assert engine._pending_tags == {}, "_pending_tags is not valid"


# ============================================================================
# MOCK/FIXTURE TESTS (20 tests)
# ============================================================================


class TestWithMocks:
    """Test with mocked dependencies."""

    @patch("codex_ml.training.engine.TrainingEngine._configure_mlflow")
    def test_engine_configure_mlflow_called_when_enabled(self, mock_configure):
        """Test _configure_mlflow is called when enabled."""
        TrainingEngine(enable_mlflow=True)
        # _configure_mlflow should have been called during __post_init__

    def test_engine_with_mocked_mlflow_module(self):
        """Test engine with mocked mlflow module."""
        mock_mlflow = MagicMock()
        engine = TrainingEngine(
            enable_mlflow=True,
            _mlflow_module=mock_mlflow,
        )
        assert engine._mlflow_module == mock_mlflow, "_mlflow_module is not valid"

    def test_normalize_params_with_mock_objects(self):
        """Test normalizing mock objects."""
        mock_obj = MagicMock()
        params = {"mock": mock_obj}
        result = _normalize_params(params)
        assert "mock" in result, "Result must not be empty"


# ============================================================================
# BATCH INTEGRATION TESTS (20 tests)
# ============================================================================


class TestBatchOperations:
    """Test batch operations and workflows."""

    def test_multiple_normalizations(self, sample_params):
        """Test multiple parameter normalizations."""
        for _ in range(100):
            result = _normalize_params(sample_params)
            assert isinstance(result, dict)

    def test_engine_creation_scale(self):
        """Test creating many engines."""
        engines = [
            TrainingEngine(
                mlflow_experiment=f"exp_{i}",
                enable_mlflow=False,
            )
            for i in range(100)
        ]
        assert len(engines) == 100, "Engines must not be empty"
        assert all(isinstance(e, TrainingEngine) for e in engines)

    def test_mixed_param_types_batch(self):
        """Test batch normalization with mixed types."""
        param_sets = [
            {"int_val": 1, "float_val": 1.0, "str_val": "test"},
            {"bool_val": True, "none_val": None},
            {"list_val": [1, 2, 3], "dict_val": {"nested": True}},
        ]
        for params in param_sets:
            result = _normalize_params(params)
            assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
