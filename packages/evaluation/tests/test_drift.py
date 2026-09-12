from __future__ import annotations

import math

import pytest
from codex_evaluation import (
    DriftBatch,
    KullbackLeiblerDivergence,
    PopulationStabilityIndex,
)


def _legacy_scores(reference, current, epsilon=1e-8):
    ref = [(float(value) + epsilon) for value in reference]
    cur = [(float(value) + epsilon) for value in current]
    ref = [value / sum(ref) for value in ref]
    cur = [value / sum(cur) for value in cur]
    psi = sum((c - r) * math.log(c / r) for r, c in zip(ref, cur))
    kl = sum(c * math.log(c / r) for r, c in zip(ref, cur))
    return psi, kl


@pytest.mark.parametrize(
    ("reference", "current"),
    [
        ([50, 30, 20], [40, 35, 25]),
        ([1, 0, 9], [0, 2, 8]),
        ([2, 3], [2, 3]),
    ],
)
def test_drift_evaluators_have_deterministic_legacy_parity(reference, current) -> None:
    expected_psi, expected_kl = _legacy_scores(reference, current)
    batch = DriftBatch(reference, current, metadata={"run": "fixed"})

    psi = PopulationStabilityIndex(threshold=0.0).evaluate(batch)
    kl = KullbackLeiblerDivergence(threshold=0.0).evaluate(batch)

    assert psi.score == pytest.approx(expected_psi, rel=1e-15, abs=1e-15)
    assert kl.score == pytest.approx(max(0.0, expected_kl), rel=1e-15, abs=1e-15)
    assert dict(psi.metadata) == {"run": "fixed"}
    assert psi.drifted is (psi.score > psi.threshold)
    assert kl.drifted is (kl.score > kl.threshold)


@pytest.mark.parametrize(
    ("reference", "current", "message"),
    [
        ([], [], "must not be empty"),
        ([1], [1, 2], "same length"),
        ([-1, 2], [1, 2], "non-negative"),
        ([0, 0], [1, 2], "positive total"),
        ([float("nan")], [1], "finite"),
    ],
)
def test_drift_batch_rejects_invalid_distributions(reference, current, message) -> None:
    with pytest.raises(ValueError, match=message):
        DriftBatch(reference, current)


def test_drift_report_details_are_immutable() -> None:
    report = PopulationStabilityIndex().evaluate(DriftBatch([1, 1], [1, 1]))
    with pytest.raises(TypeError):
        report.details["score"] = 1.0  # type: ignore[index]
