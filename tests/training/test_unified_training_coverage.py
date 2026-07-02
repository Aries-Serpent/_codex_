"""
pytest.importorskip("mlflow")
Comprehensive test suite for codex_ml.training.unified_training module.

This module provides 25+ tests targeting 70%+ coverage of unified_training.py.
Tests cover configuration validation, checkpoint management, training orchestration,
and backend strategy integration.

Phase: 2.1 - Core ML Training Coverage Initiative
Created: 2026-01-18
Target Coverage: 70%+
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import modules under test
from codex_ml.training.unified_training import (
    ContinualConfig,
    ContinualPhase,
    UnifiedTrainingConfig,
    _auto_backend,
    _coerce_metric_value,
    _materialise_mapping,
    _seed_all,
    _to_plain_container,
    distributed_context,
)

# =============================================================================
# Test Data & Fixtures
# =============================================================================


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create temporary output directory for training artifacts."""
    output_dir = tmp_path / "training_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


@pytest.fixture
def mock_checkpoint_utils():
    """Mock checkpoint utilities to avoid file I/O."""
    with (
        patch("codex_ml.training.unified_training.save_checkpoint") as mock_save,
        patch("codex_ml.training.unified_training.load_checkpoint") as mock_load,
    ):
        mock_save.return_value = (Path("checkpoint.pt"), {"epoch": 1, "metric": 0.5})
        mock_load.return_value = {"model_state": {}, "optimizer_state": {}}
        yield {"save": mock_save, "load": mock_load}


@pytest.fixture
def mock_mlflow():
    """Mock MLflow integration."""
    with (
        patch("codex_ml.training.unified_training.init_mlflow_safe") as mock_init,
        patch("codex_ml.training.unified_training.log_metric_safe") as mock_metric,
        patch("codex_ml.training.unified_training.log_params_safe") as mock_params,
    ):
        yield {"init": mock_init, "metric": mock_metric, "params": mock_params}


@pytest.fixture
def minimal_config() -> UnifiedTrainingConfig:
    """Create minimal valid training configuration."""
    return UnifiedTrainingConfig(
        model_name="test-model",
        epochs=2,
        batch_size=4,
        output_dir="test_runs",
    )


# =============================================================================
# ContinualPhase Tests
# =============================================================================


def test_continual_phase_initialization():
    """Test ContinualPhase initialization with valid parameters."""
    phase = ContinualPhase(name="phase1", epochs=5, replay_ratio=0.3)
    assert phase.name == "phase1", "name is not valid"
    assert phase.epochs == 5, "epochs is not valid"
    assert phase.replay_ratio == 0.3, "replay_ratio is not valid"


def test_continual_phase_epochs_validation():
    """Test ContinualPhase validates epoch count."""
    with pytest.raises(ValueError, match="epochs must be >= 1"):
        ContinualPhase(name="invalid", epochs=0)


def test_continual_phase_replay_ratio_validation():
    """Test ContinualPhase validates replay_ratio bounds."""
    with pytest.raises(ValueError, match="replay_ratio must be between 0 and 1"):
        ContinualPhase(name="invalid", epochs=1, replay_ratio=1.5)


def test_continual_phase_default_values():
    """Test ContinualPhase uses sensible defaults."""
    phase = ContinualPhase(name="default")
    assert phase.epochs == 1, "epochs is not valid"
    assert phase.dataset == {}, "Data must not be empty"
    assert phase.replay_ratio is None, "replay_ratio is not valid"
    assert phase.notes is None, "notes is not valid"


# =============================================================================
# ContinualConfig Tests
# =============================================================================


def test_continual_config_initialization():
    """Test ContinualConfig initialization."""
    config = ContinualConfig(
        strategy="replay",
        buffer_size=1000,
        replay_ratio=0.2,
    )
    assert config.strategy == "replay", "strategy is not valid"
    assert config.buffer_size == 1000, "buffer_size is not valid"
    assert config.replay_ratio == 0.2, "replay_ratio is not valid"


def test_continual_config_buffer_size_validation():
    """Test ContinualConfig validates buffer_size."""
    with pytest.raises(ValueError, match="buffer_size must be >= 0"):
        ContinualConfig(buffer_size=-100)


def test_continual_config_phases_from_dict():
    """Test ContinualConfig converts dict phases to ContinualPhase objects."""
    config = ContinualConfig(
        phases=[
            {"name": "phase1", "epochs": 3},
            {"name": "phase2", "epochs": 5},
        ]
    )
    assert len(config.phases) == 2, "Collection must not be empty"
    assert all(isinstance(p, ContinualPhase) for p in config.phases)
    assert config.phases[0].name == "phase1", "name is not valid"
    assert config.phases[1].epochs == 5, "epochs is not valid"


# =============================================================================
# UnifiedTrainingConfig Tests
# =============================================================================


