"""
Comprehensive test suite for codex_ml.training.early_stopping module.

This module provides 10+ tests targeting 70%+ coverage of early_stopping.py.
Tests cover early stopping configuration, callback injection, patience logic,
and HuggingFace integration.

Phase: 2.1 - Core ML Training Coverage Initiative
Created: 2026-01-18
Target Coverage: 70%+
"""

from __future__ import annotations

from typing import Any, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from codex_ml.training.early_stopping import (
    CodexEarlyStoppingCallback,
    EarlyStoppingConfig,
    auto_inject_early_stopping_for_trainer,
    inject_early_stopping,
)


# =============================================================================
# Test Data & Fixtures
# =============================================================================


@pytest.fixture
def mock_eval_dataset():
    """Create a mock evaluation dataset."""
    dataset = MagicMock()
    dataset.__len__ = Mock(return_value=100)
    return dataset


@pytest.fixture
def mock_hf_callback():
    """Mock HuggingFace EarlyStoppingCallback."""
    with patch("codex_ml.training.early_stopping.EarlyStoppingCallback") as mock:
        yield mock


# =============================================================================
# EarlyStoppingConfig Tests
# =============================================================================


def test_early_stopping_config_default():
    """Test EarlyStoppingConfig default values."""
    config = EarlyStoppingConfig()
    assert config.patience == 3
    assert config.threshold == 0.0
    assert config.metric == "eval_loss"
    assert config.mode == "min"


def test_early_stopping_config_custom():
    """Test EarlyStoppingConfig with custom values."""
    config = EarlyStoppingConfig(
        patience=5,
        threshold=0.001,
        metric="eval_accuracy",
        mode="max"
    )
    assert config.patience == 5
    assert config.threshold == 0.001
    assert config.metric == "eval_accuracy"
    assert config.mode == "max"


def test_early_stopping_config_to_dict():
    """Test EarlyStoppingConfig.to_dict serialization."""
    config = EarlyStoppingConfig(patience=10, metric="eval_f1")
    config_dict = config.to_dict()
    
    assert config_dict["patience"] == 10
    assert config_dict["metric"] == "eval_f1"
    assert config_dict["threshold"] == 0.0
    assert config_dict["mode"] == "min"


def test_early_stopping_config_all_metrics():
    """Test EarlyStoppingConfig with various metrics."""
    metrics = ["eval_loss", "eval_accuracy", "eval_f1", "eval_precision"]
    for metric in metrics:
        config = EarlyStoppingConfig(metric=metric)
        assert config.metric == metric


def test_early_stopping_config_modes():
    """Test EarlyStoppingConfig with both min and max modes."""
    config_min = EarlyStoppingConfig(mode="min")
    config_max = EarlyStoppingConfig(mode="max")
    
    assert config_min.mode == "min"
    assert config_max.mode == "max"


# =============================================================================
# CodexEarlyStoppingCallback Tests
# =============================================================================


def test_codex_early_stopping_callback_default():
    """Test CodexEarlyStoppingCallback with default config."""
    callback = CodexEarlyStoppingCallback()
    assert callback.config is not None
    assert callback.config.patience == 3


def test_codex_early_stopping_callback_with_config():
    """Test CodexEarlyStoppingCallback with custom config."""
    config = EarlyStoppingConfig(patience=7, threshold=0.01)
    callback = CodexEarlyStoppingCallback(config=config)
    
    assert callback.config.patience == 7
    assert callback.config.threshold == 0.01


def test_codex_early_stopping_callback_override_patience():
    """Test CodexEarlyStoppingCallback overrides patience parameter."""
    config = EarlyStoppingConfig(patience=3)
    callback = CodexEarlyStoppingCallback(config=config, early_stopping_patience=10)
    
    assert callback.config.patience == 10


def test_codex_early_stopping_callback_override_threshold():
    """Test CodexEarlyStoppingCallback overrides threshold parameter."""
    config = EarlyStoppingConfig(threshold=0.0)
    callback = CodexEarlyStoppingCallback(config=config, early_stopping_threshold=0.005)
    
    assert callback.config.threshold == 0.005


@patch("codex_ml.training.early_stopping.EarlyStoppingCallback")
def test_codex_callback_uses_hf_callback(mock_hf_callback):
    """Test CodexEarlyStoppingCallback wraps HF callback when available."""
    mock_instance = MagicMock()
    mock_hf_callback.return_value = mock_instance
    
    callback = CodexEarlyStoppingCallback()
    assert callback.is_hf_callback is True
    assert callback.callback is mock_instance


def test_codex_callback_fallback_without_hf():
    """Test CodexEarlyStoppingCallback fallback without transformers."""
    with patch("codex_ml.training.early_stopping.EarlyStoppingCallback", side_effect=ImportError):
        callback = CodexEarlyStoppingCallback()
        assert callback.is_hf_callback is False
        assert callback.best_metric is None
        assert callback.patience_counter == 0


def test_codex_callback_getattr_delegation():
    """Test CodexEarlyStoppingCallback delegates to HF callback."""
    with patch("codex_ml.training.early_stopping.EarlyStoppingCallback") as mock_hf:
        mock_instance = MagicMock()
        mock_instance.some_method = Mock(return_value=42)
        mock_hf.return_value = mock_instance
        
        callback = CodexEarlyStoppingCallback()
        result = callback.some_method()
        
        assert result == 42


# =============================================================================
# inject_early_stopping Tests
# =============================================================================


def test_inject_early_stopping_empty_list():
    """Test inject_early_stopping adds callback to empty list."""
    callbacks = []
    result = inject_early_stopping(callbacks)
    
    assert len(result) == 1
    assert isinstance(result[0], CodexEarlyStoppingCallback)


