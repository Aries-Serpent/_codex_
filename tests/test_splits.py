"""
Test Splits

Test module for splits.
"""

import math

import pytest

from codex_ml.data.splits import SplitDistribution, assign_split, stable_fold


@pytest.mark.parametrize("example_id", ["alpha", "beta", "gamma", "delta"])
def test_stable_fold_deterministic(example_id):
    first = stable_fold(example_id)
    second = stable_fold(example_id)
    assert first == second, "first is not valid"
    assert 0 <= first < 100, "0 is not valid"


def test_assign_split_stable():
    result_a = assign_split("alpha")
    result_b = assign_split("alpha")
    assert result_a == result_b, "Result must not be empty"
    assert result_a in {"train", "val", "test"}


@pytest.mark.parametrize("count", [101, 1000])
def test_distribution_sanity(count):
    ids = [f"example-{i}" for i in range(count)]
    dist = SplitDistribution.from_ids(ids)
    assert dist.total() == count, "Count must be greater than zero"
    proportions = dist.proportions()
    assert math.isclose(sum(proportions.values()), 1.0, rel_tol=1e-9)
    # Expect approximately 80/10/10 split within a reasonable tolerance
    assert pytest.approx(0.8, rel=0.15) == proportions["train"]
    assert pytest.approx(0.1, rel=0.5) == proportions["val"]
    assert pytest.approx(0.1, rel=0.5) == proportions["test"]