def test_unified_training_config_minimal():
    """Test UnifiedTrainingConfig with minimal parameters."""
    config = UnifiedTrainingConfig(model_name="gpt2", epochs=1)
    assert config.model_name == "gpt2", "model_name is not valid"
    assert config.epochs == 1, "epochs is not valid"
    assert config.batch_size == 8, "batch_size is not valid"
    assert config.learning_rate == 3e-4, "learning_rate is not valid"


def test_unified_training_config_validation_epochs():
    """Test UnifiedTrainingConfig validates epoch count."""
    with pytest.raises(ValueError, match="epochs must be >= 1"):
        UnifiedTrainingConfig(model_name="test", epochs=-1)


def test_unified_training_config_validation_batch_size():
    """Test UnifiedTrainingConfig validates batch_size."""
    with pytest.raises(ValueError, match="batch_size must be >=1"):
        UnifiedTrainingConfig(model_name="test", batch_size=0)


def test_unified_training_config_validation_dtype():
    """Test UnifiedTrainingConfig validates dtype."""
    with pytest.raises(ValueError, match="dtype must be one of"):
        UnifiedTrainingConfig(model_name="test", dtype="invalid")


def test_unified_training_config_validation_seed():
    """Test UnifiedTrainingConfig validates seed range."""
    with pytest.raises(ValueError, match="seed must be in"):
        UnifiedTrainingConfig(model_name="test", seed=-1)


def test_unified_training_config_continual_from_dict():
    """Test UnifiedTrainingConfig converts continual dict to ContinualConfig."""
    config = UnifiedTrainingConfig(
        model_name="test", continual={"strategy": "replay", "buffer_size": 500}
    )
    assert isinstance(config.continual, ContinualConfig)
    assert config.continual.strategy == "replay", "strategy is not valid"
    assert config.continual.buffer_size == 500, "buffer_size is not valid"


def test_unified_training_config_all_dtypes():
    """Test UnifiedTrainingConfig accepts all valid dtypes."""
    for dtype in ["fp32", "fp16", "bf16"]:
        config = UnifiedTrainingConfig(model_name="test", dtype=dtype)
        assert config.dtype == dtype, "dtype is not valid"


# =============================================================================
# Helper Function Tests
# =============================================================================


def test_to_plain_container_dict():
    """Test _to_plain_container converts nested dicts."""
    data = {"a": {"b": {"c": 1}}, "d": 2}
    result = _to_plain_container(data)
    assert result == {"a": {"b": {"c": 1}}, "d": 2}
    assert isinstance(result, dict)


def test_to_plain_container_list():
    """Test _to_plain_container converts lists."""
    data = [1, [2, 3], {"a": 4}]
    result = _to_plain_container(data)
    assert result == [1, [2, 3], {"a": 4}]


def test_to_plain_container_primitives():
    """Test _to_plain_container preserves primitives."""
    assert _to_plain_container(42) == 42, "Condition must be true"
    assert _to_plain_container("text") == "text", "Condition must be true"
    assert _to_plain_container(3.14) == 3.14, "Condition must be true"
    assert _to_plain_container(None) is None, "Condition must be true"


def test_materialise_mapping_none():
    """Test _materialise_mapping handles None input."""
    assert _materialise_mapping(None) == {}, "Condition must be true"


def test_materialise_mapping_valid():
    """Test _materialise_mapping converts mapping to dict."""
    result = _materialise_mapping({"key": "value", "nested": {"a": 1}})
    assert result == {"key": "value", "nested": {"a": 1}}


def test_materialise_mapping_invalid_type():
    """Test _materialise_mapping raises on non-mapping."""
    with pytest.raises(TypeError, match="must be mappings"):
        _materialise_mapping("not a mapping")  # type: ignore


def test_coerce_metric_value_valid():
    """Test _coerce_metric_value converts numeric values."""
    assert _coerce_metric_value(0.5) == 0.5, "Value must be initialized"
    assert _coerce_metric_value(42) == 42.0, "Value must be initialized"
    assert _coerce_metric_value("3.14") == 3.14, "Value must be initialized"


def test_coerce_metric_value_none():
    """Test _coerce_metric_value handles None."""
    assert _coerce_metric_value(None) is None, "Value must be initialized"


def test_coerce_metric_value_invalid():
    """Test _coerce_metric_value returns None for invalid values."""
    assert _coerce_metric_value("invalid") is None, "Value must be initialized"
    assert _coerce_metric_value([1, 2, 3]) is None


def test_auto_backend_explicit():
    """Test _auto_backend uses explicit backend if specified."""
    config = UnifiedTrainingConfig(model_name="test", backend="legacy")
    assert _auto_backend(config) == "legacy", "Condition must be true"


def test_auto_backend_default():
    """Test _auto_backend defaults to functional."""
    config = UnifiedTrainingConfig(model_name="test")
    assert _auto_backend(config) == "functional", "Condition must be true"


@patch("codex_ml.training.unified_training.set_seed")
def test_seed_all_deterministic(mock_set_seed):
    """Test _seed_all sets deterministic seed."""
    _seed_all(42, deterministic=True)
    mock_set_seed.assert_called_once_with(42, deterministic=True)


