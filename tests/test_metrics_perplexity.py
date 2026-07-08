"""
Test Metrics Perplexity

Test module for metrics perplexity.
"""

import math
from types import SimpleNamespace

import pytest

# Skip entire module if torch is not available or unloadable
pytest.importorskip("torch", reason="PyTorch required for tests")
from codex_ml.metrics.evaluator import batch_metrics

try:  # pragma: no cover - torch optional in CI
    import torch
except ImportError:  # pragma: no cover - skip when torch unavailable
    torch = None  # type: ignore[assignment]

pytestmark = pytest.mark.skipif(torch is None, reason="requires PyTorch")


def test_batch_metrics_includes_perplexity_from_loss() -> None:
    loss_tensor = torch.tensor(0.5)
    outputs = SimpleNamespace(loss=loss_tensor)

    metrics = batch_metrics(outputs, {})

    assert metrics["loss"] == pytest.approx(0.5), "Condition must be true"
    assert metrics["perplexity"] == pytest.approx(math.exp(0.5)), "Condition must be true"
