"""
Tests for evaluation loop module.

Covers basic functionality and edge cases per Coverage_96-99 spec.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestEvaluationLoopBasics:
    """Basic evaluation loop tests."""

    def test_import_evaluation_module(self):
        """Test that evaluation module can be imported."""
        from codex_ml.evaluation import (
            EvaluationConfig,
            EvaluationResult,
            evaluate_epoch,
            run_evaluation,
        )

        assert callable(evaluate_epoch)
        assert callable(run_evaluation)
        assert EvaluationConfig is not None
        assert EvaluationResult is not None

    def test_evaluation_config_defaults(self):
        """Test EvaluationConfig default values."""
        from codex_ml.evaluation import EvaluationConfig

        config = EvaluationConfig()
        assert config.device == "cpu"
        assert config.max_batches is None
        assert config.seed is None
        assert config.metrics is None
        assert config.system_metrics is False

    def test_evaluation_config_custom(self):
        """Test EvaluationConfig with custom values."""
        from codex_ml.evaluation import EvaluationConfig

        config = EvaluationConfig(
            device="cuda",
            max_batches=10,
            seed=42,
            system_metrics=True,
        )
        assert config.device == "cuda"
        assert config.max_batches == 10
        assert config.seed == 42
        assert config.system_metrics is True

    def test_protocol_interfaces_defined(self):
        """Test that Protocol interfaces are properly defined."""
        from codex_ml.evaluation import Criterion, Logger

        # Protocols should be importable and have expected methods
        assert hasattr(Criterion, "__call__")
        assert hasattr(Logger, "log")
        assert hasattr(Logger, "close")


class TestEvaluationLoopEdgeCases:
    """Edge case tests for evaluation loop."""

    def test_evaluate_epoch_raises_without_torch(self):
        """evaluate_epoch raises RuntimeError when torch is None."""
        from codex_ml.evaluation import evaluate_epoch

        with patch("codex_ml.evaluation.loop.torch", None):
            with pytest.raises(RuntimeError, match="Torch not available"):
                evaluate_epoch(
                    model=MagicMock(),
                    dataloader=[],
                    criterion=MagicMock(),
                )

    def test_eval_result_to_dict(self):
        """EvalResult.to_dict() returns expected structure."""
        from codex_ml.evaluation.loop import EvalResult

        result = EvalResult(
            loss=0.5,
            count=100,
            metrics={"accuracy": 0.9},
            batches=10,
            duration_sec=1.23456789,
        )
        d = result.to_dict()
        assert d["loss"] == 0.5
        assert d["count"] == 100
        assert d["metrics"] == {"accuracy": 0.9}
        assert d["batches"] == 10
        assert d["duration_sec"] == 1.234568  # rounded to 6 decimal places

    def test_safe_item_with_float(self):
        """_safe_item returns float for a plain float."""
        from codex_ml.evaluation.loop import _safe_item

        assert _safe_item(3.14) == 3.14

    def test_safe_item_with_item_method(self):
        """_safe_item calls .item() on tensor-like objects."""
        from codex_ml.evaluation.loop import _safe_item

        tensor_like = MagicMock()
        tensor_like.item.return_value = 2.718
        assert _safe_item(tensor_like) == 2.718


class TestEvaluationDeterminism:
    """Determinism tests for evaluation loop."""

    def test_eval_result_roundtrip(self):
        """EvalResult fields survive to_dict and back."""
        from codex_ml.evaluation.loop import EvalResult

        original = EvalResult(loss=0.1, count=50, metrics={}, batches=5, duration_sec=0.5)
        d = original.to_dict()
        assert d["loss"] == original.loss
        assert d["count"] == original.count
        assert d["batches"] == original.batches

    def test_evaluation_result_alias(self):
        """EvaluationResult is an alias for EvalResult."""
        from codex_ml.evaluation import EvalResult, EvaluationResult

        assert EvaluationResult is EvalResult


class TestEvaluationLogging:
    """Tests for logging integration."""

    def test_run_evaluation_is_evaluate_epoch(self):
        """run_evaluation is an alias for evaluate_epoch."""
        from codex_ml.evaluation import evaluate_epoch, run_evaluation

        assert run_evaluation is evaluate_epoch


class TestCheckpointRetention:
    """Tests for checkpoint best-k retention."""

    def test_import_checkpoint_module(self):
        """Test that checkpoint retention module can be imported."""
        from codex_ml.checkpointing.best_k_retention import (
            CheckpointEntry,
            CheckpointIndex,
            prune_checkpoints,
            save_checkpoint_with_retention,
        )

        assert CheckpointEntry is not None
        assert CheckpointIndex is not None
        assert callable(prune_checkpoints)
        assert callable(save_checkpoint_with_retention)

    def test_checkpoint_entry_creation(self):
        """Test CheckpointEntry dataclass."""
        from codex_ml.checkpointing.best_k_retention import CheckpointEntry

        entry = CheckpointEntry(
            path="checkpoint_1.pt",
            metric=0.5,
            step=100,
            created_at=1234567890.0,
        )
        assert entry.path == "checkpoint_1.pt"
        assert entry.metric == 0.5
        assert entry.step == 100
        assert entry.created_at == 1234567890.0
