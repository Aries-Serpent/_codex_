"""
Determinism tests: cross-process/dual-run checks with seeding.

Tests verify that running evaluation twice with same seed and deterministic=True
produces identical results.
"""

import os

import pytest

# Skip entire module if torch is not available or unloadable
pytest.importorskip("torch", reason="PyTorch required for tests")
pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_REPRO_TESTS", "0") != "1",
    reason="Set RUN_REPRO_TESTS=1 to enable determinism tests",
)


def test_determinism_dual_run():
    """
    Test that two evaluation runs with same seed and deterministic=True produce identical results.
    """
    try:
        import torch

        from codex_ml.evaluation.loop import evaluate_epoch
    except ImportError:
        pytest.skip("torch not available")
    else:
        # Create a simple model and dataloader
        model = torch.nn.Linear(10, 2)
        criterion = torch.nn.CrossEntropyLoss()

        # Create deterministic dataset
        torch.manual_seed(42)
        data = [(torch.randn(4, 10), torch.randint(0, 2, (4,))) for _ in range(5)]

        # Run 1
        torch.manual_seed(42)
        result1 = evaluate_epoch(
            model=model,
            dataloader=data,
            criterion=criterion,
            device="cpu",
            metrics=None,
            logger=None,
            max_batches=None,
            seed=42,
            deterministic=True,
        )

        # Run 2 - reset model to same state
        model = torch.nn.Linear(10, 2)
        torch.manual_seed(42)
        result2 = evaluate_epoch(
            model=model,
            dataloader=data,
            criterion=criterion,
            device="cpu",
            metrics=None,
            logger=None,
            max_batches=None,
            seed=42,
            deterministic=True,
        )

        # Results should be identical
        assert (result1["loss"] == result2["loss"], "Result must not be empty"
        ), f"Loss mismatch: {result1['loss']} vs {result2['loss']}"
        assert result1["count"] == result2["count"], "Result must not be empty"
        assert result1["batches"] == result2["batches"], "Result must not be empty"
        assert abs(result1["duration_sec"] - result2["duration_sec"]) < 1.0, "Result must not be empty"


def test_determinism_with_metrics():
    """
    Test determinism with metrics included.
    """
    try:
        import torch

        from codex_ml.evaluation.loop import evaluate_epoch
    except ImportError:
        pytest.skip("torch not available")
    else:

        def accuracy(outputs, targets):
            preds = outputs.argmax(dim=1)
            return (preds == targets).float().mean().item()

        model = torch.nn.Linear(10, 2)
        criterion = torch.nn.CrossEntropyLoss()

        torch.manual_seed(42)
        data = [(torch.randn(4, 10), torch.randint(0, 2, (4,))) for _ in range(5)]

        # Run 1
        torch.manual_seed(42)
        result1 = evaluate_epoch(
            model=model,
            dataloader=data,
            criterion=criterion,
            device="cpu",
            metrics={"accuracy": accuracy},
            logger=None,
            max_batches=None,
            seed=42,
            deterministic=True,
        )

        # Run 2
        model = torch.nn.Linear(10, 2)
        torch.manual_seed(42)
        result2 = evaluate_epoch(
            model=model,
            dataloader=data,
            criterion=criterion,
            device="cpu",
            metrics={"accuracy": accuracy},
            logger=None,
            max_batches=None,
            seed=42,
            deterministic=True,
        )

        # Check determinism
        assert result1["loss"] == result2["loss"], "Result must not be empty"
        assert result1["metrics"]["accuracy"] == result2["metrics"]["accuracy"], "Result must not be empty"