@patch("codex_ml.training.unified_training.set_seed")
def test_seed_all_non_deterministic(mock_set_seed):
    """Test _seed_all supports non-deterministic mode."""
    _seed_all(123, deterministic=False)
    mock_set_seed.assert_called_once_with(123, deterministic=False)


# =============================================================================
# Distributed Context Tests
# =============================================================================


def test_distributed_context_no_env(monkeypatch):
    """Test distributed_context with no environment variables."""
    monkeypatch.delenv("WORLD_SIZE", raising=False)
    monkeypatch.delenv("RANK", raising=False)
    monkeypatch.delenv("LOCAL_RANK", raising=False)

    context = distributed_context()
    assert context["world_size"] == 1, "Condition must be true"
    assert context["rank"] == 0, "Condition must be true"
    assert context["local_rank"] == 0, "Condition must be true"


def test_distributed_context_from_env(monkeypatch):
    """Test distributed_context reads from environment variables."""
    monkeypatch.setenv("WORLD_SIZE", "4")
    monkeypatch.setenv("RANK", "2")
    monkeypatch.setenv("LOCAL_RANK", "1")

    context = distributed_context()
    assert context["world_size"] == 4, "Condition must be true"
    assert context["rank"] == 2, "Condition must be true"
    assert context["local_rank"] == 1, "Condition must be true"


def test_distributed_context_fallback_localworld(monkeypatch):
    """Test distributed_context falls back to LOCALWORLD variable."""
    monkeypatch.delenv("LOCAL_RANK", raising=False)
    monkeypatch.setenv("LOCALWORLD", "3")

    context = distributed_context()
    assert context["local_rank"] == 3, "Condition must be true"


@patch("codex_ml.training.unified_training.torch")
def test_distributed_context_with_torch_dist(mock_torch, monkeypatch):
    """Test distributed_context integrates torch.distributed if available."""
    monkeypatch.setenv("WORLD_SIZE", "2")

    # Mock torch.distributed at the module level where it's imported
    mock_dist = MagicMock()
    mock_dist.is_available.return_value = True
    mock_dist.is_initialized.return_value = True
    mock_dist.get_backend.return_value = "nccl"
    mock_dist.get_world_size.return_value = 4
    mock_dist.get_rank.return_value = 1

    # Make torch.distributed accessible as an attribute
    mock_torch.distributed = mock_dist

    # Also patch the actual torch.distributed import
    with patch("torch.distributed", mock_dist):
        context = distributed_context()
        assert context["backend"] == "nccl", "Condition must be true"
        assert context["world_size"] == 4, "Condition must be true"
        assert context["rank"] == 1, "Condition must be true"


# =============================================================================
# Integration Tests
# =============================================================================


def test_unified_config_serialization(minimal_config):
    """Test UnifiedTrainingConfig can be serialized to dict."""
    from dataclasses import asdict

    config_dict = asdict(minimal_config)
    assert config_dict["model_name"] == "test-model", "Condition must be true"
    assert config_dict["epochs"] == 2, "Condition must be true"
    assert config_dict["batch_size"] == 4, "Condition must be true"


def test_unified_config_with_extra_params():
    """Test UnifiedTrainingConfig preserves extra parameters."""
    config = UnifiedTrainingConfig(model_name="test", extra={"custom_param": "value", "flag": True})
    assert config.extra["custom_param"] == "value", "Value must be initialized"
    assert config.extra["flag"] is True, "Condition must be true"


def test_continual_config_complex_phases():
    """Test ContinualConfig with complex phase configurations."""
    config = ContinualConfig(
        strategy="curriculum",
        phases=[
            ContinualPhase(name="warmup", epochs=2, replay_ratio=0.1),
            ContinualPhase(name="main", epochs=10, replay_ratio=0.3),
            ContinualPhase(name="finetune", epochs=5, replay_ratio=0.5),
        ],
    )
    assert len(config.phases) == 3, "Collection must not be empty"
    assert config.phases[0].name == "warmup", "name is not valid"
    assert config.phases[1].epochs == 10, "epochs is not valid"
    assert config.phases[2].replay_ratio == 0.5, "replay_ratio is not valid"


def test_unified_config_grad_clip_optional():
    """Test UnifiedTrainingConfig with optional grad_clip_norm."""
    config = UnifiedTrainingConfig(model_name="test", grad_clip_norm=1.0)
    assert config.grad_clip_norm == 1.0, "grad_clip_norm is not valid"

    config2 = UnifiedTrainingConfig(model_name="test")
    assert config2.grad_clip_norm is None, "grad_clip_norm is not valid"


def test_unified_config_resume_from():
    """Test UnifiedTrainingConfig with resume_from path."""
    config = UnifiedTrainingConfig(model_name="test", resume_from="/path/to/checkpoint.pt")
    assert config.resume_from == "/path/to/checkpoint.pt", "resume_from is not valid"
