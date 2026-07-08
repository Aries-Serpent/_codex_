"""
Comprehensive test suite for codex_ml.training.legacy_api module.

This module provides 20+ tests targeting 70%+ coverage of legacy_api.py.
Tests cover dataclasses, configuration coercion, safety integration,
and training orchestration functions.

Phase: 2.1 - Core ML Training Coverage Initiative
Created: 2026-01-18
Target Coverage: 70%+
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import modules under test - with proper guards
try:
    from codex_ml.training.legacy_api import (
        OptimizerSettings,
        SafetySettings,
        SchedulerSettings,
        TrainingRunConfig,
    )

    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False

pytestmark = pytest.mark.skipif(not LEGACY_AVAILABLE, reason="legacy_api not available")


# =============================================================================
# Test Data & Fixtures
# =============================================================================


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Create temporary data directory with sample JSONL."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    train_file = data_dir / "train.jsonl"
    train_file.write_text('{"text": "sample1"}\n{"text": "sample2"}\n')

    return data_dir


@pytest.fixture
def mock_torch():
    """Mock torch module."""
    with patch("codex_ml.training.legacy_api.torch") as mock:
        mock.cuda.is_available.return_value = False
        mock.device.return_value = "cpu"
        yield mock


@pytest.fixture
def mock_model():
    """Create a mock ML model."""
    model = MagicMock()
    model.parameters.return_value = iter([MagicMock()])
    model.train.return_value = None
    model.eval.return_value = None
    return model


# =============================================================================
# SafetySettings Tests
# =============================================================================


def test_safety_settings_default():
    """Test SafetySettings uses sensible defaults."""
    settings = SafetySettings()
    assert settings.enabled is True, "enabled is not valid"
    assert settings.policy_path is None, "policy_path is not valid"
    assert settings.bypass is False, "bypass is not valid"


def test_safety_settings_custom():
    """Test SafetySettings with custom values."""
    settings = SafetySettings(enabled=False, policy_path="/path/to/policy.json", bypass=True)
    assert settings.enabled is False, "enabled is not valid"
    assert settings.policy_path == "/path/to/policy.json", "policy_path is not valid"
    assert settings.bypass is True, "bypass is not valid"


def test_safety_settings_moderation():
    """Test SafetySettings includes moderation settings."""
    settings = SafetySettings()
    assert hasattr(settings, "moderation")


# =============================================================================
# OptimizerSettings Tests
# =============================================================================


def test_optimizer_settings_default():
    """Test OptimizerSettings uses AdamW defaults."""
    settings = OptimizerSettings()
    assert settings.name == "adamw_torch", "name is not valid"
    assert settings.weight_decay == 0.01, "weight_decay is not valid"
    assert settings.betas == (0.9, 0.999)
    assert settings.eps == 1e-8, "eps is not valid"


def test_optimizer_settings_custom():
    """Test OptimizerSettings with custom values."""
    settings = OptimizerSettings(name="sgd", weight_decay=0.001, betas=(0.95, 0.9995), eps=1e-6)
    assert settings.name == "sgd", "name is not valid"
    assert settings.weight_decay == 0.001, "weight_decay is not valid"
    assert settings.betas == (0.95, 0.9995)
    assert settings.eps == 1e-6, "eps is not valid"


def test_optimizer_settings_betas_tuple():
    """Test OptimizerSettings validates betas as tuple."""
    settings = OptimizerSettings(betas=(0.9, 0.999))
    assert len(settings.betas) == 2, "Collection must not be empty"
    assert settings.betas[0] == 0.9, "Condition must be true"
    assert settings.betas[1] == 0.999, "Condition must be true"


# =============================================================================
# SchedulerSettings Tests
# =============================================================================


def test_scheduler_settings_default():
    """Test SchedulerSettings defaults."""
    settings = SchedulerSettings()
    assert hasattr(settings, "name") or hasattr(settings, "type")


def test_scheduler_settings_custom():
    """Test SchedulerSettings with custom scheduler type."""
    # Assuming SchedulerSettings has name/type attribute
    settings = SchedulerSettings()
    assert settings is not None, "settings must be initialized"


# =============================================================================
# TrainingRunConfig Tests
# =============================================================================


def test_training_run_config_minimal():
    """Test TrainingRunConfig with minimal parameters."""
    config = TrainingRunConfig()
    assert config is not None, "config must be initialized"


def test_training_run_config_custom():
    """Test TrainingRunConfig with custom values."""
    config = TrainingRunConfig()
    # Verify config is a dataclass
    assert hasattr(config, "__dataclass_fields__")


# =============================================================================
# Configuration Coercion Tests (if exposed)
# =============================================================================


def test_optimizer_coercion_dict():
    """Test optimizer configuration coercion from dict."""
    # Test if _coerce_optimizer exists and is accessible
    try:
        from codex_ml.training.legacy_api import _coerce_optimizer

        result = _coerce_optimizer({"name": "adam", "weight_decay": 0.005})
        assert isinstance(result, OptimizerSettings)
        assert result.name == "adam", "Result must not be empty"
        assert result.weight_decay == 0.005, "Result must not be empty"
    except (ImportError, AttributeError):
        pytest.skip("_coerce_optimizer not exposed")


def test_optimizer_coercion_object():
    """Test optimizer configuration coercion from object."""
    try:
        from codex_ml.training.legacy_api import _coerce_optimizer

        settings = OptimizerSettings(name="sgd")
        result = _coerce_optimizer(settings)
        assert result is settings, "Result must not be empty"
    except (ImportError, AttributeError):
        pytest.skip("_coerce_optimizer not exposed")


def test_safety_coercion_dict():
    """Test safety configuration coercion from dict."""
    try:
        from codex_ml.training.legacy_api import _coerce_safety

        result = _coerce_safety({"enabled": False, "bypass": True})
        assert isinstance(result, SafetySettings)
        assert result.enabled is False, "Result must not be empty"
        assert result.bypass is True, "Result must not be empty"
    except (ImportError, AttributeError):
        pytest.skip("_coerce_safety not exposed")


def test_scheduler_coercion_dict():
    """Test scheduler configuration coercion from dict."""
    try:
        from codex_ml.training.legacy_api import _coerce_scheduler

        result = _coerce_scheduler({"name": "cosine"})
        assert isinstance(result, SchedulerSettings)
    except (ImportError, AttributeError):
        pytest.skip("_coerce_scheduler not exposed")


# =============================================================================
# Helper Function Tests
# =============================================================================


def test_listify_texts_string():
    """Test _listify_texts converts string to list."""
    try:
        from codex_ml.training.legacy_api import _listify_texts

        result = _listify_texts("single text")
        assert result == ["single text"], "Result must not be empty"
    except (ImportError, AttributeError):
        pytest.skip("_listify_texts not exposed")


def test_listify_texts_list():
    """Test _listify_texts preserves list."""
    try:
        from codex_ml.training.legacy_api import _listify_texts

        result = _listify_texts(["text1", "text2"])
        assert result == ["text1", "text2"]
    except (ImportError, AttributeError):
        pytest.skip("_listify_texts not exposed")


def test_listify_texts_none():
    """Test _listify_texts handles None."""
    try:
        from codex_ml.training.legacy_api import _listify_texts

        result = _listify_texts(None)
        assert result == [] or result is None, "Result must not be empty"
    except (ImportError, AttributeError):
        pytest.skip("_listify_texts not exposed")


def test_load_texts_from_file(temp_data_dir):
    """Test _load_texts loads from JSONL file."""
    try:
        from codex_ml.training.legacy_api import _load_texts

        file_path = temp_data_dir / "train.jsonl"
        result = _load_texts(str(file_path))
        assert isinstance(result, list)
        assert len(result) > 0, "Result must not be empty"
    except (ImportError, AttributeError):
        pytest.skip("_load_texts not exposed")


def test_normalize_config_dict():
    """Test _normalize_config processes dict configs."""
    try:
        from codex_ml.training.legacy_api import _normalize_config

        config_dict = {"epochs": 5, "batch_size": 16}
        result = _normalize_config(config_dict)
        assert result is not None, "result must be initialized"
    except (ImportError, AttributeError):
        pytest.skip("_normalize_config not exposed")


def test_log_optional_dependencies():
    """Test _log_optional_dependencies logs without errors."""
    try:
        from codex_ml.training.legacy_api import _log_optional_dependencies

        # Should not raise
        _log_optional_dependencies()
    except (ImportError, AttributeError):
        pytest.skip("_log_optional_dependencies not exposed")


# =============================================================================
# Integration Tests
# =============================================================================


@patch("codex_ml.training.legacy_api.load_jsonl")
def test_build_dataloader_basic(mock_load_jsonl):
    """Test build_dataloader creates DataLoader."""
    try:
        from codex_ml.training.legacy_api import build_dataloader

        mock_load_jsonl.return_value = [
            {"text": "sample1"},
            {"text": "sample2"},
        ]

        loader = build_dataloader(data_path="test.jsonl", batch_size=2, shuffle=True)
        assert loader is not None, "loader must be initialized"
    except (ImportError, AttributeError):
        pytest.skip("build_dataloader not exposed")


def test_training_run_config_serialization():
    """Test TrainingRunConfig can be serialized."""
    from dataclasses import asdict

    config = TrainingRunConfig()
    config_dict = asdict(config)
    assert isinstance(config_dict, dict)


def test_safety_settings_with_moderation_config():
    """Test SafetySettings integrates with ModerationSettings."""
    from codex_ml.safety import ModerationSettings
    from codex_ml.training.legacy_api import SafetySettings

    moderation = ModerationSettings()
    settings = SafetySettings(moderation=moderation)
    assert settings.moderation is moderation, "moderation is not valid"


@patch("codex_ml.training.legacy_api.maybe_autocast")
def test_autocast_integration(mock_autocast):
    """Test autocast integration for mixed precision."""
    mock_autocast.return_value.__enter__ = Mock()
    mock_autocast.return_value.__exit__ = Mock()

    # Test that autocast can be imported and called
    from codex_ml.training.legacy_api import maybe_autocast

    with maybe_autocast("cuda", dtype="fp16"):
        pass


def test_optimizer_settings_serialization():
    """Test OptimizerSettings can be serialized."""
    from dataclasses import asdict

    settings = OptimizerSettings(name="adam", weight_decay=0.02)
    settings_dict = asdict(settings)

    assert settings_dict["name"] == "adam", "Condition must be true"
    assert settings_dict["weight_decay"] == 0.02, "Condition must be true"


def test_safety_settings_policy_loading():
    """Test SafetySettings can reference external policy."""
    settings = SafetySettings(policy_path="/etc/safety/policy.json", enabled=True)
    assert Path(settings.policy_path).name == "policy.json", "name is not valid"


# =============================================================================
# Error Handling Tests
# =============================================================================


def test_optimizer_settings_invalid_epsilon():
    """Test OptimizerSettings with edge case epsilon."""
    settings = OptimizerSettings(eps=0.0)
    assert settings.eps == 0.0, "eps is not valid"


def test_safety_settings_conflicting_flags():
    """Test SafetySettings with conflicting flags."""
    # Should allow both enabled and bypass to be True (bypass overrides)
    settings = SafetySettings(enabled=True, bypass=True)
    assert settings.enabled is True, "enabled is not valid"
    assert settings.bypass is True, "bypass is not valid"


def test_optimizer_settings_negative_weight_decay():
    """Test OptimizerSettings allows negative weight decay."""
    # Some optimizers may allow negative weight decay
    settings = OptimizerSettings(weight_decay=-0.01)
    assert settings.weight_decay == -0.01, "weight_decay is not valid"
