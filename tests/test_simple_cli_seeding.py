"""
pytest.importorskip("mlflow")
Test Simple Cli Seeding

Test module for simple cli seeding.
"""

from __future__ import annotations

import random

import pytest

from codex_ml.cli.simple_cli import _seed_everything

np = pytest.importorskip("numpy")


@pytest.mark.parametrize("seed", [7, 99])
def test_seed_everything_reproducible(seed: int) -> None:
    _seed_everything(seed)
    first_random = random.random()
    first_array = np.random.rand(3)

    _seed_everything(seed)
    second_random = random.random()
    second_array = np.random.rand(3)

    assert first_random == pytest.approx(second_random), "first_random is not valid"
    assert np.allclose(first_array, second_array)
