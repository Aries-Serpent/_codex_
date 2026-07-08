import pytest

pytest.importorskip("charset_normalizer")
"""
Test Ingestion Seeded Shuffle

Test module for ingestion seeded shuffle.
"""

from ingestion.utils import deterministic_shuffle


def test_seeded_shuffle_deterministic():
    data = list(range(5))
    result_seed0_a = deterministic_shuffle(data, 0)
    result_seed0_b = deterministic_shuffle(data, 0)
    result_seed1 = deterministic_shuffle(data, 1)
    assert result_seed0_a == result_seed0_b, "Result must not be empty"
    assert result_seed1 != result_seed0_a, "Result must not be empty"
