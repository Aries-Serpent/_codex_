"""
Test Metrics

Test module for metrics.
"""

from __future__ import annotations

import importlib.util

import pytest


def _has_module(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


def _require_metrics_module():
    if not _has_module("torch"):
        pytest.skip("torch is required for metrics tests")
    if not _has_module("torch.nn.functional"):
        pytest.skip("torch.nn.functional is required for metrics tests")

    torch = None  # ensure variable is always bound before use
    try:
        import torch
    except Exception as exc:  # pragma: no cover - optional dependency guard
        pytest.skip(f"torch import failed: {exc!r}")

    if getattr(torch, "IS_CODEX_STUB", False):
        pytest.skip("torch stub lacks the real tensor/dtype APIs required for metrics tests")

    if not hasattr(torch, "tensor"):
        pytest.skip("torch installation lacks tensor APIs required for metrics tests")

    try:
        from codex_ml.utils.torch_checks import inspect_torch
    except ImportError:  # pragma: no cover - best effort guard
        inspect_torch = None  # type: ignore[assignment]
    else:
        status = inspect_torch(torch)
        if not status.ok:
            reinstall_hint = status.reinstall_hint
            detail = status.detail
            if reinstall_hint:
                detail = f"{detail}. Reinstall via: {reinstall_hint}"
            pytest.skip(f"torch installation incomplete: {detail}")

    from src.evaluation import metrics as metrics_module

    return torch, metrics_module


def test_precision_recall_f1_perfect_predictions() -> None:
    torch, metrics_module = _require_metrics_module()

    logits = torch.tensor([[4.0, 0.1], [0.1, 3.9]], dtype=torch.float32)
    targets = torch.tensor([0, 1], dtype=torch.long)

    precision, recall, f1 = metrics_module.precision_recall_f1(logits, targets)

    assert precision == pytest.approx(1.0)
    assert recall == pytest.approx(1.0)
    assert f1 == pytest.approx(1.0)


def test_precision_recall_f1_handles_missing_predictions() -> None:
    torch, metrics_module = _require_metrics_module()

    logits = torch.tensor([[3.0, 0.1], [3.1, 0.2]], dtype=torch.float32)
    targets = torch.tensor([0, 1], dtype=torch.long)

    precision, recall, f1 = metrics_module.precision_recall_f1(logits, targets)

    assert precision == pytest.approx(0.0)
    assert recall == pytest.approx(0.0)
    assert f1 == pytest.approx(0.0)


def test_precision_recall_f1_accepts_single_logit_binary_logits() -> None:
    torch, metrics_module = _require_metrics_module()

    logits = torch.tensor([2.0, -1.0, 0.1, -0.2], dtype=torch.float32)
    targets = torch.tensor([1, 0, 1, 0], dtype=torch.long)

    precision, recall, f1 = metrics_module.precision_recall_f1(logits, targets)

    assert precision == pytest.approx(1.0)
    assert recall == pytest.approx(1.0)
    assert f1 == pytest.approx(1.0)


def test_precision_recall_f1_accepts_single_logit_probabilities() -> None:
    torch, metrics_module = _require_metrics_module()

    logits = torch.tensor([0.8, 0.6, 0.4, 0.2], dtype=torch.float32)
    targets = torch.tensor([1, 1, 0, 0], dtype=torch.long)

    precision, recall, f1 = metrics_module.precision_recall_f1(logits, targets)

    assert precision == pytest.approx(1.0)
    assert recall == pytest.approx(1.0)
    assert f1 == pytest.approx(1.0)


def test_metrics_aggregator_combines_metrics() -> None:
    torch, metrics_module = _require_metrics_module()

    logits = torch.tensor(
        [[4.0, 0.2], [0.4, 3.6], [1.4, 0.6]],
        dtype=torch.float32,
    )
    targets = torch.tensor([0, 1, 1], dtype=torch.long)

    aggregator = metrics_module.MetricsAggregator(
        metrics_module.accuracy, metrics_module.precision_recall_f1
    )
    metrics = aggregator(logits, targets)

    expected_keys = {
        "accuracy",
        "precision_recall_f1_0",
        "precision_recall_f1_1",
        "precision_recall_f1_2",
    }

    assert set(metrics) == expected_keys
    assert metrics["accuracy"] == pytest.approx(2 / 3)
    assert metrics["precision_recall_f1_0"] == pytest.approx(1.0)
    assert metrics["precision_recall_f1_1"] == pytest.approx(0.5)
    assert metrics["precision_recall_f1_2"] == pytest.approx(2 / 3)


def test_metrics_aggregator_flattens_sequence_outputs() -> None:
    torch, metrics_module = _require_metrics_module()

    logits = torch.tensor([[1.0, 0.0]], dtype=torch.float32)
    targets = torch.tensor([0], dtype=torch.long)

    def dummy_metric(_: torch.Tensor, __: torch.Tensor) -> list[float]:
        return [0.25, 0.75]

    aggregator = metrics_module.MetricsAggregator(dummy_metric)
    metrics = aggregator(logits, targets)

    assert metrics == {
        "dummy_metric_0": pytest.approx(0.25),
        "dummy_metric_1": pytest.approx(0.75),
    }
