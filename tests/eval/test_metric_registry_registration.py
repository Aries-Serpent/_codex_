"""
Test Metric Registry Registration

Test module for metric registry registration.
"""

from __future__ import annotations

import pytest

from codex_ml.metrics.registry import get_metric, metric_registry
from codex_ml.registry.base import RegistryNotFoundError


def test_custom_metric_registration_round_trip() -> None:
    """Custom metrics can be registered temporarily without leaking state."""

    def _metric(preds, targets):  # type: ignore[unused-argument]
        return 0.5

    with metric_registry.temporarily_registered({"custom_metric": _metric}):
        metric = get_metric("custom_metric")
        assert metric([1, 2, 3], [1, 2, 3]) == 0.5

    with pytest.raises(RegistryNotFoundError):
        get_metric("custom_metric")
