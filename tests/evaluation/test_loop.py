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

        assert callable(evaluate_epoch), "Condition must be true"
        assert callable(run_evaluation), "Condition must be true"
        assert EvaluationConfig is not None, "EvaluationConfig must be initialized"
        assert EvaluationResult is not None, "EvaluationResult must be initialized"

    def test_evaluation_config_defaults(self):
        """Test EvaluationConfig default values."""
        from codex_ml.evaluation import EvaluationConfig

        config = EvaluationConfig()
        assert config.device == "cpu", "device is not valid"
        assert config.max_batches is None, "max_batches is not valid"
        assert config.seed is None, "seed is not valid"
        assert config.metrics is None, "metrics is not valid"
        assert config.system_metrics is False, "system_metrics is not valid"

    def test_evaluation_config_custom(self):
        """Test EvaluationConfig with custom values."""
        from codex_ml.evaluation import EvaluationConfig

        config = EvaluationConfig(
            device="cuda",
            max_batches=10,
            seed=42,
            system_metrics=True,
        )
        assert config.device == "cuda", "device is not valid"
        assert config.max_batches == 10, "max_batches is not valid"
        assert config.seed == 42, "seed is not valid"
        assert config.system_metrics is True, "system_metrics is not valid"

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
        assert d["loss"] == 0.5, "Condition must be true"
        assert d["count"] == 100, "Count must be greater than zero"
        assert d["metrics"] == {"accuracy": 0.9}, "Condition must be true"
        assert d["batches"] == 10, "Condition must be true"
        assert d["duration_sec"] == 1.234568, "Condition must be true"

    def test_safe_item_with_float(self):
        """_safe_item returns float for a plain float."""
        from codex_ml.evaluation.loop import _safe_item

        assert _safe_item(3.14) == 3.14, "Item must not be empty"

    def test_safe_item_with_item_method(self):
        """_safe_item calls .item() on tensor-like objects."""
        from codex_ml.evaluation.loop import _safe_item

        tensor_like = MagicMock()
        tensor_like.item.return_value = 2.718
        assert _safe_item(tensor_like) == 2.718, "Item must not be empty"


class TestEvaluationDeterminism:
    """Determinism tests for evaluation loop."""

    def test_eval_result_roundtrip(self):
        """EvalResult fields survive to_dict and back."""
        from codex_ml.evaluation.loop import EvalResult

        original = EvalResult(loss=0.1, count=50, metrics={}, batches=5, duration_sec=0.5)
        d = original.to_dict()
        assert d["loss"] == original.loss, "Condition must be true"
        assert d["count"] == original.count, "Count must be greater than zero"
        assert d["batches"] == original.batches, "Condition must be true"

    def test_evaluation_result_alias(self):
        """EvaluationResult is an alias for EvalResult."""
        from codex_ml.evaluation import EvalResult, EvaluationResult

        assert EvaluationResult is EvalResult, "Result must not be empty"


class TestEvaluationLogging:
    """Tests for logging integration."""

    def test_run_evaluation_is_evaluate_epoch(self):
        """run_evaluation is an alias for evaluate_epoch."""
        from codex_ml.evaluation import evaluate_epoch, run_evaluation

        assert run_evaluation is evaluate_epoch, "run_evaluation is not valid"


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

        assert CheckpointEntry is not None, "CheckpointEntry must be initialized"
        assert CheckpointIndex is not None, "CheckpointIndex must be initialized"
        assert callable(prune_checkpoints), "Condition must be true"
        assert callable(save_checkpoint_with_retention), "Condition must be true"

    def test_checkpoint_entry_creation(self):
        """Test CheckpointEntry dataclass."""
        from codex_ml.checkpointing.best_k_retention import CheckpointEntry

        entry = CheckpointEntry(
            path="checkpoint_1.pt",
            metric=0.5,
            step=100,
            created_at=1234567890.0,
        )
        assert entry.path == "checkpoint_1.pt", "path is not valid"
        assert entry.metric == 0.5, "metric is not valid"
        assert entry.step == 100, "step is not valid"
        assert entry.created_at == 1234567890.0, "created_at is not valid"
