"""
pytest.importorskip("mlflow")
Comprehensive test suite for codex_ml.training.strategies module.

This module provides 15+ tests targeting 70%+ coverage of strategies.py.
Tests cover strategy resolution, callback protocols, backend adapters,
and training result structures.

Phase: 2.1 - Core ML Training Coverage Initiative
Created: 2026-01-18
Target Coverage: 70%+
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from codex_ml.training.strategies import (
    FunctionalStrategy,
    LegacyStrategy,
    NoOpCallback,
    TrainingCallback,
    TrainingResult,
    _safe_callbacks,
    resolve_strategy,
)

# =============================================================================
# Test Data & Fixtures
# =============================================================================


@pytest.fixture
def mock_config():
    """Create a mock training configuration."""
    config = MagicMock()
    config.model_name = "test-model"
    config.epochs = 2
    config.batch_size = 4
    config.grad_accum = 1
    config.seed = 42
    config.output_dir = "test_output"
    config.mlflow_enable = False
    config.extra = {}
    return config


@pytest.fixture
def mock_callback():
    """Create a mock callback."""
    return MagicMock(spec=TrainingCallback)


@pytest.fixture
def noop_callback():
    """Create NoOpCallback instance."""
    return NoOpCallback()


# =============================================================================
# TrainingResult Tests
# =============================================================================


def test_training_result_initialization():
    """Test TrainingResult initialization."""
    result = TrainingResult(
        status="ok",
        backend="functional",
        final_epoch=5,
        output_dir="/output",
        extra={"metric": 0.95},
    )
    assert result.status == "ok", "Result must not be empty"
    assert result.backend == "functional", "Result must not be empty"
    assert result.final_epoch == 5, "Result must not be empty"
    assert result.output_dir == "/output", "Result must not be empty"
    assert result.extra["metric"] == 0.95, "Result must not be empty"


def test_training_result_empty_extra():
    """Test TrainingResult with empty extra dict."""
    result = TrainingResult(
        status="ok", backend="legacy", final_epoch=1, output_dir="/tmp", extra={}
    )
    assert result.extra == {}, "Result must not be empty"


def test_training_result_serialization():
    """Test TrainingResult can be serialized."""
    from dataclasses import asdict

    result = TrainingResult(
        status="ok", backend="functional", final_epoch=3, output_dir="/output", extra={"loss": 0.5}
    )
    result_dict = asdict(result)
    assert result_dict["status"] == "ok", "Result must not be empty"
    assert result_dict["extra"]["loss"] == 0.5, "Result must not be empty"


# =============================================================================
# NoOpCallback Tests
# =============================================================================


def test_noop_callback_epoch_start(noop_callback):
    """Test NoOpCallback.on_epoch_start does nothing."""
    # Should not raise
    noop_callback.on_epoch_start(1, {})


def test_noop_callback_epoch_end(noop_callback):
    """Test NoOpCallback.on_epoch_end does nothing."""
    # Should not raise
    noop_callback.on_epoch_end(1, {"loss": 0.5}, {})


def test_noop_callback_step(noop_callback):
    """Test NoOpCallback.on_step does nothing."""
    # Should not raise
    noop_callback.on_step(0, 0, 0.5, {})


def test_noop_callback_checkpoint(noop_callback):
    """Test NoOpCallback.on_checkpoint does nothing."""
    # Should not raise
    noop_callback.on_checkpoint(1, "/path", {"loss": 0.5}, {})


# =============================================================================
# Helper Function Tests
# =============================================================================


def test_safe_callbacks_with_callbacks():
    """Test _safe_callbacks preserves callback list."""
    cb1 = NoOpCallback()
    cb2 = NoOpCallback()

    result = _safe_callbacks([cb1, cb2])
    assert len(result) == 2, "Result must not be empty"
    assert result[0] is cb1, "Result must not be empty"
    assert result[1] is cb2, "Result must not be empty"


def test_safe_callbacks_empty_list():
    """Test _safe_callbacks returns NoOpCallback for empty list."""
    result = _safe_callbacks([])
    assert len(result) == 1, "Result must not be empty"
    assert isinstance(result[0], NoOpCallback)


def test_safe_callbacks_none():
    """Test _safe_callbacks handles None input."""
    result = _safe_callbacks(None)
    assert len(result) == 1, "Result must not be empty"
    assert isinstance(result[0], NoOpCallback)


# =============================================================================
# Strategy Resolution Tests
# =============================================================================


def test_resolve_strategy_functional():
    """Test resolve_strategy returns FunctionalStrategy."""
    strategy = resolve_strategy("functional")
    assert isinstance(strategy, FunctionalStrategy)
    assert strategy.backend_name == "functional", "backend_name is not valid"


def test_resolve_strategy_legacy():
    """Test resolve_strategy returns LegacyStrategy."""
    strategy = resolve_strategy("legacy")
    assert isinstance(strategy, LegacyStrategy)
    assert strategy.backend_name == "legacy", "backend_name is not valid"


def test_resolve_strategy_default():
    """Test resolve_strategy defaults to functional."""
    strategy = resolve_strategy(None)
    assert isinstance(strategy, FunctionalStrategy)


def test_resolve_strategy_unknown():
    """Test resolve_strategy handles unknown backend."""
    with pytest.raises(ValueError, match="Unknown backend"):
        resolve_strategy("unknown_backend")


def test_resolve_strategy_case_insensitive():
    """Test resolve_strategy is case insensitive."""
    strategy = resolve_strategy("FUNCTIONAL")
    assert isinstance(strategy, FunctionalStrategy)


# =============================================================================
# FunctionalStrategy Tests
# =============================================================================


@patch("codex_ml.training.strategies.import_module")
def test_functional_strategy_run_basic(mock_import, mock_config, mock_callback):
    """Test FunctionalStrategy.run basic execution."""
    # Mock functional_training module
    mock_module = MagicMock()
    mock_train_config = MagicMock()
    mock_module.TrainConfig = mock_train_config
    mock_module.train.return_value = {"loss": 0.5}
    mock_import.return_value = mock_module

    strategy = FunctionalStrategy()
    result = strategy.run(mock_config, [mock_callback])

    assert result.status == "ok", "Result must not be empty"
    assert result.backend == "functional", "Result must not be empty"
    assert result.final_epoch == mock_config.epochs, "Result must not be empty"


@patch("codex_ml.training.strategies.import_module")
def test_functional_strategy_with_texts(mock_import, mock_config):
    """Test FunctionalStrategy.run with training texts."""
    mock_config.extra = {"train_texts": ["text1", "text2"]}

    mock_module = MagicMock()
    mock_module.TrainConfig = MagicMock()
    mock_module.train.return_value = {"loss": 0.3}
    mock_import.return_value = mock_module

    strategy = FunctionalStrategy()
    result = strategy.run(mock_config, [])

    assert result.extra.get("trained") is True, "Result must not be empty"


@patch("codex_ml.training.strategies.import_module")
def test_functional_strategy_error_handling(mock_import, mock_config):
    """Test FunctionalStrategy.run handles errors gracefully."""
    mock_module = MagicMock()
    mock_module.TrainConfig = MagicMock()
    mock_module.train.side_effect = RuntimeError("Training failed")
    mock_import.return_value = mock_module

    mock_config.extra = {"train_texts": ["text"]}

    strategy = FunctionalStrategy()
    result = strategy.run(mock_config, [])

    assert result.status == "error", "Result must not be empty"
    assert "exception" in result.extra, "Result must not be empty"


# =============================================================================
# LegacyStrategy Tests
# =============================================================================


@patch("codex_ml.training.strategies.import_module")
@patch("codex_ml.training.strategies.warnings.warn")
def test_legacy_strategy_deprecation_warning(mock_warn, mock_import, mock_config):
    """Test LegacyStrategy emits deprecation warning."""
    mock_module = MagicMock()
    mock_import.return_value = mock_module

    strategy = LegacyStrategy()

    try:
        strategy.run(mock_config, [])
    except Exception as _err:
        _ = None  # We only care about the warning

    # Verify deprecation warning was called
    assert mock_warn.called, "Condition must be true"


@patch("codex_ml.training.strategies.import_module")
def test_legacy_strategy_run_basic(mock_import, mock_config):
    """Test LegacyStrategy.run basic execution."""
    # Mock legacy train_loop module
    mock_module = MagicMock()
    legacy_run = MagicMock()
    mock_module.run_training = legacy_run

    # Patch at the import location
    with patch("codex_ml.training.strategies.warnings.warn"):
        with patch("codex_ml.train_loop.run_training", legacy_run):
            strategy = LegacyStrategy()
            result = strategy.run(mock_config, [])

            assert result.status == "ok", "Result must not be empty"
            assert result.backend == "legacy", "Result must not be empty"


# =============================================================================
# Callback Protocol Tests
# =============================================================================


def test_callback_protocol_methods():
    """Test callback protocol defines expected methods."""

    # Create a custom callback implementing the protocol
    class CustomCallback:
        def on_epoch_start(self, epoch: int, state: dict[str, Any]) -> None:
            self.epoch_started = epoch

        def on_epoch_end(
            self, epoch: int, metrics: dict[str, float], state: dict[str, Any]
        ) -> None:
            self.epoch_ended = epoch

        def on_step(
            self, batch_index: int, global_step: int, loss: float, state: dict[str, Any]
        ) -> None:
            self.step_called = True

        def on_checkpoint(
            self, epoch: int, path: str, metrics: dict[str, float], state: dict[str, Any]
        ) -> None:
            self.checkpoint_saved = path

    callback = CustomCallback()
    callback.on_epoch_start(1, {})
    callback.on_epoch_end(1, {"loss": 0.5}, {})
    callback.on_step(0, 0, 0.5, {})
    callback.on_checkpoint(1, "/path", {"loss": 0.5}, {})

    assert callback.epoch_started == 1, "epoch_started is not valid"
    assert callback.epoch_ended == 1, "epoch_ended is not valid"
    assert callback.step_called is True, "step_called is not valid"
    assert callback.checkpoint_saved == "/path", "checkpoint_saved is not valid"


def test_mock_callback_integration(mock_callback, mock_config):
    """Test callback integration in strategy execution."""
    with patch("codex_ml.training.strategies.import_module") as mock_import:
        mock_module = MagicMock()
        mock_module.TrainConfig = MagicMock()
        mock_module.train.return_value = {}
        mock_import.return_value = mock_module

        strategy = FunctionalStrategy()
        strategy.run(mock_config, [mock_callback])

        # Verify callbacks were invoked
        assert mock_callback.on_epoch_start.called, "Condition must be true"


# =============================================================================
# Integration Tests
# =============================================================================


def test_strategy_result_consistency():
    """Test all strategies return consistent TrainingResult structure."""
    strategies = [
        ("functional", FunctionalStrategy()),
        ("legacy", LegacyStrategy()),
    ]

    for name, strategy in strategies:
        assert hasattr(strategy, "backend_name")
        assert strategy.backend_name == name, "backend_name is not valid"


def test_functional_strategy_resume_from(mock_config):
    """Test FunctionalStrategy.run with resume_from parameter."""
    with patch("codex_ml.training.strategies.import_module") as mock_import:
        mock_module = MagicMock()
        mock_module.TrainConfig = MagicMock()
        mock_module.train.return_value = {}
        mock_import.return_value = mock_module

        strategy = FunctionalStrategy()
        result = strategy.run(mock_config, [], resume_from="/checkpoint.pt")

        assert result.extra.get("resume_from") == "/checkpoint.pt", "Result must not be empty"


def test_backend_strategy_protocol_compliance():
    """Test strategies comply with BackendStrategy protocol."""
    strategies = [FunctionalStrategy(), LegacyStrategy()]

    for strategy in strategies:
        # Check required attributes
        assert hasattr(strategy, "backend_name")
        assert hasattr(strategy, "run")

        # Check method signature
        assert callable(strategy.run), "Condition must be true"