def test_inject_early_stopping_with_config():
    """Test inject_early_stopping uses provided config."""
    config = EarlyStoppingConfig(patience=15)
    callbacks = []
    result = inject_early_stopping(callbacks, config=config)
    
    assert result[0].config.patience == 15


def test_inject_early_stopping_already_present():
    """Test inject_early_stopping skips if already present."""
    existing_callback = CodexEarlyStoppingCallback()
    callbacks = [existing_callback]
    
    result = inject_early_stopping(callbacks)
    
    # Should not add another one
    assert len(result) == 1


@patch("codex_ml.training.early_stopping.EarlyStoppingCallback")
def test_inject_early_stopping_detects_hf_callback(mock_hf_callback):
    """Test inject_early_stopping detects HuggingFace callback."""
    mock_instance = mock_hf_callback.return_value
    callbacks = [mock_instance]
    
    result = inject_early_stopping(callbacks)
    
    # Should detect existing callback
    assert len(result) == 1


def test_inject_early_stopping_force_flag():
    """Test inject_early_stopping with force=True adds even if present."""
    existing_callback = CodexEarlyStoppingCallback()
    callbacks = [existing_callback]
    
    result = inject_early_stopping(callbacks, force=True)
    
    # Should add another one due to force=True
    assert len(result) == 2


def test_inject_early_stopping_preserves_other_callbacks():
    """Test inject_early_stopping preserves existing callbacks."""
    other_callback1 = MagicMock()
    other_callback2 = MagicMock()
    callbacks = [other_callback1, other_callback2]
    
    result = inject_early_stopping(callbacks)
    
    assert len(result) == 3
    assert other_callback1 in result
    assert other_callback2 in result


# =============================================================================
# auto_inject_early_stopping_for_trainer Tests
# =============================================================================


def test_auto_inject_with_eval_dataset(mock_eval_dataset):
    """Test auto_inject_early_stopping_for_trainer with eval dataset."""
    callbacks = []
    result = auto_inject_early_stopping_for_trainer(
        trainer_class="Trainer",
        eval_dataset=mock_eval_dataset,
        callbacks=callbacks
    )
    
    assert len(result) == 1
    assert isinstance(result[0], CodexEarlyStoppingCallback)


def test_auto_inject_without_eval_dataset():
    """Test auto_inject_early_stopping_for_trainer without eval dataset."""
    callbacks = []
    result = auto_inject_early_stopping_for_trainer(
        trainer_class="Trainer",
        eval_dataset=None,
        callbacks=callbacks
    )
    
    # Should not inject if no eval dataset
    assert len(result) == 0


def test_auto_inject_with_none_callbacks(mock_eval_dataset):
    """Test auto_inject_early_stopping_for_trainer with None callbacks."""
    result = auto_inject_early_stopping_for_trainer(
        trainer_class="Trainer",
        eval_dataset=mock_eval_dataset,
        callbacks=None
    )
    
    assert len(result) == 1


def test_auto_inject_with_custom_config(mock_eval_dataset):
    """Test auto_inject_early_stopping_for_trainer with custom config."""
    config = EarlyStoppingConfig(patience=20, metric="eval_accuracy")
    result = auto_inject_early_stopping_for_trainer(
        trainer_class="Trainer",
        eval_dataset=mock_eval_dataset,
        callbacks=[],
        config=config
    )
    
    assert result[0].config.patience == 20
    assert result[0].config.metric == "eval_accuracy"


def test_auto_inject_preserves_existing_callbacks(mock_eval_dataset):
    """Test auto_inject_early_stopping_for_trainer preserves callbacks."""
    existing = MagicMock()
    callbacks = [existing]
    
    result = auto_inject_early_stopping_for_trainer(
        trainer_class="Trainer",
        eval_dataset=mock_eval_dataset,
        callbacks=callbacks
    )
    
    assert existing in result
    assert len(result) == 2


# =============================================================================
# Integration Tests
# =============================================================================


def test_early_stopping_config_validation():
    """Test EarlyStoppingConfig accepts valid configurations."""
    configs = [
        EarlyStoppingConfig(patience=1),
        EarlyStoppingConfig(patience=100),
        EarlyStoppingConfig(threshold=0.0),
        EarlyStoppingConfig(threshold=1.0),
    ]
    
    for config in configs:
        assert config.patience >= 1 or config.patience == configs[0].patience


def test_callback_chain_integration(mock_eval_dataset):
    """Test full callback injection chain."""
    # Start with empty callbacks
    callbacks = []
    
    # Auto-inject for trainer
    callbacks = auto_inject_early_stopping_for_trainer(
        trainer_class="Trainer",
        eval_dataset=mock_eval_dataset,
        callbacks=callbacks,
        config=EarlyStoppingConfig(patience=5)
    )
    
    assert len(callbacks) == 1
    assert callbacks[0].config.patience == 5


def test_multiple_injection_attempts():
    """Test multiple injection attempts don't duplicate."""
    callbacks = []
    
    # First injection
    callbacks = inject_early_stopping(callbacks)
    assert len(callbacks) == 1
    
    # Second injection (should skip)
    callbacks = inject_early_stopping(callbacks)
    assert len(callbacks) == 1
    
    # Third injection with force
    callbacks = inject_early_stopping(callbacks, force=True)
    assert len(callbacks) == 2


def test_early_stopping_config_serialization_round_trip():
    """Test EarlyStoppingConfig serialization round-trip."""
    original = EarlyStoppingConfig(
        patience=12,
        threshold=0.002,
        metric="eval_bleu",
        mode="max"
    )
    
    config_dict = original.to_dict()
    restored = EarlyStoppingConfig(**config_dict)
    
    assert restored.patience == original.patience
    assert restored.threshold == original.threshold
    assert restored.metric == original.metric
    assert restored.mode == original.mode
